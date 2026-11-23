# flask http json server for the saudi coffee shop guide
import os
import sqlite3
from flask import Flask, jsonify, request
from shop_store import ShopStore


# path to the sqlite database file
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'coffee_shops.db')
DB_PATH = os.environ.get('COFFEE_DB_PATH', DEFAULT_DB_PATH)

# allowed values for coffee shop fields
ALLOWED_STYLES = ('Saudi Qahwa', 'V60 / Specialty', 'Espresso & Dessert')
ALLOWED_VIBES = ('Quiet Study', 'Social Hangout', 'Family Seating', 'Drive-Thru')
ALLOWED_OPEN_LATE = ('Yes', 'No')

# the flask application object
app = Flask(__name__)


# build a json error response with the given status code
def make_error(message, status_code):
    # return a json dictionary and status code
    return jsonify({
        'status': 'error',
        'error': message,
        'message': message
    }), status_code


# validate form fields for adding or editing a coffee shop
def validate_shop_form(form):
    # read and trim all text fields from the form
    name = form.get('name', '').strip()
    region = form.get('region', '').strip()
    rating_text = form.get('rating', '').strip()
    coffee_style = form.get('coffee_style', '').strip()
    seating_vibe = form.get('seating_vibe', '').strip()
    open_late = form.get('open_late', '').strip()
    notes = form.get('notes', '').strip()

    # check required name and region
    if not name:
        return None, 'Shop name is required.'
    if not region:
        return None, 'Region is required.'
    if not rating_text:
        return None, 'Rating is required.'

    # check that rating is an integer
    try:
        rating = int(rating_text)
    except ValueError:
        return None, 'Rating must be a whole number from 1 to 5.'

    # check that rating is between 1 and 5
    if rating < 1 or rating > 5:
        return None, 'Rating must be between 1 and 5.'

    # check allowed dropdown selections
    if coffee_style not in ALLOWED_STYLES:
        return None, 'Invalid coffee style.'
    if seating_vibe not in ALLOWED_VIBES:
        return None, 'Invalid seating vibe.'
    if open_late not in ALLOWED_OPEN_LATE:
        return None, 'Open late must be Yes or No.'

    # return the validated dictionary
    cleaned = {
        'name': name,
        'region': region,
        'rating': rating,
        'coffee_style': coffee_style,
        'seating_vibe': seating_vibe,
        'open_late': open_late,
        'notes': notes
    }
    return cleaned, None


# return all coffee shops or filter by optional region and min_rating
@app.route('/shops', methods=['GET'])
def get_shops():
    # read optional query parameters
    region = request.args.get('region', '').strip()
    min_rating_text = request.args.get('min_rating', '').strip()

    # validate optional minimum rating if provided
    min_rating = None
    if min_rating_text and min_rating_text != 'All':
        try:
            min_rating = int(min_rating_text)
        except ValueError:
            return make_error('Minimum rating must be a whole number from 1 to 5.', 400)
        if min_rating < 1 or min_rating > 5:
            return make_error('Minimum rating must be between 1 and 5.', 400)

    # open a fresh store connection for this request
    store = None
    try:
        store = ShopStore(DB_PATH)

        # query all shops or apply filters
        if not region and min_rating is None:
            shops = store.get_all_shops()
        else:
            shops = store.filter_shops(region=region, min_rating=min_rating)

        # return the matching shops list as a json dictionary
        return jsonify({
            'status': 'ok',
            'count': len(shops),
            'shops': shops
        }), 200
    except sqlite3.Error:
        return make_error('Database error while loading coffee shops.', 500)
    finally:
        # always close the store connection
        if store is not None:
            store.close()


# return coffee shops matching late-night status, seating vibe, and coffee style
@app.route('/shops/find_spot', methods=['GET'])
def find_spot():
    # read optional query parameters for Find My Spot Now
    open_late = request.args.get('open_late', '').strip()
    seating_vibe = request.args.get('seating_vibe', '').strip()
    coffee_style = request.args.get('coffee_style', '').strip()

    # open a fresh store connection for this request
    store = None
    try:
        store = ShopStore(DB_PATH)

        # run the Find My Spot Now query
        shops = store.find_spot_now(
            open_late=open_late,
            seating_vibe=seating_vibe,
            coffee_style=coffee_style
        )

        # return matching spots as a json dictionary
        return jsonify({
            'status': 'ok',
            'count': len(shops),
            'shops': shops
        }), 200
    except sqlite3.Error:
        return make_error('Database error while finding coffee spots.', 500)
    finally:
        # always close the store connection
        if store is not None:
            store.close()


