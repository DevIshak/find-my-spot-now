# sqlite3 data access module for saudi coffee shops
import sqlite3


# default saudi coffee shop records for initial seeding
SAMPLE_SHOPS = [
    (
        'Elixir Bunn',
        'Riyadh',
        5,
        'V60 / Specialty',
        'Quiet Study',
        'Yes',
        'Single-origin pour-over, calm seating for studying'
    ),
    (
        'Brew92',
        'Jeddah',
        5,
        'V60 / Specialty',
        'Social Hangout',
        'Yes',
        'Specialty roastery with lively late-night vibe'
    ),
    (
        'Kiffa',
        'Madinah',
        5,
        'Saudi Qahwa',
        'Family Seating',
        'Yes',
        'Traditional cardamom qahwa and Ajwa dates'
    ),
    (
        'Black Knight',
        'Eastern Province',
        4,
        'Espresso & Dessert',
        'Social Hangout',
        'Yes',
        'Popular Spanish latte and cheesecake in Khobar'
    ),
    (
        'Minzal',
        'AlUla',
        4,
        'Saudi Qahwa',
        'Family Seating',
        'No',
        'Scenic sunset seating with local roast'
    ),
    (
        'Veranda',
        'Asir',
        4,
        'Espresso & Dessert',
        'Drive-Thru',
        'No',
        'Quick morning espresso stop in cool weather'
    ),
]


