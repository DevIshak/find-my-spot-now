# automated http api tests for server.py using urllib.request on port 5050
import json
import os
import socket
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen
from werkzeug.serving import make_server

# allow importing server and shop_store from the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import server
from shop_store import ShopStore


# base url for the local flask server
BASE_URL = 'http://127.0.0.1:5050'


# send a get or post request with urllib and return status code and json dict
def call_api(path, form_data=None):
    # build the full request url
    url = BASE_URL + path

    try:
        # send a GET request when no form data is given
        if form_data is None:
            reply = urlopen(url, timeout=5)
        else:
            # encode form fields and send a POST request
            body = urlencode(form_data).encode('utf-8')
            reply = urlopen(url, data=body, timeout=5)

        # decode the json response body and close the reply
        payload = json.loads(reply.read().decode('utf-8'))
        status_code = reply.status
        reply.close()
        return status_code, payload
    except HTTPError as error:
        # read and parse flask json error response and close the error stream
        error_text = error.read().decode('utf-8')
        error_code = error.code
        error.close()
        payload = json.loads(error_text)
        return error_code, payload
    except socket.timeout:
        return 0, {'status': 'error', 'error': 'Request timed out.'}
    except URLError:
        return 0, {'status': 'error', 'error': 'Could not connect to server.'}


