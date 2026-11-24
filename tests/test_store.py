# automated tests for ShopStore on a temporary sqlite database
import os
import sys
import tempfile
import unittest

# allow importing shop_store from the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from shop_store import ShopStore


# test suite for the ShopStore data layer
class TestShopStore(unittest.TestCase):

    # create a fresh temporary database before each test
    def setUp(self):
        # create a temporary directory and database path
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'test_coffee_shops.db')
        self.store = ShopStore(self.db_path)

    # close the database and remove the temporary directory after each test
    def tearDown(self):
        # close store connection and clean up temp folder
        self.store.close()
        self.temp_dir.cleanup()

    # test adding and reading back a coffee shop
    def test_add_and_read_shop(self):
        # add a new coffee shop
        new_id = self.store.add_shop(
            'Camel Step Roasters',
            'Riyadh',
            5,
            'V60 / Specialty',
            'Quiet Study',
            'Yes',
            'Great pour-over in Riyadh'
        )

        # verify the returned id and stored fields
        self.assertIsInstance(new_id, int)
        shop = self.store.get_shop_by_id(new_id)
        self.assertIsNotNone(shop)
        self.assertEqual(shop['name'], 'Camel Step Roasters')
        self.assertEqual(shop['region'], 'Riyadh')
        self.assertEqual(shop['rating'], 5)
        self.assertEqual(shop['open_late'], 'Yes')

        # verify get_all_shops returns one record
        all_shops = self.store.get_all_shops()
        self.assertEqual(len(all_shops), 1)

    # test updating an existing coffee shop
    def test_edit_shop(self):
        # insert a shop to edit
        shop_id = self.store.add_shop(
            'Half Million',
            'Riyadh',
            4,
            'Espresso & Dessert',
            'Drive-Thru',
            'Yes',
            'Quick iced latte'
        )

        # update the shop fields
        updated_count = self.store.update_shop(
            shop_id,
            'Half Million Flagship',
            'Jeddah',
            5,
            'Espresso & Dessert',
            'Social Hangout',
            'No',
            'Updated branch details'
        )

        # verify exactly one row was updated and values changed
        self.assertEqual(updated_count, 1)
        shop = self.store.get_shop_by_id(shop_id)
        self.assertEqual(shop['name'], 'Half Million Flagship')
        self.assertEqual(shop['region'], 'Jeddah')
        self.assertEqual(shop['rating'], 5)
        self.assertEqual(shop['seating_vibe'], 'Social Hangout')
        self.assertEqual(shop['open_late'], 'No')

    # test deleting an existing coffee shop
    def test_delete_shop(self):
        # insert two shops so we can verify only one is deleted
        first_id = self.store.add_shop(
            'Shop One', 'Riyadh', 4, 'Saudi Qahwa', 'Family Seating', 'Yes', ''
        )
        second_id = self.store.add_shop(
            'Shop Two', 'Jeddah', 5, 'V60 / Specialty', 'Quiet Study', 'No', ''
        )

        # delete only the first shop
        deleted_count = self.store.delete_shop(first_id)
        self.assertEqual(deleted_count, 1)

        # verify the first shop is gone and the second remains
        self.assertIsNone(self.store.get_shop_by_id(first_id))
        self.assertIsNotNone(self.store.get_shop_by_id(second_id))
        self.assertEqual(len(self.store.get_all_shops()), 1)

    # test unknown id handling returns None for read and 0 for edit/delete
    def test_unknown_id(self):
        # check read on non-existent id
        self.assertIsNone(self.store.get_shop_by_id(99999))

        # check update on non-existent id
        updated = self.store.update_shop(
            99999, 'Ghost Cafe', 'Riyadh', 3, 'Saudi Qahwa', 'Quiet Study', 'No', ''
        )
        self.assertEqual(updated, 0)

        # check delete on non-existent id
        deleted = self.store.delete_shop(99999)
        self.assertEqual(deleted, 0)

    # test seeding sample shops and idempotency
    def test_seed_sample_shops_idempotent(self):
        # first seed should insert 6 shops
        first_inserted = self.store.seed_sample_shops()
        self.assertEqual(first_inserted, 6)
        self.assertEqual(len(self.store.get_all_shops()), 6)

        # second seed should insert 0 shops and keep 6
        second_inserted = self.store.seed_sample_shops()
        self.assertEqual(second_inserted, 0)
        self.assertEqual(len(self.store.get_all_shops()), 6)

    # test filtering by region and minimum rating
    def test_filter_shops(self):
        # seed the 6 sample shops
        self.store.seed_sample_shops()

        # filter by region Riyadh
        riyadh_shops = self.store.filter_shops(region='Riyadh')
        self.assertEqual(len(riyadh_shops), 1)
        self.assertEqual(riyadh_shops[0]['name'], 'Elixir Bunn')

        # filter by minimum rating 5
        top_shops = self.store.filter_shops(min_rating=5)
        self.assertEqual(len(top_shops), 3)

        # filter by region Eastern Province and minimum rating 5 (no match)
        no_match = self.store.filter_shops(region='Eastern Province', min_rating=5)
        self.assertEqual(no_match, [])

    # test the Find My Spot Now query
    def test_find_spot_now(self):
        # seed the 6 sample shops
        self.store.seed_sample_shops()

        # find late-night Quiet Study V60 spots
        quiet_late = self.store.find_spot_now(
            open_late='Yes',
            seating_vibe='Quiet Study',
            coffee_style='V60 / Specialty'
        )
        self.assertEqual(len(quiet_late), 1)
        self.assertEqual(quiet_late[0]['name'], 'Elixir Bunn')

        # find all late-night spots regardless of vibe or style
        all_late = self.store.find_spot_now(open_late='Yes', seating_vibe='All', coffee_style='All')
        self.assertEqual(len(all_late), 4)

        # verify empty result when no spot matches
        none_matching = self.store.find_spot_now(
            open_late='Yes',
            seating_vibe='Drive-Thru',
            coffee_style='Saudi Qahwa'
        )
        self.assertEqual(none_matching, [])


# run the test suite when executed directly
if __name__ == '__main__':
    unittest.main(verbosity=2)