# data access class for the coffee_shops table
class ShopStore:

    # open the database connection and create the table
    def __init__(self, db_path):
        # connect to the sqlite file and enable row access by column name
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        # ensure the table exists
        self.create_table()

    # create the coffee_shops table if it does not exist
    def create_table(self):
        # run the table creation statement inside a transaction
        with self.conn:
            self.conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS coffee_shops (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    region TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    coffee_style TEXT NOT NULL,
                    seating_vibe TEXT NOT NULL,
                    open_late TEXT NOT NULL,
                    notes TEXT DEFAULT ''
                )
                '''
            )

    # convert a sqlite row object into a plain dictionary
    def _row_to_dict(self, row):
        # build and return the dictionary
        return {
            'id': row['id'],
            'name': row['name'],
            'region': row['region'],
            'rating': row['rating'],
            'coffee_style': row['coffee_style'],
            'seating_vibe': row['seating_vibe'],
            'open_late': row['open_late'],
            'notes': row['notes'],
        }

    # convert a list of sqlite rows into a list of dictionaries
    def _rows_to_list(self, rows):
        # loop over rows and collect dictionaries
        result = []
        for row in rows:
            # append the converted dictionary
            result.append(self._row_to_dict(row))
        return result

    # insert a new coffee shop and return its generated id
    def add_shop(self, name, region, rating, coffee_style, seating_vibe, open_late, notes=''):
        # insert the row inside a transaction
        with self.conn:
            cursor = self.conn.execute(
                '''
                INSERT INTO coffee_shops (
                    name, region, rating, coffee_style, seating_vibe, open_late, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (name, region, int(rating), coffee_style, seating_vibe, open_late, notes)
            )
            # return the new primary key id
            return cursor.lastrowid

    # fetch all coffee shops ordered by id
    def get_all_shops(self):
        # query all rows from the table
        cursor = self.conn.execute(
            '''
            SELECT id, name, region, rating, coffee_style, seating_vibe, open_late, notes
            FROM coffee_shops
            ORDER BY id ASC
            '''
        )
        rows = cursor.fetchall()

        # convert rows to dictionaries and return
        return self._rows_to_list(rows)

    # fetch one coffee shop by id or return None if not found
    def get_shop_by_id(self, shop_id):
        # query the matching row by id
        cursor = self.conn.execute(
            '''
            SELECT id, name, region, rating, coffee_style, seating_vibe, open_late, notes
            FROM coffee_shops
            WHERE id = ?
            ''',
            (shop_id,)
        )
        row = cursor.fetchone()

        # return None when no row matches
        if row is None:
            return None

        # convert the row to a dictionary
        return self._row_to_dict(row)

    # update an existing coffee shop and return the affected row count
    def update_shop(self, shop_id, name, region, rating, coffee_style, seating_vibe, open_late, notes=''):
        # run the update inside a transaction
        with self.conn:
            cursor = self.conn.execute(
                '''
                UPDATE coffee_shops
                SET name = ?,
                    region = ?,
                    rating = ?,
                    coffee_style = ?,
                    seating_vibe = ?,
                    open_late = ?,
                    notes = ?
                WHERE id = ?
                ''',
                (name, region, int(rating), coffee_style, seating_vibe, open_late, notes, shop_id)
            )
            # return 1 if updated or 0 if id was not found
            return cursor.rowcount

    # delete a coffee shop by id and return the affected row count
    def delete_shop(self, shop_id):
        # run the delete inside a transaction
        with self.conn:
            cursor = self.conn.execute(
                '''
                DELETE FROM coffee_shops
                WHERE id = ?
                ''',
                (shop_id,)
            )
            # return 1 if deleted or 0 if id was not found
            return cursor.rowcount

    # filter coffee shops by optional region and minimum rating
    def filter_shops(self, region='', min_rating=None):
        # normalize empty or All region values
        region_val = ''
        if region and region != 'All':
            region_val = region

        # normalize empty or None minimum rating values
        rating_val = None
        if min_rating is not None and min_rating != '' and min_rating != 'All':
            rating_val = int(min_rating)

        # query matching shops with parameterized placeholders
        cursor = self.conn.execute(
            '''
            SELECT id, name, region, rating, coffee_style, seating_vibe, open_late, notes
            FROM coffee_shops
            WHERE (? = '' OR region = ?)
              AND (? IS NULL OR rating >= ?)
            ORDER BY id ASC
            ''',
            (region_val, region_val, rating_val, rating_val)
        )
        rows = cursor.fetchall()

        # convert rows to dictionaries and return
        return self._rows_to_list(rows)

    # find matching spots for the Find My Spot Now feature
    def find_spot_now(self, open_late='', seating_vibe='', coffee_style=''):
        # normalize optional filter values
        late_val = ''
        if open_late and open_late not in ('All', 'Any'):
            late_val = open_late

        vibe_val = ''
        if seating_vibe and seating_vibe not in ('All', 'Any'):
            vibe_val = seating_vibe

        style_val = ''
        if coffee_style and coffee_style not in ('All', 'Any'):
            style_val = coffee_style

        # query matching spots sorted by highest rating first
        cursor = self.conn.execute(
            '''
            SELECT id, name, region, rating, coffee_style, seating_vibe, open_late, notes
            FROM coffee_shops
            WHERE (? = '' OR open_late = ?)
              AND (? = '' OR seating_vibe = ?)
              AND (? = '' OR coffee_style = ?)
            ORDER BY rating DESC, id ASC
            ''',
            (late_val, late_val, vibe_val, vibe_val, style_val, style_val)
        )
        rows = cursor.fetchall()

        # convert rows to dictionaries and return
        return self._rows_to_list(rows)

    # insert the 6 sample Saudi coffee shops only when the table is empty
    def seed_sample_shops(self):
        # check the current number of rows
        cursor = self.conn.execute('SELECT COUNT(*) FROM coffee_shops')
        count = cursor.fetchone()[0]

        # skip seeding if any records already exist
        if count > 0:
            return 0

        # insert all sample shops inside a transaction
        with self.conn:
            for shop in SAMPLE_SHOPS:
                # insert one sample shop record
                self.conn.execute(
                    '''
                    INSERT INTO coffee_shops (
                        name, region, rating, coffee_style, seating_vibe, open_late, notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    shop
                )

        # return the number of inserted sample rows
        return len(SAMPLE_SHOPS)

    # close the database connection
    def close(self):
        # close the sqlite connection cleanly
        self.conn.close()