# test suite for all Phase 2 Flask JSON routes
class TestFlaskApi(unittest.TestCase):

    # start the flask server on 127.0.0.1:5050 in a background thread
    @classmethod
    def setUpClass(cls):
        # create and start the live http server on port 5050
        cls.http_server = make_server('127.0.0.1', 5050, server.app)
        cls.server_thread = threading.Thread(target=cls.http_server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    # stop the flask server cleanly after all tests complete
    @classmethod
    def tearDownClass(cls):
        # shut down the server and wait for the thread
        cls.http_server.shutdown()
        cls.http_server.server_close()
        cls.server_thread.join(timeout=5)

    # create a fresh temporary database with 6 seeded sample shops before each test
    def setUp(self):
        # create a temporary folder and seed the test database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'test_api_shops.db')
        server.DB_PATH = self.db_path

        # seed the 6 sample saudi coffee shops
        store = ShopStore(self.db_path)
        try:
            store.seed_sample_shops()
        finally:
            store.close()

    # remove the temporary database directory after each test
    def tearDown(self):
        # clean up temporary directory
        self.temp_dir.cleanup()

    # test GET /shops returns the seeded list and supports optional filters
    def test_get_shops(self):
        # fetch all shops
        status, data = call_api('/shops')
        self.assertEqual(status, 200)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['count'], 6)
        self.assertIsInstance(data['shops'], list)
        self.assertEqual(len(data['shops']), 6)

        # fetch shops filtered by region Riyadh and min_rating 5
        query = urlencode({'region': 'Riyadh', 'min_rating': '5'})
        status, filtered = call_api('/shops?' + query)
        self.assertEqual(status, 200)
        self.assertEqual(filtered['count'], 1)
        self.assertEqual(filtered['shops'][0]['name'], 'Elixir Bunn')

    # test POST /shops/add with valid fields returns 200 and saved shop
    def test_add_shop_valid(self):
        # send a valid new coffee shop
        form = {
            'name': 'Coyard Coffee Roasters',
            'region': 'Riyadh',
            'rating': '5',
            'coffee_style': 'V60 / Specialty',
            'seating_vibe': 'Social Hangout',
            'open_late': 'Yes',
            'notes': 'Specialty pour-over and outdoor courtyard'
        }
        status, data = call_api('/shops/add', form)

        # verify status 200 and returned record
        self.assertEqual(status, 200)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['shop']['name'], 'Coyard Coffee Roasters')
        self.assertEqual(data['shop']['rating'], 5)

        # confirm total shops increased to 7
        _, all_data = call_api('/shops')
        self.assertEqual(all_data['count'], 7)

    # test POST /shops/add validation errors return 400
    def test_add_shop_validation_errors(self):
        # test missing name returns 400
        missing_name_form = {
            'name': '   ',
            'region': 'Riyadh',
            'rating': '5',
            'coffee_style': 'Saudi Qahwa',
            'seating_vibe': 'Family Seating',
            'open_late': 'Yes',
            'notes': ''
        }
        status, data = call_api('/shops/add', missing_name_form)
        self.assertEqual(status, 400)
        self.assertEqual(data['status'], 'error')

        # test non-numeric rating returns 400
        bad_rating_form = {
            'name': 'Test Cafe',
            'region': 'Jeddah',
            'rating': 'five',
            'coffee_style': 'Saudi Qahwa',
            'seating_vibe': 'Family Seating',
            'open_late': 'Yes',
            'notes': ''
        }
        status, data = call_api('/shops/add', bad_rating_form)
        self.assertEqual(status, 400)
        self.assertEqual(data['status'], 'error')

        # test rating out of 1..5 range returns 400
        out_of_range_form = {
            'name': 'Test Cafe',
            'region': 'Jeddah',
            'rating': '9',
            'coffee_style': 'Saudi Qahwa',
            'seating_vibe': 'Family Seating',
            'open_late': 'Yes',
            'notes': ''
        }
        status, data = call_api('/shops/add', out_of_range_form)
        self.assertEqual(status, 400)
        self.assertEqual(data['status'], 'error')

    # test POST /shops/edit with valid id (200) and unknown id 99999 (404)
    def test_edit_shop_valid_and_unknown_id(self):
        # edit shop id 1 with valid fields
        valid_edit = {
            'id': '1',
            'name': 'Elixir Bunn Flagship',
            'region': 'Riyadh',
            'rating': '5',
            'coffee_style': 'V60 / Specialty',
            'seating_vibe': 'Quiet Study',
            'open_late': 'No',
            'notes': 'Updated hours'
        }
        status, data = call_api('/shops/edit', valid_edit)
        self.assertEqual(status, 200)
        self.assertEqual(data['shop']['name'], 'Elixir Bunn Flagship')
        self.assertEqual(data['shop']['open_late'], 'No')

        # attempt to edit unknown id 99999 and verify 404
        unknown_edit = dict(valid_edit)
        unknown_edit['id'] = '99999'
        status, data = call_api('/shops/edit', unknown_edit)
        self.assertEqual(status, 404)
        self.assertEqual(data['status'], 'error')

    # test POST /shops/delete with valid id (200) and unknown id 99999 (404)
    def test_delete_shop_valid_and_unknown_id(self):
        # delete existing shop id 2
        status, data = call_api('/shops/delete', {'id': '2'})
        self.assertEqual(status, 200)
        self.assertEqual(data['deleted_id'], 2)

        # verify remaining shop count is 5
        _, all_data = call_api('/shops')
        self.assertEqual(all_data['count'], 5)

        # attempt to delete unknown id 99999 and verify 404
        status, data = call_api('/shops/delete', {'id': '99999'})
        self.assertEqual(status, 404)
        self.assertEqual(data['status'], 'error')

    # test GET /shops/find_spot returns matching spots and handles empty result cleanly
    def test_find_spot_endpoint(self):
        # search for late-night Social Hangout spots
        query = urlencode({
            'open_late': 'Yes',
            'seating_vibe': 'Social Hangout',
            'coffee_style': 'All'
        })
        status, data = call_api('/shops/find_spot?' + query)
        self.assertEqual(status, 200)
        self.assertEqual(data['count'], 2)
        # collect the returned shop names
        names = []
        for shop in data['shops']:
            # add each shop name to the list
            names.append(shop['name'])
        self.assertIn('Brew92', names)
        self.assertIn('Black Knight', names)

        # search for a combination with no matching spots
        empty_query = urlencode({
            'open_late': 'Yes',
            'seating_vibe': 'Drive-Thru',
            'coffee_style': 'Saudi Qahwa'
        })
        status, empty_data = call_api('/shops/find_spot?' + empty_query)
        self.assertEqual(status, 200)
        self.assertEqual(empty_data['count'], 0)
        self.assertEqual(empty_data['shops'], [])


# run the api test suite when executed directly
if __name__ == '__main__':
    unittest.main(verbosity=2)
