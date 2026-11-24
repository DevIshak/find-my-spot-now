# tkinter desktop app for the saudi coffee shop guide
import json
import socket
import tkinter as tk
from tkinter import messagebox, ttk
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


# base address of the flask server
BASE_URL = 'http://127.0.0.1:5050'

# choices for the dropdown lists
REGIONS = ['Riyadh', 'Jeddah', 'Madinah', 'Eastern Province', 'AlUla', 'Asir']
STYLES = ['Saudi Qahwa', 'V60 / Specialty', 'Espresso & Dessert']
VIBES = ['Quiet Study', 'Social Hangout', 'Family Seating', 'Drive-Thru']
OPEN_LATE_CHOICES = ['Yes', 'No']
MIN_RATING_CHOICES = ['All', '1', '2', '3', '4', '5']

# theme colors and font
CREAM = '#FAF6F0'
CREAM_LIGHT = '#FFFFFF'
CREAM_ROW = '#F3EBDD'
ESPRESSO = '#4A2C2A'
ESPRESSO_LIGHT = '#6B4440'
FONT_NAME = 'Segoe UI'


# send one request to the server and return (data, error_message)
def send_request(path, form_data=None):
    # build the full url
    url = BASE_URL + path

    try:
        # send a GET request when there is no form data
        if form_data is None:
            with urlopen(url, timeout=5) as reply:
                data = json.loads(reply.read().decode('utf-8'))
        else:
            # send a POST request with the encoded form fields
            body = urlencode(form_data).encode('utf-8')
            with urlopen(url, data=body, timeout=5) as reply:
                data = json.loads(reply.read().decode('utf-8'))
        return data, None
    except HTTPError as error:
        # read the json error message sent by flask
        error_text = error.read().decode('utf-8')
        error.close()
        try:
            error_data = json.loads(error_text)
            message = error_data.get('error', 'Server error.')
        except ValueError:
            message = 'Server error.'
        return None, 'Server error ' + str(error.code) + ': ' + message
    except socket.timeout:
        return None, 'The server took too long to answer. Please try again.'
    except URLError:
        return None, 'Cannot connect to the server. Start server.py and try again.'


