import calendar
import os
import pandas
from dal import GoogleAuthManager
from datetime import datetime
from exceptions import BusinessLogicException, DalException
from logging_config import get_logger
from models import NewGuestList, ExitGuestList, ReturnGuestList
import gui


logger = get_logger(__name__)
COLUMNS = ['first name', 'last name', 'date of birth', 'last four digits of my ssn', 'what is your phone number?',
           'what is your email address?', 'score', 'optional photo release:']
DIFFERENT_VARIATIONS_OF_NA = ['N/A', 'N/a', 'n/A', 'n/a', 'NA', 'Na', 'nA', 'na']


# -> THIS IS THE CURRENT METHOD TO CALL FROM OTHER LAYERS FOR THE DATA <-
def generate_new_guest_list_class(url: str, sheet_names):
    """
    mostly a passthrough function, calls on the new_guest_factory function from the models directory
    :param url: the url (google sheets) where the data is being stored
    :return: a NewGuestList object
    """
    try:
        new_guests = NewGuestList.new_guest_factory(url, sheet_names)
        return new_guests
    except BusinessLogicException:
        raise BusinessLogicException
    

def generate_exit_guest_list(url: str, sheet_names):
    """
    mostly a passthrough function, calls on the new_guest_factory function from the models directory
    :param url: the url (google sheets) where the data is being stored
    :return: a ExitGuestList object
    """
    try:
        exit_guests = ExitGuestList.exit_guest_factory(url, sheet_names)
        return exit_guests
    except BusinessLogicException:
        raise BusinessLogicException
    

def generate_return_guest_list(url, sheet_names):
    """
    mostly a passthrough function, calls on the new_guest_factory function from the models directory
    :param url: the url (google sheets) where the data is being stored
    :return: a ReturnGuestList object
    """
    try:
        return_guest = ReturnGuestList.return_guest_factory(url, sheet_names)
        return return_guest
    except BusinessLogicException:
        raise BusinessLogicException


def sort_guests_by_date(guest_list, start_date, end_date):
    """
    sorts a object by start date and end date
    :param guest_list: a object to sort
    :param start_date: the first date the user selected
    :param end_date: the second date the user selected
    :return: a list of objects that fit the criteria
    """
    guest_list['Timestamp'] = pandas.to_datetime(guest_list['Timestamp'])
    guest_len_list = len(guest_list)
    for index in range(0, guest_len_list):
        if not (start_date <= guest_list.loc[index, 'Timestamp'].date() <= end_date):
            guest_list = guest_list.drop([index])
    guest_list = guest_list.reset_index()
    return guest_list


def return_entries_for_current_month(guest_list) -> []:
    """
    takes a list object, returns new guests whose timestamp matches the current month
    :param new_guest_list: a object to sort
    :return: a list of objects that match the criteria stated above
    """
    guest_list['Timestamp'] = pandas.to_datetime(guest_list['Timestamp'])
    guest_len_list = len(guest_list)
    current_month_year = return_current_month_year()
    for index in range(0, guest_len_list):
        guest_date = guest_list.loc[index, 'Timestamp'].date()
        guest_date = (guest_date.month, guest_date.year)
        if not (guest_date == current_month_year):
            guest_list = guest_list.drop([index])
    guest_list = guest_list.reset_index()
    return guest_list


def return_entries_for_current_year(guest_list):
    """
    takes a list object, returns new guests whose timestamp matches the current year
    :param guest_list: a object to sort
    :return: a list of objects that match the criteria stated above
    """
    guest_list['Timestamp'] = pandas.to_datetime(guest_list['Timestamp'])
    guest_len_list = len(guest_list)
    current_month_year = return_current_month_year()[1]
    for index in range(0, guest_len_list):
        guest_date = guest_list.loc[index, 'Timestamp'].date()
        guest_date = guest_date.year
        if not (guest_date == current_month_year):
            guest_list = guest_list.drop([index])
    guest_list = guest_list.reset_index()
    return guest_list


def return_current_month_year() -> (int, int):
    """
    retrieves the current month & year as a tuple of ints (month, year)
    :return: the current month & year
    """
    now = datetime.now()
    return (now.month, now.year)


def timestamp_parser(timestamp: str):
    """
    takes a timestamp from the google sheet, returns a tuple (month, year) for each timestamp
    :param timestamp: timestamp from the google sheet
    :return: a tuple (month, year) for each timestamp
    """
    tokens = timestamp.split(" ")  # separates the date & time
    date = tokens[0].split('/')
    return datetime(int(date[2]), int(date[0]), int(date[1])).date()


