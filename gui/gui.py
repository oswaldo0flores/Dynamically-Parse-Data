import tkinter as tk
from tkcalendar import DateEntry
import business
from tkinter import ttk, messagebox
from exceptions import BusinessLogicException
from PIL import Image, ImageTk
import os, sys
import json


# should rename the first one to just 'Totals' since they will select a month, or current month, or year, or any
# other timeframe. but I will hold off on that for now.
DESIRED_DATA = ['New Guest Report Totals', 'Welcome Back Report Totals', 'Exit/Feedback Data']
#IMG_FILENAME = os.path.join(os.path.dirname(sys.executable), 'way_station_image.png')


class ProcessForm:
    def __init__(self, root):
        """
        To initalize the GUI class. 
        """
        self.root = root
        self.root.title('Google Sheet Parser')
        self.root.config(bg='black')  # just leaving this here so we have the option to change it later if we want
        self.create_widgets()

    def create_widgets(self):
        """
        To desgin the GUI application. This application must be easy to use.
        The user must be able to pass through a google sheet and process that
        data.
        """
        left_frame = tk.Frame(self.root, width=75, height=55, bg='white')
        left_frame.grid(row=0, column=0, padx=5, pady=5)

        right_frame = tk.Frame(self.root, width=75, height=55, bg='white')
        right_frame.grid(row=0, column=1, padx=5, pady=5)

        #waystation_logo = Image.open(IMG_FILENAME)  # open image
        # waystation_logo = Image.open('way_station_image.png')
        #waystation_logo = waystation_logo.resize((175,75))  # resize image
        #waystation_logo = ImageTk.PhotoImage(waystation_logo)  # convert it to a tkinter photoimage object...

    # -> LEFT FRAME <-
        #self.image_label = tk.Label(left_frame, image=waystation_logo, background='white')
        #self.image_label.image = waystation_logo
        #self.image_label.grid(row=0, column=0, columnspan=2, padx=7, pady=7)

        # assuming we are going to grab the url for the google sheets from them..
        self.url_label = ttk.Label(left_frame, text="URL of the Google Sheet: ", background='white',
                                   font=('Helvetica', 12))
        self.url_label.grid(row=1, column=0, padx=7, pady=10, sticky='e')
        self.url_entry = ttk.Entry(left_frame, width=50)
        self.url_entry.grid(row=1, column=1, padx=7, pady=10)

        self.sheet_names_entry_label = ttk.Label(left_frame, text="Sheet Names: ", background='white',
                                                     font=('Helvetica', 12))
        self.sheet_names_entry_label.grid(row=2, column=0, padx=7, pady=10, sticky='e')
        self.sheet_names_entry = ttk.Entry(left_frame, width=50)
        self.sheet_names_entry.grid(row=2, column=1, padx=7, pady=10, sticky='w')

        self.desired_output_label = ttk.Label(left_frame, text="Desired Report Type: ", background='white',
                                              font=('Helvetica', 12))
        self.desired_output_label.grid(row=3, column=0, padx=7, pady=10, sticky='e')
        self.output_options = DESIRED_DATA
        self.desired_output_combobox = ttk.Combobox(left_frame, state='readonly', width=35, values=self.output_options)
        self.desired_output_combobox.grid(row=3, column=1, padx=7, pady=10, sticky='w')

        self.output_file_name_label = ttk.Label(left_frame, text="Output Google Sheet URL: ", background='white',
                                                font=('Helvetica', 12))
        self.output_file_name_label.grid(row=4, column=0, padx=7, pady=10, sticky='e')
        self.output_file_name_entry = ttk.Entry(left_frame, width=50)
        self.output_file_name_entry.grid(row=4, column=1, padx=7, pady=10)

        self.selected_radio_button = tk.IntVar()

        # date selection frame
        self.date_selection_label = ttk.Label(left_frame, text="Date Range Selection", background='white',
                                              justify=tk.CENTER, font=('Helvetica', 12, 'bold'))
        self.date_selection_label.grid(row=5, column=0, columnspan=2, padx=1, pady=1)
        self.date_selection_frame = ttk.Frame(left_frame, width=30, borderwidth=5, relief='sunken')
        self.date_selection_frame.grid(row=6, rowspan=3, column=0, columnspan=2, padx=5, pady=5, ipady=5)

        self.from_selection_radiobutton = tk.Radiobutton(self.date_selection_frame, text="From Selection",
                                                         value=0, variable=self.selected_radio_button)
        self.from_selection_radiobutton.grid(row=6, column=2, padx=5, pady=1)
        self.current_month_checkbox = tk.Radiobutton(self.date_selection_frame, text="Current Month",
                                                     value=1, variable=self.selected_radio_button)
        self.current_month_checkbox.grid(row=7, column=2, padx=5, pady=1)
        self.ytd_checkbox = tk.Radiobutton(self.date_selection_frame, text="Current Year", value=2,
                                           variable=self.selected_radio_button)
        self.ytd_checkbox.grid(row=8, column=2, padx=5, pady=1)

        self.start_date_label = ttk.Label(self.date_selection_frame, text='Start Date: ', font=('Helvetica', 10))
        self.start_date_label.grid(row=6, column=0, padx=3, pady=5, sticky='e')
        self.start_cal = DateEntry(self.date_selection_frame, width=12, background='darkblue', foreground='white',
                                   borderwidth=2)
        self.start_cal.grid(row=6, column=1, padx=3, pady=5, sticky='w')
        self.end_date_label = ttk.Label(self.date_selection_frame, text='End Date: ', font=('Helvetica', 10))
        self.end_date_label.grid(row=7, column=0, padx=3, pady=5, sticky='e')
        self.end_cal = DateEntry(self.date_selection_frame, width=12, background='darkblue', foreground='white',
                                 borderwidth=2)
        self.end_cal.grid(row=7, column=1, padx=3, pady=5, sticky='w')

    # -> RIGHT FRAME <-
        self.status_label = tk.Label(right_frame, text='Status:', font=('Helvetica', 12, 'bold'), justify=tk.CENTER,
                                      background='white')
        self.status_label.grid(row=0, column=0, columnspan=2)

        self.status_tracking_label = tk.Label(right_frame, text='Ready...', font=('Helvetica', 12), justify=tk.CENTER,
                                              background='white')
        self.status_tracking_label.grid(row=1, column=0, columnspan=2)

        self.go_button = tk.Button(right_frame, text='Go', bg='green', width=20, command=self.click_go,
                                   font=('Helvetica', 12, 'bold'))
        self.go_button.grid(row=2, column=0, columnspan=2, padx=15, pady=10, ipadx=2, sticky='w,e')
        self.go_button.bind('<Enter>', self.go_button_color_change_enter)
        self.go_button.bind('<Leave>', self.go_button_color_change_leave)

        self.save_urls_button = tk.Button(right_frame, text='Save Current Fields', width=20,
                                          font=('Helvetica', 12, 'bold'), command=self.save_url_onclick)
        self.save_urls_button.grid(row=4, column=0, columnspan=2, padx=15, pady=10, ipadx=2, sticky='w,e')

        self.load_urls_button = tk.Button(right_frame, text='Load Fields', width=20,
                                          font=('Helvetica', 12, 'bold'), command=self.load_url_onclick)
        self.load_urls_button.grid(row=3, column=0, columnspan=2, padx=15, pady=10, ipadx=2, sticky='w,e')

        self.help_button = tk.Button(right_frame, text='Help', width=15, command=self.click_help,
                                     font=('Helvetica', 12, 'bold'))
        self.help_button.grid(row=5, column=0, columnspan=2, padx=15, pady=10, ipadx=2, sticky='w,e')

        self.delete_token_button = tk.Button(right_frame, text='Logout', width=15,
                                             font=('Helvetica', 12, 'bold'), command=self.click_delete)
        self.delete_token_button.grid(row=6,column=0, columnspan=2, padx=15, pady=10, ipadx=2, sticky='w,e')
        
        self.menu_one = tk.Menu(self.url_entry, tearoff=0)
        self.menu_one.add_command(label="Copy", command=lambda: self.url_entry.event_generate("<<Copy>>"))
        self.menu_one.add_separator()
        self.menu_one.add_command(label="Cut", command=lambda: self.url_entry.event_generate("<<Cut>>"))
        self.menu_one.add_separator()
        self.menu_one.add_command(label="Paste", command=lambda: self.url_entry.event_generate("<<Paste>>"))
        self.url_entry.bind("<Button - 3>", self.pop_menu_one)
        
        self.menu_two = tk.Menu(self.sheet_names_entry, tearoff=0)
        self.menu_two.add_command(label="Copy", command=lambda: self.sheet_names_entry.event_generate("<<Copy>>"))
        self.menu_two.add_separator()
        self.menu_two.add_command(label="Cut", command=lambda: self.sheet_names_entry.event_generate("<<Cut>>"))
        self.menu_two.add_separator()
        self.menu_two.add_command(label="Paste", command=lambda: self.sheet_names_entry.event_generate("<<Paste>>"))
        self.sheet_names_entry.bind("<Button - 3>", self.pop_menu_two)
        self.output_file_name_entry.bind("<Button - 3>", self.pop_menu_two)
        
        self.menu_three = tk.Menu(self.output_file_name_entry, tearoff=0)
        self.menu_three.add_command(label="Copy", command=lambda: self.output_file_name_entry.event_generate("<<Copy>>"))
        self.menu_three.add_separator()
        self.menu_three.add_command(label="Cut", command=lambda: self.output_file_name_entry.event_generate("<<Cut>>"))
        self.menu_three.add_separator()
        self.menu_three.add_command(label="Paste", command=lambda: self.output_file_name_entry.event_generate("<<Paste>>"))
        self.output_file_name_entry.bind("<Button - 3>", self.pop_menu_three)
   
    def pop_menu_one(self, event):
        """
        A popup menu when the user right click a text box.
        """
        try: 
            self.menu_one.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_one.grab_release()
            
    def pop_menu_two(self, event):
        """
        A popup menu when the user right click a text box.
        """
        try: 
            self.menu_two.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_two.grab_release()
            
    def pop_menu_three(self, event):
        """
        A popup menu when the user right click a text box.
        """
        try: 
            self.menu_three.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_three.grab_release()

    def click_delete(self):
        """
        To delete a token.
        """
        self.status_tracking_label.config(text='Deleting Token... (in progress)')
        business.new_guests_bl.delete_token()
        self.status_tracking_label.config(text='Token Deleted Successfully!')
        
    def click_help(self):
        """
        To help the client.
        """
        self.status_tracking_label.config(text='Help File Opened')
        os.startfile('help_file.txt')

    def click_go(self):
        """
        event handler for the go button
        this function is getting pretty large, it's ripe for abstraction, I'll do this next week unless you want to
        """
        self.status_tracking_label.config(text="Processing...")
        selected_radio_button = self.selected_radio_button.get()
        url = self.url_entry.get()
        sheet_names = self.sheet_names_entry.get()
        start_date = self.start_cal.get_date()
        end_date = self.end_cal.get_date()
        desired_data = self.desired_output_combobox.get()
        output_url = self.output_file_name_entry.get()
        if not self.is_url(url) and not self.is_url(output_url):
            self.display_error_message("The provided URL looks wrong")
        elif not self.is_not_empty(sheet_names):
            self.display_error_message("You must enter sheet name(s)")
        elif not self.is_not_empty(desired_data):
            self.display_error_message("You must pick a data output type (desired data)")
        else:
            try:
                if selected_radio_button == 0:
                    if desired_data == 'New Guest Report Totals':
                        new_guest_list = business.generate_new_guest_list_class(url, sheet_names)
                        results = business.new_guests_bl.sort_guests_by_date(new_guest_list, start_date, end_date)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'custom', desired_data)
                    elif desired_data == 'Welcome Back Report Totals':
                        return_guest_list = business.generate_return_guest_list(url, sheet_names)
                        results = business.new_guests_bl.sort_guests_by_date(return_guest_list, start_date, end_date)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'custom', desired_data)
                    elif desired_data == 'Exit/Feedback Data':
                        exit_guest_list = business.generate_exit_guest_list(url, sheet_names)
                        results = business.new_guests_bl.sort_guests_by_date(exit_guest_list, start_date, end_date)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'custom', desired_data)
                elif selected_radio_button == 1:
                    if desired_data == 'New Guest Report Totals':
                        new_guest_list = business.generate_new_guest_list_class(url, sheet_names)
                        results = business.new_guests_bl.return_entries_for_current_month(new_guest_list)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'monthly', desired_data)
                    elif desired_data == 'Welcome Back Report Totals':
                        return_guest_list = business.generate_return_guest_list(url, sheet_names)
                        results = business.new_guests_bl.return_entries_for_current_month(return_guest_list)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'monthly', desired_data)
                    elif desired_data == 'Exit/Feedback Data':
                        exit_guest_list = business.generate_exit_guest_list(url, sheet_names)
                        results = business.new_guests_bl.return_entries_for_current_month(exit_guest_list)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'monthly', desired_data)
                elif selected_radio_button == 2:
                    if desired_data == 'New Guest Report Totals':
                        new_guest_list = business.generate_new_guest_list_class(url, sheet_names)
                        results = business.new_guests_bl.return_entries_for_current_year(new_guest_list)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'ytd', desired_data)
                    elif desired_data == 'Welcome Back Report Totals':
                        return_guest_list = business.generate_return_guest_list(url, sheet_names)
                        results = business.new_guests_bl.return_entries_for_current_year(return_guest_list)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'ytd', desired_data)
                    elif desired_data == 'Exit/Feedback Data':
                        exit_guest_list = business.generate_exit_guest_list(url, sheet_names)
                        results = business.new_guests_bl.return_entries_for_current_year(exit_guest_list)
                        business.new_guests_bl.write_guest_report_to_drive(results, output_url, 'ytd', desired_data)
            except BusinessLogicException:
                self.display_error_message("Fatal Error")
        self.status_tracking_label.config(text="Complete!")

        
    def is_url(self, url):
        """
        Check if it is given an url.
        
        :return: The URL. False if no URL were given.
        """
        return url if url.startswith('https://') else False
    
    def is_not_empty(self, sheet_names):
        """
        Checks if the given data is not empty.
        :return: The string of data. False if the string is empty.
        """
        return sheet_names if sheet_names != '' else False

    @staticmethod
    def display_error_message(message: str):
        """
        Display an error message.
        
        Display an error message. This is a user error and tells the user they enter
        an invalid url.
        """
        tk.messagebox.showerror(title='ERROR', message=message)

    def save_url_onclick(self):
        selected_report_type = self.desired_output_combobox.get()
        if selected_report_type == "":
            self.display_error_message("You must select a 'Desired Report Type'!")
            return
        input_url = self.url_entry.get()
        sheets = self.sheet_names_entry.get()
        output_url = self.output_file_name_entry.get()
        with open('saved_url_fields.json', 'r') as file:
            data = json.load(file)
        if selected_report_type == 'New Guest Report Totals':
            data["New Guest"]["URL"] = input_url
            data["New Guest"]["Sheets"] = sheets
            data["New Guest"]["Output"] = output_url
        elif selected_report_type == 'Welcome Back Report Totals':
            data["Returning Guest"]["URL"] = input_url
            data["Returning Guest"]["Sheets"] = sheets
            data["Returning Guest"]["Output"] = output_url
        elif selected_report_type == 'Exit/Feedback Data':
            data["Exit"]["URL"] = input_url
            data["Exit"]["Sheets"] = sheets
            data["Exit"]["Output"] = output_url
        with open('saved_url_fields.json', 'w') as file:
            json.dump(data, file)
            file.flush()
        self.status_tracking_label.config(text='Saved Fields!')

    def load_url_onclick(self):
        selected_report_type = self.desired_output_combobox.get()
        if selected_report_type == "":
            self.display_error_message("You must select a 'Desired Report Type'!")
            return
        with open('saved_url_fields.json', 'r') as file:
            data = json.load(file)
        if selected_report_type == 'New Guest Report Totals':
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(tk.END, data["New Guest"]["URL"])
            self.sheet_names_entry.delete(0, tk.END)
            self.sheet_names_entry.insert(tk.END, data["New Guest"]["Sheets"])
            self.output_file_name_entry.delete(0, tk.END)
            self.output_file_name_entry.insert(tk.END,data["New Guest"]["Output"])
        elif selected_report_type == 'Welcome Back Report Totals':
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(tk.END, data["Returning Guest"]["URL"])
            self.sheet_names_entry.delete(0, tk.END)
            self.sheet_names_entry.insert(tk.END, data["Returning Guest"]["Sheets"])
            self.output_file_name_entry.delete(0, tk.END)
            self.output_file_name_entry.insert(tk.END,data["Returning Guest"]["Output"])
        elif selected_report_type == 'Exit/Feedback Data':
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(tk.END, data["Exit"]["URL"])
            self.sheet_names_entry.delete(0, tk.END)
            self.sheet_names_entry.insert(tk.END, data["Exit"]["Sheets"])
            self.output_file_name_entry.delete(0, tk.END)
            self.output_file_name_entry.insert(tk.END, data["Exit"]["Output"])
        self.status_tracking_label.config(text='Loaded Fields From Save')

    def go_button_color_change_enter(self, event):
        """
        changes the color of the go button on mouseover
        :param event: the mouseover event for this button
        :return: n/a
        """
        self.go_button.config(bg='blue')

    def go_button_color_change_leave(self, event):
        """
        changes the color of the go button back after mouseover
        :param event: the mouseover event for this button
        :return: n/a
        """
        self.go_button.config(bg='green')

    @staticmethod
    def run() -> None:
        """
        runs the application
        :return: n/a
        """
        root = tk.Tk()
        form = ProcessForm(root)
        root.mainloop()