# main window of the application
class CoffeeGuideWindow(tk.Tk):

    # build the window and load the first list
    def __init__(self):
        # create the window
        super().__init__()
        self.title('Saudi Coffee Shop Guide')

        # id of the shop selected in the table
        self.selected_shop_id = None

        # colors and fonts first, then the widgets
        self.apply_theme()

        # build every section of the window
        self.build_banner()
        self.build_form_panel()
        self.build_button_panel()
        self.build_filter_bar()
        self.build_find_spot_panel()
        self.build_table()
        self.build_status_label()

        # load the shops from the server
        self.refresh_shops()

    # set the cream and espresso colors with ttk styles
    def apply_theme(self):
        # start from the clam theme and color the window
        style = ttk.Style()
        style.theme_use('clam')
        self.configure(background=CREAM)

        # frames and labels
        style.configure('TFrame', background=CREAM)
        style.configure('TLabel', background=CREAM, foreground=ESPRESSO, font=(FONT_NAME, 10))
        style.configure('TLabelframe', background=CREAM, bordercolor=ESPRESSO_LIGHT)
        style.configure(
            'TLabelframe.Label', background=CREAM, foreground=ESPRESSO, font=(FONT_NAME, 10, 'bold')
        )

        # banner at the top
        style.configure(
            'Banner.TLabel', background=ESPRESSO, foreground=CREAM, font=(FONT_NAME, 13, 'bold')
        )

        # normal buttons
        style.configure(
            'TButton', background=CREAM_ROW, foreground=ESPRESSO, font=(FONT_NAME, 10), padding=4
        )
        style.map('TButton', background=[('active', '#E6D9C3')])

        # accent buttons for Add Shop and Find My Spot Now
        style.configure(
            'Accent.TButton', background=ESPRESSO, foreground=CREAM, font=(FONT_NAME, 10, 'bold'), padding=4
        )
        style.map('Accent.TButton', background=[('active', ESPRESSO_LIGHT)])

        # entry boxes and dropdowns
        style.configure('TEntry', fieldbackground=CREAM_LIGHT, foreground=ESPRESSO)
        style.configure('TCombobox', fieldbackground=CREAM_LIGHT, foreground=ESPRESSO)

        # table and its headings
        style.configure(
            'Treeview', background=CREAM_LIGHT, fieldbackground=CREAM_LIGHT,
            foreground=ESPRESSO, font=(FONT_NAME, 10), rowheight=24
        )
        style.map('Treeview', background=[('selected', ESPRESSO)], foreground=[('selected', CREAM)])
        style.configure(
            'Treeview.Heading', background=ESPRESSO, foreground=CREAM, font=(FONT_NAME, 10, 'bold')
        )
        style.map('Treeview.Heading', background=[('active', ESPRESSO_LIGHT)])

    # build the compact title banner
    def build_banner(self):
        # one label across the top of the window
        self.banner_label = ttk.Label(
            self, text='Saudi Coffee Shop Guide \u2014 Late-Night & Vibe Finder',
            style='Banner.TLabel', anchor='center'
        )
        self.banner_label.grid(row=0, column=0, sticky='ew', ipady=6)

    # build the form panel
    def build_form_panel(self):
        # the frame that holds the form
        form_frame = ttk.LabelFrame(self, text='Coffee Shop Details')
        form_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        # name field
        ttk.Label(form_frame, text='Name:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # region dropdown
        ttk.Label(form_frame, text='Region:').grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.region_combo = ttk.Combobox(form_frame, values=REGIONS, state='readonly', width=20)
        self.region_combo.grid(row=0, column=3, padx=5, pady=5)

        # rating field
        ttk.Label(form_frame, text='Rating (1-5):').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.rating_entry = ttk.Entry(form_frame, width=30)
        self.rating_entry.grid(row=1, column=1, padx=5, pady=5)

        # coffee style dropdown
        ttk.Label(form_frame, text='Coffee Style:').grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.style_combo = ttk.Combobox(form_frame, values=STYLES, state='readonly', width=20)
        self.style_combo.grid(row=1, column=3, padx=5, pady=5)

        # seating vibe dropdown
        ttk.Label(form_frame, text='Seating Vibe:').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.vibe_combo = ttk.Combobox(form_frame, values=VIBES, state='readonly', width=27)
        self.vibe_combo.grid(row=2, column=1, padx=5, pady=5)

        # open late dropdown
        ttk.Label(form_frame, text='Open Late:').grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.open_late_combo = ttk.Combobox(form_frame, values=OPEN_LATE_CHOICES, state='readonly', width=20)
        self.open_late_combo.grid(row=2, column=3, padx=5, pady=5)

        # notes field
        ttk.Label(form_frame, text='Notes:').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.notes_entry = ttk.Entry(form_frame, width=80)
        self.notes_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky='w')

    # build the action buttons
    def build_button_panel(self):
        # the frame that holds the buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        # add button
        self.add_button = ttk.Button(
            button_frame, text='Add Shop', style='Accent.TButton', command=self.add_shop
        )
        self.add_button.grid(row=0, column=0, padx=5, pady=5)

        # edit button
        self.edit_button = ttk.Button(button_frame, text='Update Selected', command=self.edit_shop)
        self.edit_button.grid(row=0, column=1, padx=5, pady=5)

        # delete button
        self.delete_button = ttk.Button(button_frame, text='Delete Selected', command=self.delete_shop)
        self.delete_button.grid(row=0, column=2, padx=5, pady=5)

        # clear button
        self.clear_button = ttk.Button(button_frame, text='Clear Form', command=self.clear_form)
        self.clear_button.grid(row=0, column=3, padx=5, pady=5)

        # refresh button
        self.refresh_button = ttk.Button(button_frame, text='Refresh List', command=self.refresh_shops)
        self.refresh_button.grid(row=0, column=4, padx=5, pady=5)

    # build the filter bar
    def build_filter_bar(self):
        # the frame that holds the filters
        filter_frame = ttk.LabelFrame(self, text='Filter')
        filter_frame.grid(row=3, column=0, padx=10, pady=5, sticky='ew')

        # region filter
        ttk.Label(filter_frame, text='Region:').grid(row=0, column=0, padx=5, pady=5)
        self.filter_region_combo = ttk.Combobox(
            filter_frame, values=['All'] + REGIONS, state='readonly', width=18
        )
        self.filter_region_combo.set('All')
        self.filter_region_combo.grid(row=0, column=1, padx=5, pady=5)

        # minimum rating filter
        ttk.Label(filter_frame, text='Min Rating:').grid(row=0, column=2, padx=5, pady=5)
        self.filter_rating_combo = ttk.Combobox(
            filter_frame, values=MIN_RATING_CHOICES, state='readonly', width=8
        )
        self.filter_rating_combo.set('All')
        self.filter_rating_combo.grid(row=0, column=3, padx=5, pady=5)

        # apply filter button
        self.apply_filter_button = ttk.Button(filter_frame, text='Apply Filter', command=self.refresh_shops)
        self.apply_filter_button.grid(row=0, column=4, padx=5, pady=5)

        # show all button
        self.show_all_button = ttk.Button(filter_frame, text='Show All', command=self.show_all)
        self.show_all_button.grid(row=0, column=5, padx=5, pady=5)

    # build the Find My Spot Now panel
    def build_find_spot_panel(self):
        # the frame that holds the panel
        spot_frame = ttk.LabelFrame(self, text='Find My Spot Now')
        spot_frame.grid(row=4, column=0, padx=10, pady=5, sticky='ew')

        # late night dropdown
        ttk.Label(spot_frame, text='Late Night:').grid(row=0, column=0, padx=5, pady=5)
        self.spot_late_combo = ttk.Combobox(
            spot_frame, values=['Any', 'Yes'], state='readonly', width=8
        )
        self.spot_late_combo.set('Any')
        self.spot_late_combo.grid(row=0, column=1, padx=5, pady=5)

        # vibe dropdown
        ttk.Label(spot_frame, text='Vibe:').grid(row=0, column=2, padx=5, pady=5)
        self.spot_vibe_combo = ttk.Combobox(
            spot_frame, values=['Any'] + VIBES, state='readonly', width=16
        )
        self.spot_vibe_combo.set('Any')
        self.spot_vibe_combo.grid(row=0, column=3, padx=5, pady=5)

        # coffee style dropdown
        ttk.Label(spot_frame, text='Coffee Style:').grid(row=0, column=4, padx=5, pady=5)
        self.spot_style_combo = ttk.Combobox(
            spot_frame, values=['Any'] + STYLES, state='readonly', width=18
        )
        self.spot_style_combo.set('Any')
        self.spot_style_combo.grid(row=0, column=5, padx=5, pady=5)

        # find spot button
        self.find_spot_button = ttk.Button(
            spot_frame, text='Find My Spot Now', style='Accent.TButton', command=self.find_spot_now
        )
        self.find_spot_button.grid(row=0, column=6, padx=5, pady=5)

        # reset button
        self.reset_spot_button = ttk.Button(spot_frame, text='Reset', command=self.reset_spot)
        self.reset_spot_button.grid(row=0, column=7, padx=5, pady=5)

    # build the table with a scrollbar
    def build_table(self):
        # the frame that holds the table
        table_frame = ttk.Frame(self)
        table_frame.grid(row=5, column=0, padx=10, pady=5, sticky='nsew')
        self.rowconfigure(5, weight=1)
        self.columnconfigure(0, weight=1)

        # the table columns
        columns = ('id', 'name', 'region', 'rating', 'coffee_style', 'seating_vibe', 'open_late', 'notes')
        self.shops_table = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)

        # column headings and widths
        headings = ['ID', 'Name', 'Region', 'Rating', 'Coffee Style', 'Seating Vibe', 'Open Late', 'Notes']
        widths = [40, 180, 110, 60, 120, 110, 70, 250]
        for index in range(len(columns)):
            # set one column
            self.shops_table.heading(columns[index], text=headings[index])
            self.shops_table.column(columns[index], width=widths[index])

        # scrollbar for the table
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.shops_table.yview)
        self.shops_table.configure(yscrollcommand=scrollbar.set)

        # place the table and scrollbar
        self.shops_table.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # alternating row colors
        self.shops_table.tag_configure('even_row', background=CREAM_LIGHT)
        self.shops_table.tag_configure('odd_row', background=CREAM_ROW)

        # fill the form when a row is selected
        self.shops_table.bind('<<TreeviewSelect>>', self.on_row_selected)

    # build the status label
    def build_status_label(self):
        # label that shows success and error messages
        self.status_label = ttk.Label(self, text='Ready.')
        self.status_label.grid(row=6, column=0, padx=10, pady=10, sticky='w')

    # show a message in the status label
    def show_status(self, message, is_error=False):
        # choose the color
        color = 'green'
        if is_error:
            color = 'red'

        # update the label
        self.status_label.config(text=message, foreground=color)

    # read the form fields into a dictionary
    def read_form(self):
        # read every field
        form_data = {
            'name': self.name_entry.get().strip(),
            'region': self.region_combo.get().strip(),
            'rating': self.rating_entry.get().strip(),
            'coffee_style': self.style_combo.get().strip(),
            'seating_vibe': self.vibe_combo.get().strip(),
            'open_late': self.open_late_combo.get().strip(),
            'notes': self.notes_entry.get().strip(),
        }
        return form_data

    # empty the form and forget the selected shop
    def clear_form(self):
        # clear the text fields
        self.name_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)

        # clear the dropdowns
        self.region_combo.set('')
        self.style_combo.set('')
        self.vibe_combo.set('')
        self.open_late_combo.set('')

        # forget the selection
        self.selected_shop_id = None
        self.shops_table.selection_remove(self.shops_table.selection())

    # reset the filters and show every shop
    def show_all(self):
        # reset the filter dropdowns
        self.filter_region_combo.set('All')
        self.filter_rating_combo.set('All')

        # reload the list
        self.refresh_shops()

    # load the shops from the server into the table
    def refresh_shops(self):
        # build the query string from the filters
        values = {}
        region = self.filter_region_combo.get()
        min_rating = self.filter_rating_combo.get()
        if region and region != 'All':
            values['region'] = region
        if min_rating and min_rating != 'All':
            values['min_rating'] = min_rating
        path = '/shops'
        if values:
            path = path + '?' + urlencode(values)

        # ask the server for the shops
        data, error_message = send_request(path)
        if error_message is not None:
            self.show_status(error_message, True)
            return

        # show the shops in the table
        self.fill_table(data['shops'])

        # show the result
        if len(data['shops']) == 0:
            self.show_status('No coffee shops found.')
        else:
            self.show_status('Loaded ' + str(len(data['shops'])) + ' coffee shop(s).')

    # put a list of shops into the table
    def fill_table(self, shops):
        # remove the old rows
        for row_id in self.shops_table.get_children():
            # delete one old row
            self.shops_table.delete(row_id)

        # add the new rows
        row_number = 0
        for shop in shops:
            # pick the even or odd row color tag
            row_tag = 'odd_row'
            if row_number % 2 == 0:
                row_tag = 'even_row'
            row_number = row_number + 1

            # insert one shop as a table row
            self.shops_table.insert('', tk.END, iid=str(shop['id']), tags=(row_tag,), values=(
                shop['id'],
                shop['name'],
                shop['region'],
                shop['rating'],
                shop['coffee_style'],
                shop['seating_vibe'],
                shop['open_late'],
                shop['notes'],
            ))

        # the selected row no longer exists
        self.selected_shop_id = None

    # find matching spots with the extra feature
    def find_spot_now(self):
        # build the query string from the panel
        values = {
            'open_late': self.spot_late_combo.get(),
            'seating_vibe': self.spot_vibe_combo.get(),
            'coffee_style': self.spot_style_combo.get(),
        }
        path = '/shops/find_spot?' + urlencode(values)

        # ask the server for matching spots
        data, error_message = send_request(path)
        if error_message is not None:
            self.show_status(error_message, True)
            return

        # show the matches in the table
        self.fill_table(data['shops'])

        # show the count
        if data['count'] == 0:
            self.show_status('No matching spots found. Try different choices.')
        else:
            self.show_status('Found ' + str(data['count']) + ' matching spot(s).')

    # reset the panel and show every shop
    def reset_spot(self):
        # reset the panel dropdowns
        self.spot_late_combo.set('Any')
        self.spot_vibe_combo.set('Any')
        self.spot_style_combo.set('Any')

        # reset the filters and reload the list
        self.show_all()

    # fill the form from the selected row
    def on_row_selected(self, event):
        # get the selected row
        selected = self.shops_table.selection()
        if not selected:
            return

        # read the row values
        values = self.shops_table.item(selected[0], 'values')
        self.selected_shop_id = int(values[0])

        # fill the text fields
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])
        self.rating_entry.delete(0, tk.END)
        self.rating_entry.insert(0, values[3])
        self.notes_entry.delete(0, tk.END)
        self.notes_entry.insert(0, values[7])

        # fill the dropdowns
        self.region_combo.set(values[2])
        self.style_combo.set(values[4])
        self.vibe_combo.set(values[5])
        self.open_late_combo.set(values[6])

    # show an error and reload the list if the shop no longer exists
    def show_error_and_reload(self, error_message, title):
        # show the error to the user
        messagebox.showerror(title, error_message)

        # remove the stale row when the server says 404 not found
        if error_message.startswith('Server error 404'):
            self.clear_form()
            self.refresh_shops()

        # keep the error visible in the status label
        self.show_status(error_message, True)

    # add a new shop
    def add_shop(self):
        # send the form to the server
        form_data = self.read_form()
        data, error_message = send_request('/shops/add', form_data)
        if error_message is not None:
            self.show_status(error_message, True)
            messagebox.showerror('Add Failed', error_message)
            return

        # refresh the list and report success
        self.clear_form()
        self.refresh_shops()
        self.show_status('Added: ' + data['shop']['name'])

    # update the selected shop
    def edit_shop(self):
        # a row must be selected first
        if self.selected_shop_id is None:
            self.show_status('Please select a coffee shop first.', True)
            messagebox.showwarning('No Selection', 'Please select a coffee shop first.')
            return

        # send the form and the id to the server
        form_data = self.read_form()
        form_data['id'] = str(self.selected_shop_id)
        data, error_message = send_request('/shops/edit', form_data)
        if error_message is not None:
            self.show_error_and_reload(error_message, 'Update Failed')
            return

        # refresh the list and report success
        self.clear_form()
        self.refresh_shops()
        self.show_status('Updated: ' + data['shop']['name'])

    # delete the selected shop after asking
    def delete_shop(self):
        # a row must be selected first
        if self.selected_shop_id is None:
            self.show_status('Please select a coffee shop first.', True)
            messagebox.showwarning('No Selection', 'Please select a coffee shop first.')
            return

        # a table row must still be selected
        selected_row = self.shops_table.selection()
        if not selected_row:
            self.show_status('Please select a coffee shop first.', True)
            messagebox.showwarning('No Selection', 'Please select a coffee shop first.')
            return

        # read the shop name from the table row, not the typed box
        shop_name = self.shops_table.item(selected_row[0], 'values')[1]

        # ask the user to confirm
        answer = messagebox.askyesno('Confirm Delete', 'Delete "' + shop_name + '"?')
        if not answer:
            return

        # send the id to the server
        form_data = {'id': str(self.selected_shop_id)}
        data, error_message = send_request('/shops/delete', form_data)
        if error_message is not None:
            self.show_error_and_reload(error_message, 'Delete Failed')
            return

        # refresh the list and report success
        self.clear_form()
        self.refresh_shops()
        self.show_status('Deleted: ' + shop_name)


# start the app when run directly
if __name__ == '__main__':
    window = CoffeeGuideWindow()
    window.mainloop()