def build_dict_for_factory_method(url, sheet_names) -> list:
    """
    call this one to build the dict for the factory method (factory method is currently in need of repair)
    :param url: the url where the spreadsheet is located
    :return: a list of dicts where each dict represents a row with column headers as keys
    """
    sheet_names_list = parse_sheet_names(sheet_names)
    # this is a list of lists of dictionaries, each list of dictionaries representing an individual sheet:
    cumulative_dict_list = []
    # error = False  # used to track if there is an error in one of the sheets
    for sheet_name in sheet_names_list:
        data = get_data_from_google_drive(url, sheet_name)
        # if len(data) != 0: #and 
        if not data.empty:
            cumulative_dict_list.append(data)
        else:
            logger.error('error retrieving data!')
            # error = True
    if len(cumulative_dict_list) > 0:
        # no error, return the dict list
        return cumulative_dict_list
    else:
        # error, raise
        raise BusinessLogicException


def add_word_empty_for_blank_rows(columns, data):
    # Pandas was getting mad because some rows were blank, so this is my hacky solution for that...
    needed_length = len(columns)
    new_data_list = []
    for item in data:
        if len(item) == 0:  # there were empty rows (they were imported as an empty list, not sure why...)
            pass  # kick to next item
        elif item[0] == '':  # if there is no datetime in the first column, its not a response, so I don't want it either
            pass  # kick to next item
        else:
            while len(item) != needed_length:
                item.append('empty')
            new_data_list.append(item)
    return new_data_list


def strip_and_lower_each_response(data):
    new_data = [] # this will replace the data coming in
    for item in data:
        new_row = []  # this will replace the row of data coming in
        for token in item:
            token = token.strip() # remove any leading or trailing whitespace (want to do this to all pieces of data)
            if token in DIFFERENT_VARIATIONS_OF_NA:  # people type N/A a lot of different ways...
                # I want them all to be counted as the same response, to cut down on the number of columns output
                token = 'N/A'
            if is_alpha(token):  # if the piece of data is only letters, I want to lowercase it
                token_lower = token.lower()  # lowercase
                new_row.append(token_lower)
            else: # the piece of data contains not alphabetic characters, but I still want to append the stripped token
                new_row.append(token)
        new_data.append(new_row)
    return new_data


def strip_column_names(columns):
    # I want to remove any potential leading & trailing whitespace from the column names, so they are counted the same
    new_columns = []
    for item in columns:
        new_item = item.strip()
        new_columns.append(new_item)
    return new_columns


def is_alpha(string):
    # will tell you if a string contains only alphabetic characters or spaces
    for char in string:
        if not char.isalpha() and char != ' ':  # if the character is not a space or an alphabetic char...
            return False
    return True


def get_data_from_google_drive(url: str, sheet_name: str) -> []:
    """
    calls on GoogleAuthManager to return JSON representing the data in a single sheet of a Google Drive spreadsheet
    :param url: the url where the spreadsheet is located
    :return: a list of list, each list containing a row of data
    """
    try:
        results = GoogleAuthManager.get_data_from_file(url, sheet_name)
        columns = results['values'][0]  # set column headers
        columns = strip_column_names(columns)
        results['values'].pop(0)  # remove column headers from the results
        data = results['values']
        data = add_word_empty_for_blank_rows(columns, data)
        data = strip_and_lower_each_response(data)
        df = pandas.DataFrame(data, columns=columns)
        return df
    except DalException:
        raise BusinessLogicException


def parse_sheet_names(sheet_names: str) -> list:
    """
    takes a string separated by commas, returns a list with each item in that list representing one sheet name
    :param sheet_names: the string containing the sheet names (from gui layer)
    :return: a list with each item/index in the list representing one individual sheet name
    """
    sheet_name_list = []
    tokens = sheet_names.split(",")
    for item in tokens:
        item = item.strip()
        sheet_name_list.append(item)
    logger.info(f'parsed sheet names: {sheet_name_list}')
    return sheet_name_list


def generate_report_type_string(report_type='monthly'):
    """
    generates a string to return to the user stating the type of report this row of data represents.
    :param report_type: the report type the user selected. default is monthly (need to change this probably)
    :return: a string stating the type of report this row of data represents.
    """
    current_month_year = return_current_month_year()
    if report_type == 'monthly':
        return f"Monthly totals for {calendar.month_abbr[current_month_year[0]]}, {current_month_year[1]}"
    elif report_type == 'ytd':
        return f"Year To Date totals for {current_month_year[1]}"
    elif report_type == 'custom':
        return f"Totals for custom date range"  # I want to think of a way to pass the custom dates here.


