# terminal script that writes a text report of all coffee shops
import json
import socket
import threading
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


# server address and report file name
SHOPS_URL = 'http://127.0.0.1:5050/shops'
REPORT_PATH = 'coffee_shops_report.txt'


# fetch all shops from the server, returns (shops, error_message)
def fetch_shops():
    try:
        # send the GET request
        with urlopen(SHOPS_URL, timeout=5) as reply:
            data = json.loads(reply.read().decode('utf-8'))
        return data['shops'], None
    except HTTPError as error:
        # read the json error message sent by flask
        error_text = error.read().decode('utf-8')
        error.close()
        try:
            message = json.loads(error_text).get('error', 'Server error.')
        except ValueError:
            message = 'Server error.'
        return None, 'Server error ' + str(error.code) + ': ' + message
    except socket.timeout:
        return None, 'The server took too long to answer.'
    except URLError:
        return None, 'Cannot connect to the server. Start server.py first.'


# write the report file, runs inside the worker thread
def write_report(shops, output_path, result):
    # build the report lines
    lines = []
    lines.append('SAUDI COFFEE SHOP GUIDE - REPORT')
    lines.append('=' * 40)
    for shop in shops:
        # add one block per shop
        lines.append('')
        lines.append('Name:         ' + shop['name'])
        lines.append('Region:       ' + shop['region'])
        lines.append('Rating:       ' + str(shop['rating']) + '/5')
        lines.append('Coffee Style: ' + shop['coffee_style'])
        lines.append('Seating Vibe: ' + shop['seating_vibe'])
        lines.append('Open Late:    ' + shop['open_late'])
        lines.append('Notes:        ' + shop['notes'])
    lines.append('')
    lines.append('=' * 40)
    lines.append('Total coffee shops: ' + str(len(shops)))

    try:
        # write the lines to the file
        with open(output_path, 'w', encoding='utf-8') as report_file:
            report_file.write('\n'.join(lines) + '\n')
        result['ok'] = True
    except OSError as error:
        # remember the error for the main thread
        result['ok'] = False
        result['error'] = str(error)


# run the whole report job
def main(output_path=REPORT_PATH):
    # fetch the shops
    shops, error_message = fetch_shops()
    if error_message is not None:
        print('Report FAILED: ' + error_message)
        return

    # start one thread to write the file
    result = {'ok': False, 'error': ''}
    writer = threading.Thread(target=write_report, args=(shops, output_path, result))
    writer.start()

    # wait for the thread to finish
    writer.join()

    # print the final status
    if result['ok']:
        print('Report SUCCESS: wrote ' + str(len(shops)) + ' shops to ' + output_path)
    else:
        print('Report FAILED: could not write file (' + result['error'] + ')')


# run when executed directly
if __name__ == '__main__':
    main()
