# standalone database setup and sample seeding script
import os
from shop_store import ShopStore


# path to the sqlite database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'coffee_shops.db')


# create the table and seed sample shops if empty
def setup_database(db_path=DB_PATH):
    # open the shop store
    store = ShopStore(db_path)

    try:
        # seed the 6 sample saudi coffee shops only if the table is empty
        inserted = store.seed_sample_shops()
        total = len(store.get_all_shops())

        # print the setup summary
        if inserted > 0:
            print(f'Database ready: seeded {inserted} sample coffee shops (total: {total}).')
        else:
            print(f'Database ready: existing records preserved (total: {total}).')
    finally:
        # always close the database connection
        store.close()


# run setup when executed directly
if __name__ == '__main__':
    setup_database()