def write_guest_report_to_drive(exit_guest_list, url, report_date_range, report_type):
    """
    writes a ExitGuestList object to a Google Sheet on the user's drive, outcomes vary based on the report_type
    :param new_guest_list: the ExitGuestList object to base the report on (should be sorted by date)
    :param report_date_range: report type the user wants (currently, 'monthly', 'custom', or 'ytd'
    :return: no return, calls GoogleAuthManager.append_data_to_file()
    """
    #google_key = GoogleAuthManager.parse_link(url)
    exit_guest_list = convert_str_int(exit_guest_list)
    guest_dict = guest_int_report(exit_guest_list)
    guest_dict = guest_object(exit_guest_list, guest_dict)
    guest_dict = sorted_dict(guest_dict)
    guest_dict = clean_up_guest_dict(guest_dict)
    guest_dict = fix_multiple_choice_counts(guest_dict)

    # before I split the dict up into rows, I will grab the number of guests so I can add that to the first row
    guest_count = guest_dict['# of guests']
    guest_dict.pop('# of guests')  # now remove the number of guests from the dict
    guest_dict_list = split_into_multiple_rows(guest_dict)  # then split it into rows
    report_name = generate_report_type_string(report_date_range)  # also grab report name for the output...

    # add some separation to the spreadsheet, also output the report type & number of guests counted
    first_row = [report_name, report_type, f"Total Guests: {guest_count}"]
    try:
        GoogleAuthManager.append_data_to_file([first_row], url)
    except DalException:
        logger.error("Some exception encountered when trying to write data to drive")
        raise BusinessLogicException

    # now, actually add the data!
    for row in guest_dict_list:
        keys = (list(row.keys()))
        values = (list(row.values()))
        keys = make_list_have_string(keys)
        values = make_list_have_string(values)
        try:
            GoogleAuthManager.append_data_to_file([keys], url)
            GoogleAuthManager.append_data_to_file([values], url)
        except DalException:
            logger.error("Some exception encountered when trying to write data to drive")
            raise BusinessLogicException

    # then add another border to the end, I will add the date generated here because that may be nice to know
    today = datetime.today()
    end_border = [f"Report Generated On: {today}"]
    GoogleAuthManager.append_data_to_file([end_border], url)
    # Auto-Resize the sheet...
    GoogleAuthManager.resize_columns(url)


def clean_up_guest_dict(guest_dict):
    # want to clean up the guest dict to remove responses of: nan, empty, empty string
    responses_to_remove = ['nan', 'empty', '']
    keys_to_delete = []
    for key in guest_dict.keys():
        tokens = key.split('::')  # split question from response
        try:
            response_token = tokens[1]  # this is the response portion of the key
            sliced_response = response_token[13:]  # slice off the leading space & newline char
            if sliced_response in responses_to_remove:
                keys_to_delete.append(key)  # add key to list to be deleted
        except IndexError:  # the '# of guest' column will not split and thus will cause an index error
            pass  # just pass that one, we want to keep it anyway...
    # now actually delete the matching keys:
    # you may wonder why I didn't do this in the above for loop... you cannot modify a dictionary's size while
    # you are iterating over it, it will cause errors.
    for key in keys_to_delete:
        del guest_dict[key]
    # finally, return new modified dict:
    return guest_dict


def split_into_multiple_rows(dict):
    # I'm going to take in one dict, then spit out a list of dictionaries, so I can append multiple rows per output
    # instead of just 2 rows, this will prevent the output from being so long, and make it more human-readable
    previous_question = ''  # will be used to track the previous question.
    current_question_counter = 0  # this will be used to count how many times the current question has been seen
    new_dict = {}  # this will be used to store the current dict I am building, I will then clear it each time I
    # add that dict to the dict_list.
    dict_list = []  # this will be the list of dictionaries I am returning.
    iteration_counter = 1  # this will count the number of times I have iterated so far.
    dictionary_length = len(dict)  # I will compare this to the iteration_counter to see when I have come to the end
    # not good at breaking code up with spaces, but I will try here to make it more readable...
    for key in dict.keys():
        iteration_counter += 1
        tokens = key.split('::')
        try:
            question_token = tokens[0]  # this is the question portion of the key
            current_question = question_token.strip()  # just in case, I may have already done this elsewhere in the code

            if current_question == previous_question:  # if the current question has been seen before
                new_dict[key] = dict[key]  # add the current item to the new dict
                current_question_counter += 1  # increase the current_question_counter
            else:
                if current_question_counter >= 1:
                    # if the current question counter is greater than one, and the current question is no longer the same
                    # as the previous question, I want to start a new row
                    dict_list.append(new_dict)  # add the previous question/responses to the list of rows
                    new_dict = {}  # clear out the new dict, so we can start fresh for the next row
                current_question_counter = 0  # questions are not the same, reset the counter.
                previous_question = current_question  # reset the previous question
                new_dict[key] = dict[key]  # add the (previously unseen) new question to the new row's dict

            if iteration_counter == dictionary_length:  # if we have reached the end of the dict
                if len(new_dict) != 0:  # and there is still something in new_dict
                    # then we still have a row stored in new_dict, so we need to append it!
                    dict_list.append(new_dict)

        except IndexError:
            pass  # we insert some columns that will not pass the split, so I will pass those

    return dict_list


