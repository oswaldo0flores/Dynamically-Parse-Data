import business
import pandas
from exceptions import BusinessLogicException, DalException
from logging_config import get_logger


logger = get_logger(__name__)

# CONST_GET_HELP_ONE = 'If you came to WayStation today for any of the following, did you get help you needed today with:'
# CONST_GET_HELP_TWO = '\n~something to eat and drink'
# CONST_GET_HELP_THREE = '\n~hygiene supplies'
# CONST_GET_HELP_FOUR = '\n~getting out of rain, heat or cold'
# CONST_GET_HELP_FIVE = '\n~a change of clothes'
# CONST_GET_HELP_SIX = '\n~a face mask'
# CONST_GET_HELP = f'{CONST_GET_HELP_ONE}{CONST_GET_HELP_TWO}{CONST_GET_HELP_THREE}{CONST_GET_HELP_FOUR}{CONST_GET_HELP_FIVE}{CONST_GET_HELP_SIX}'

# CONST_TWO_HOURS_NEEDS_ONE = 'If you were at WayStation for at least 2 hours today, and you needed any of these things:'
# CONST_TWO_HOURS_NEEDS_TWO = '\n~a locker'
# CONST_TWO_HOURS_NEEDS_THREE = '\n~to use a computer'
# CONST_TWO_HOURS_NEEDS_FOUR = '\n~to use the phone'
# CONST_TWO_HOURS_NEEDS_FIVE = '\nWere you able to use these things you needed?'
# CONST_TWO_HOURS_NEEDS = f'{CONST_TWO_HOURS_NEEDS_ONE}{CONST_TWO_HOURS_NEEDS_TWO}{CONST_TWO_HOURS_NEEDS_THREE}{CONST_TWO_HOURS_NEEDS_FOUR}{CONST_TWO_HOURS_NEEDS_FIVE}'


class ExitGuestList:
    
    def __init__(self, exit_guest_list):
        """
        To initialize the class with an empty list. This class should have a mutable list because
        at the start of the application I do not know how many new guests I am getting.
        """
        self._exit_guest_list = exit_guest_list
        
    def __len__(self):
        """
        To get the length of the list.
        :return: Length of the list
        """
        return len(self._exit_guest_list)
    
    def __str__(self):
        """
        To display the class data in a readable way.
        :return: Data from the class.
        """
        return f"".join([f"{line}\n" for line in self._exit_guest_list])

    def __iter__(self):
        """
        To iterate over the list. Yields every guest in the list
        """
        for guest in self._exit_guest_list:
            yield guest
        
    @staticmethod
    def exit_guest_factory(url: str, sheet_names: str):
        """
        factory method to generate a ExitGuestList class, which itself contains a list of exit guest objects
        :param url: the url where the data is located (google drive url)
        :param sheet_names: the sheet names from the gui entry field with the same name
        :return: a ExitGuestList object 
        """
        try:
            exit_guest_list = business.new_guests_bl.build_dict_for_factory_method(url, sheet_names)
            #pandas.set_option("display.max_columns", 100)
            if exit_guest_list:
                exit_guests = ''
                list_length = len(exit_guest_list)
                if list_length > 1:
                    exit_guests = pandas.concat(exit_guest_list, ignore_index=True)
                else:
                    exit_guests = exit_guest_list[0]
                #print(exit_guests)
                return exit_guests
            else:
                logger.error(f'Error parsing google sheet, it returned None')
                raise BusinessLogicException
        except DalException:
            raise BusinessLogicException


# class ExitGuest:
#     def __init__(self, timestamp, rating, guest_helped, two_hours_needs, service_satisfied, comments):
#         """
#         To intialize the class with a given data. This data should not change.
#         """
#         self._timestamp = timestamp
#         self._rating = rating
#         self._guest_helped = guest_helped
#         self._two_hours_needs = two_hours_needs
#         self._service_satisfed = service_satisfied
#         self._comments = comments
        
#     @property
#     def timestamp(self):
#         """
#         To get the timestamp from a guest.
#         """
#         return str(self._timestamp)
    
#     @property 
#     def rating(self):
#         """
#         To get a rating from the guest.
#         """
#         return int(self._rating)
    
#     @property 
#     def guest_helped(self):
#         """
#         To determine if the guest got help throughout the day.
#         """
#         return self._guest_helped
    
#     @property 
#     def two_hours_needs(self):
#         """
#         To determine if the guest got helped within two hours.
#         """
#         return self._two_hours_needs
        
#     @property
#     def service_satisfied(self):
#         """
#         To determine if the guest got a good experience 
#         """
#         return self._service_satisfed
    
#     @property
#     def comments(self):
#         """
#         To get a guest comments.
#         """
#         return self._comments
    
#     def __str__(self):
#         return f"{self._timestamp} | {self._rating} | {self._guest_helped} | {self._two_hours_needs} | {self._service_satisfed} | {self._comments}"

#     def __repr__(self):
#         return f"{self._timestamp} | {self._rating} | {self._guest_helped} | {self._two_hours_needs} | {self._service_satisfed} | {self._comments}"
        