# validate and add a new coffee shop
@app.route('/shops/add', methods=['POST'])
def add_shop():
    # validate the submitted form data
    cleaned, error_message = validate_shop_form(request.form)
    if error_message is not None:
        return make_error(error_message, 400)

    # open a fresh store connection for this request
    store = None
    try:
        store = ShopStore(DB_PATH)

        # insert the new shop and read back the saved record
        new_id = store.add_shop(
            cleaned['name'],
            cleaned['region'],
            cleaned['rating'],
            cleaned['coffee_style'],
            cleaned['seating_vibe'],
            cleaned['open_late'],
            cleaned['notes']
        )
        saved_shop = store.get_shop_by_id(new_id)

        # return the saved record with status 200
        return jsonify({
            'status': 'ok',
            'message': 'Coffee shop added.',
            'shop': saved_shop
        }), 200
    except sqlite3.Error:
        return make_error('Database error while adding coffee shop.', 500)
    finally:
        # always close the store connection
        if store is not None:
            store.close()


# validate and update an existing coffee shop by id
@app.route('/shops/edit', methods=['POST'])
def edit_shop():
    # read and validate the target shop id
    id_text = request.form.get('id', '').strip()
    if not id_text:
        return make_error('Shop ID is required.', 400)
    try:
        shop_id = int(id_text)
    except ValueError:
        return make_error('Shop ID must be a valid integer.', 400)

    # validate the updated shop fields
    cleaned, error_message = validate_shop_form(request.form)
    if error_message is not None:
        return make_error(error_message, 400)

    # open a fresh store connection for this request
    store = None
    try:
        store = ShopStore(DB_PATH)

        # update the record in sqlite
        updated_count = store.update_shop(
            shop_id,
            cleaned['name'],
            cleaned['region'],
            cleaned['rating'],
            cleaned['coffee_style'],
            cleaned['seating_vibe'],
            cleaned['open_late'],
            cleaned['notes']
        )

        # return 404 when the shop id does not exist
        if updated_count == 0:
            return make_error(f'Coffee shop with ID {shop_id} was not found.', 404)

        # read back the updated record and return status 200
        updated_shop = store.get_shop_by_id(shop_id)
        return jsonify({
            'status': 'ok',
            'message': 'Coffee shop updated.',
            'shop': updated_shop
        }), 200
    except sqlite3.Error:
        return make_error('Database error while updating coffee shop.', 500)
    finally:
        # always close the store connection
        if store is not None:
            store.close()


# validate and delete an existing coffee shop by id
@app.route('/shops/delete', methods=['POST'])
def delete_shop():
    # read and validate the target shop id
    id_text = request.form.get('id', '').strip()
    if not id_text:
        return make_error('Shop ID is required.', 400)
    try:
        shop_id = int(id_text)
    except ValueError:
        return make_error('Shop ID must be a valid integer.', 400)

    # open a fresh store connection for this request
    store = None
    try:
        store = ShopStore(DB_PATH)

        # delete the record in sqlite
        deleted_count = store.delete_shop(shop_id)

        # return 404 when the shop id does not exist
        if deleted_count == 0:
            return make_error(f'Coffee shop with ID {shop_id} was not found.', 404)

        # return confirmation with status 200
        return jsonify({
            'status': 'ok',
            'message': 'Coffee shop deleted.',
            'deleted_id': shop_id
        }), 200
    except sqlite3.Error:
        return make_error('Database error while deleting coffee shop.', 500)
    finally:
        # always close the store connection
        if store is not None:
            store.close()


# start the flask server on port 5050 when run directly
if __name__ == '__main__':
    # ensure the database table exists before starting the server
    startup_store = ShopStore(DB_PATH)
    startup_store.close()

    # run the development server on localhost port 5050
    app.run(host='127.0.0.1', port=5050, debug=False)