def fix_multiple_choice_counts(input_dict):
    multiple_choice_questions = ['Of all of the services that WayStation can offer me, I am interested in these',
                                 'If answered the above, "Sleeping in my home", check any that apply']
    new_dict = {}
    for key in input_dict.keys():
        tokens = key.split('::')  # split up the question & response
        try:
            question_token = tokens[0]  # this is the question portion of the key
            question_string = question_token.strip()  # just in case, I may have already done this elsewhere in the code
            if question_string not in multiple_choice_questions:
                # can go ahead and add it to the new dict, these are not the droids you're looking for
                new_dict[key] = input_dict[key]
            else:
                # the question is one we are looking for...
                response_token = tokens[1]  # get the response
                response_token = response_token.lower()
                sliced_response = response_token[13:]  # slice off the leading space & newline char
                individual_response = sliced_response.split(',')  # each individual response is split by a ','
                for answer in individual_response:
                    answer = answer.strip()
                    new_key = f"{question_string} :: \n Response: {answer}"  # rebuild the key
                    if new_key in new_dict.keys():  # if we have already come across this answer before...
                        new_dict[new_key] += 1  # increase count by 1
                    else:
                        # have not come across this question before
                        new_dict[new_key] = 1  # count is 1
        except IndexError:
            pass # we insert some columns that will not pass the split, so I will pass those
    return new_dict
    

def make_list_have_string(values):
    """
    To make every value in a given list into a string.
    This method fixes an issue where the Google sheet import does not read integers, but reading it
    as a string fixes the issue.
    :param value: A given list
    :return: A list of strings
    """
    str_values = []
    for value in values:
        str_values.append(f'{value}')
    return str_values


def sorted_dict(dict):
    """
    To sort a dictionary. I decided to sort the dictionary alpabetically
    because this makes outputing the data more readable. (Special characters -> A -> Z)
    :param dict: A given dictionary
    :return: A sorted dictionary.
    """
    dict_keys = list(dict.keys())
    dict_keys.sort()
    sorted_dict = {i: dict[i] for i in dict_keys}
    return sorted_dict

def guest_object(exit_guest_list, guest_dict):
    """
    To dynamically process a object and put it into a dictionary.
    :param exit_guest_list: unprocess data
    :param guest_dict: A dictionary of process data.
    :return: A dictionary of process data based on the exit guest list object.
    """
    guest_len_list = len(exit_guest_list)
    for index in range(0, guest_len_list):
        for column in exit_guest_list.select_dtypes(include=object):
            value = f'{column} :: \n Response: {exit_guest_list.loc[index, column]}'
            if exit_guest_list.loc[index, column] is not None and value not in guest_dict.keys() and f'{column}'.lower() not in COLUMNS:
                guest_dict[value] = 1
            elif exit_guest_list.loc[index, column] is not None and value in guest_dict.keys() and f'{column}'.lower() not in COLUMNS:
                guest_dict[value] += 1
    return guest_dict
            

def guest_int_report(guests):
    """
    To dynamically process a object and put it into a dictionary.
    :param guests: An object that holds unprocess data.
    :return: Process data based on guests.
    """
    guest_dict = {}
    guest_dict['# of guests'] = len(guests)
    for column in guests.select_dtypes(include=int):
        if column != 'index' and column not in guest_dict.keys() and f'{column}'.lower() not in COLUMNS:
            mean_value = f'{column}---mean'
            max_value = f'{column}---max'
            min_value = f'{column}---min'
            guest_dict[mean_value] = guests[column].mean()
            guest_dict[max_value] = guests[column].max()
            guest_dict[min_value] = guests[column].min()
    return guest_dict
            

def convert_str_int(results):
    """
    If a string column contains integers only. Make the whole column an  integer.
    This solves an issue, it help us to dynamically process data much more easily.
    :param results: Given data that can hold anything.
    :return: Updated results.
    """
    for column in results:
        try:
            results[column] = results[column].astype(int)
        except:
            pass
    return results


def delete_token():
    """
    To delete a token
    """
    if os.path.isfile("token.json"):
        os.remove("token.json")

def pass_error_message(message: str):
    return gui.ProcessForm.display_error_message(message)