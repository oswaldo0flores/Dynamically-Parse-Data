import csv
from exceptions import DalException
from logging_config import get_logger
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import business

FILE_PATH = 'test_form_response.csv'
logger = get_logger(__name__)


def get_data_from_csv(file_path: str) -> list:
    """
    reads csv file, returns a list of dicts where each dict represents a row with column headers as keys
    :return: a list of dictionaries.. (see above)
    """
    csv_data = []
    try:
        with open(file_path, 'r', newline='') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                csv_data.append(dict(row))
        logger.info('successfully read data from csv')
        return csv_data  # the first dict is just the headers with blank lines.
    except Exception:  # we can change this to be more specific later
        logger.error('something went wrong reading from csv')
        raise DalException


def write_to_csv(data, file_path):
    """
    write data to a csv file
    :param data: a list of lists, where each list represents a row of data
    :param file_path: the file path to write to
    :return: n/a, writes data to a file...
    """
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(data)
    logger.info(f"Data written to {file_path}")


class GoogleAuthManager:
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/drive",
              "https://www.googleapis.com/auth/forms",
              "https://www.googleapis.com/auth/documents",
              "https://www.googleapis.com/auth/spreadsheets"]

    @staticmethod
    def parse_link(url):
        """
        To parse the link to get a key.
        :return: A key
        """
        try:
            parsed_url = url.split('/')
            return parsed_url[5]
        except Exception as e:
            logger.error(f'Error parsing the URL {e}')
            raise DalException
    
    @staticmethod
    def __get_creds():
        """
        To get the credentials from a user. Validate if the user should have access to a file.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", GoogleAuthManager.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    logger.error("Error Authenticating, please click logout")
                    business.pass_error_message("Error Authenticating, please click logout & re-authenticate")
                    raise DalException
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", GoogleAuthManager.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    @staticmethod
    def get_data_from_file(url, sheet_name):
        """
        gets data from a Google Drive spreadsheet
        :param url: the url where the file is located
        :return: json containing the contents of the file
        """
        file_id = GoogleAuthManager.parse_link(url)
        try:
            result = GoogleAuthManager.__get_values(file_id, sheet_name)
            return result
        except (HttpError, DalException) as error:
            logger.error(f"An error occurred: {error}")
            raise DalException

    @staticmethod
    def append_data_to_file(values, url):
        """
        Appends data to a Google Drive sheet. Work in progress
        :param values: a list of lists, each list representing a row of data.
        :return: nothing at the moment
        """
        # 1JlobtKOn1iAPxHogaBnQFAMicaXHQ1wh-_l2kuNGs48 For exit guest output
        # 1Hpm3EFLX__DhlBoJqVbsEvdtbFvHmflEjDtW0LhhihU For New Guest output
        # file_id = url  # hard-coding this in for now.
        # I think we can come up with a better solution than copy/pasting URL, just not sure what it is yet.
        # we are not limited to just appending data, I can also make a method to create a new file
        try:
            logger.info('appending values to file')
            file_id = GoogleAuthManager.parse_link(url)
            GoogleAuthManager.__append_values(file_id, 'A1:Z20', 'USER_ENTERED', values)
        except DalException:
            raise

    @staticmethod
    def __get_values(spreadsheet_id, range_name):
        """
        Creates the batch_update the user has access to.
        Load pre-authorized user credentials from the environment.
        """
        creds = GoogleAuthManager.__get_creds()
        try:
            service = build("sheets", "v4", credentials=creds)

            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=spreadsheet_id, range=range_name)
                .execute()
            )
            rows = result.get("values", [])
            print(f"{len(rows)} rows retrieved")
            return result
        except Exception as error:
            logger.error(f"an error has occurred, {error}")
            business.pass_error_message("Error Authenticating, please click logout & re-authenticate")
            raise DalException

    @staticmethod
    def __append_values(spreadsheet_id, range_name, value_input_option, values):
        """
        Creates the batch_update the user has access to.
        Load pre-authorized user credentials from the environment.
        for guides on implementing OAuth2 for the application.
        """
        creds = GoogleAuthManager.__get_creds()
        try:
            service = build("sheets", "v4", credentials=creds)
            body = {"values": values}
            result = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
            return result
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise DalException

    @staticmethod
    def resize_columns(url):
        # Resize columns in a Google Sheet.
        spreadsheet_id = GoogleAuthManager.parse_link(url)
        creds = GoogleAuthManager.__get_creds()
        try:
            service = build("sheets", "v4", credentials=creds)

            # Get the sheet ID based on the sheet name
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', '')
            sheet_id = None
            for sheet in sheets:
                if sheet['properties']['title'] == 'Sheet1':
                    sheet_id = sheet['properties']['sheetId']
                    break

            if sheet_id is None:
                raise DalException

            requests = [
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": 81,
                        }
                    }
                }
            ]
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": requests}
            ).execute()
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise DalException