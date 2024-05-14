import business
import pandas
from exceptions import BusinessLogicException, DalException
from logging_config import get_logger


logger = get_logger(__name__)

class NewGuestList:
    
    def __init__(self, new_guest_list):
        """
        To initialize the class with an empty list. This class should have a mutable list because
        at the start of the application I do not know how many new guests I am getting.
        """
        self._new_guest_list = new_guest_list
        
    def __len__(self) -> int:
        """
        To get the length of the list.
        :return: Length of the list
        """
        return len(self._new_guest_list)

    def __str__(self):
        """
        To display the class data in a readable way.
        :return: Data from the class.
        """
        return f"".join([f"{line}\n" for line in self._new_guest_list])
    
    def __iter__(self):
        """
        To iterate over the list. Yields every guest in the list
        """
        for guest in self._new_guest_list:
            yield guest

    @staticmethod
    def new_guest_factory(url: str, sheet_names: str):
        """
        factory method to generate a NewGuestList class, which itself contains a list of objects
        :param url: the url where the data is located (google drive url)
        :param sheet_names: the sheet names from the gui entry field with the same name
        :return: a NewGuestList object (which is a list containing objects)
        """
        try:
            new_guest_list = business.new_guests_bl.build_dict_for_factory_method(url, sheet_names)
            #pandas.set_option("display.max_columns", 100)
            if new_guest_list:
                new_guests = ''
                list_length = len(new_guest_list)
                if list_length > 1:
                    try:
                        new_guests = pandas.concat(new_guest_list, ignore_index=True)
                    except Exception:
                        logger.error("Error in one of the sheets")
                        business.pass_error_message("There is an error in one of your sheets, please check values of the column headers")
                else:
                    new_guests = new_guest_list[0]
                #print(new_guests)
                return new_guests
            else:
                logger.error(f'Error parsing google sheet, it returned None')
                raise BusinessLogicException
        except DalException:
            raise BusinessLogicException
        
