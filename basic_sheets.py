from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import Counter

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
INPUT_SHEET = '1ImcBQOQ86xwyA_SFtI6H9Vq3szkoUWgdtjHv7wuvBL8'
SAMPLE_RANGE_NAME = 'input!A2:E'
MAX_PALLETS = 15

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=INPUT_SHEET
,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
    #     print('weight, quantity:')
    #     for row in values:
    #         # Print columns A and E, which correspond to indices 0 and 4.
    #         print('%s, %s' % (row[0], row[1]))
        pallet_weights = [Counter() for _ in range(MAX_PALLETS)]
        pallet_counts = [Counter() for _ in range(MAX_PALLETS)]
        for row in values:
            weight = int(row[0])
            quantity = int(row[1])
            description = row[2].lower()
            source = row[3]
            pallet_num = int(row[4])
            total_weights_per_pallet = pallet_weights[pallet_num-1]
            total_counts_per_pallet = pallet_counts[pallet_num-1]
            if source == "Berkeley" or source == "berkeley":
                total_weights_per_pallet[description] += weight
                total_counts_per_pallet[description] += quantity
        counter = 0
        for c in zip(pallet_weights, pallet_counts):
            # print('weight %s, count %s', c)
            values = [
                generate_row(c)
            ]
            body = {
                'values': values
            }
            range_name = 'BerkXfer!B' + str(counter + 5)
            counter += 1
            result = service.spreadsheets().values().update(
                spreadsheetId=INPUT_SHEET, range=range_name,
                valueInputOption='RAW',body=body).execute()

RELEVANT_FIELDS = ['crt', 'lcd', 'uwed', 'unstackable uwed']
def generate_row(zipped_weight_and_counts):
    weights = zipped_weight_and_counts[0]
    counts = zipped_weight_and_counts[1]
    row = []
    for field in RELEVANT_FIELDS:
        weight = weights[field]
        count = counts[field]
        if field == 'uwed':
            weight += weights['lcd']
            count += counts['lcd']
        pair = [weight, count] if field in weights else [0, 0]
        row.extend(pair)
    print(row)
    return row

if __name__ == '__main__':
    main()