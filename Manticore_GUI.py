import tkinter as tk
from tkinter import ttk
#from datetime import datetime
#from tkinter.messagebox import askyesno
#import webbrowser
#import tkinter.font as tkFont
import os
from itertools import chain
from sys import platform
from tkinter.messagebox import askyesno


class Manticore_GUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Manticore 3.14")
        self.input_card_path, self.data_directory_path, self.temp_directory_path = self.get_pathes()
        self.main_frame = tk.LabelFrame(self, bd=0)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.head_frame = tk.LabelFrame(self.main_frame, text="Choose the source of settings", bd=2)
        self.head_frame.pack(fill="x", padx=10, pady=10)
        self.__set_head_frame()
        self.automatic_settings_frame = tk.LabelFrame(self.main_frame, text="Automatic settings", bd=2)
        self.automatic_settings_frame.pack(fill="both", expand=False, padx=10, pady=10)
        self.__set_automatic_settings_frame()
        self.manual_settings_frame = tk.LabelFrame(self.main_frame, text="Manual settings", bd=2)
        self.manual_settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.__set_manual_settings_frame()
        self.run_frame = tk.LabelFrame(self.main_frame, text="Run", bd=2)
        self.run_frame.pack(fill="both", expand=False, padx=10, pady=10)
        self.__set_run_frame()
        self.frame_activator(from_manual_to_automatic=0)

    def __set_head_frame(self):
        self.settings_choose_var = tk.BooleanVar()
        self.settings_choose_var.set(1)
        automatic_settings_radiobutton = tk.Radiobutton(self.head_frame, text='Input card', variable=self.settings_choose_var, value=False, command=lambda: self.frame_activator(from_manual_to_automatic=1))
        manual_settings_radiobutton = tk.Radiobutton(self.head_frame, text='Set manually', variable=self.settings_choose_var, value=True, command=lambda: self.frame_activator(from_manual_to_automatic=0))
        automatic_settings_radiobutton.pack(side="left", padx=10, pady=10)
        manual_settings_radiobutton.pack(side="left", padx=10, pady=10)

        self.head_separator = ttk.Separator(self.head_frame, orient='vertical')
        self.head_separator.pack(side="left", fill='y', padx=5, pady=5)

        self.data_directory_path_label = tk.Label(self.head_frame, text="Data directory:")
        self.data_directory_path_label.pack(side="left", padx=10, pady=10)
        self.data_directory_path_field = tk.Entry(self.head_frame, width=30)
        self.data_directory_path_field.insert('end', self.data_directory_path)
        self.data_directory_path_field.configure(state='disabled')
        self.data_directory_path_field.pack(side="left", padx=5, pady=10)
        self.data_directory_path_field.bind("<Return>", self.change_data_directory_path)
        self.data_directory_path_button = tk.Button(self.head_frame, text="Change path", command=lambda: self.set_path(self.data_directory_path_field))
        self.data_directory_path_button.pack(side="left", padx=5, pady=10)

        self.temp_directory_path_label = tk.Label(self.head_frame, text="Temporary files directory:")
        self.temp_directory_path_label.pack(side="left", padx=15, pady=10)
        self.temp_directory_path_field = tk.Entry(self.head_frame, width=30)
        self.temp_directory_path_field.insert('end', self.temp_directory_path)
        self.temp_directory_path_field.configure(state='disabled')
        self.temp_directory_path_field.pack(side="left", padx=5, pady=10)
        self.temp_directory_path_field.bind("<Return>", self.change_temp_directory_path)
        self.temp_directory_path_button = tk.Button(self.head_frame, text="Change path", command=lambda: self.set_path(self.temp_directory_path_field))
        self.temp_directory_path_button.pack(side="left", padx=5, pady=10)

    def __set_automatic_settings_frame(self):
        self.input_card_path_label = tk.Label(self.automatic_settings_frame, text="Path to input card:")
        self.input_card_path_label.pack(side="left", padx=10, pady=10)
        self.input_card_path_field = tk.Entry(self.automatic_settings_frame, width=70)
        self.input_card_path_field.insert('end', self.input_card_path)
        self.input_card_path_field.configure(state='disabled')
        self.input_card_path_field.pack(side="left", padx=10, pady=10)
        self.input_card_path_field.bind("<Return>", self.change_input_card_path)
        self.input_card_path_button = tk.Button(self.automatic_settings_frame, text="Change path", command=lambda: self.set_path(self.input_card_path_field))
        self.input_card_path_button.pack(side="left", padx=10, pady=10)

    def __set_manual_settings_frame(self):
        self.object_list_frame = tk.LabelFrame(self.manual_settings_frame, text="List of objects to process", bd=2)
        self.object_list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.presets_frame = tk.LabelFrame(self.manual_settings_frame, text="Presets", bd=2)
        self.presets_frame.pack(side="left", padx=10, pady=10, anchor="n")
        self.checkbutton_frame = tk.Frame(self.presets_frame, bd=2)
        self.checkbutton_frame.pack(side="top", padx=10, pady=10, anchor="nw")

        self.objects_listbox = tk.Listbox(self.object_list_frame, selectmode='extended')

        self.objects_listbox.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.set_1 = tk.Checkbutton(self.checkbutton_frame, text="Delete existing temporary files before processing and start with new raw processing")
        self.set_1.pack(side="top", padx=10, pady=10, anchor="nw")
        self.set_2 = tk.Checkbutton(self.checkbutton_frame, text="To leave all the temporary files after processing finish")
        self.set_2.pack(side="top", padx=10, pady=10, anchor="nw")

        self.add_button = tk.Button(self.checkbutton_frame, text="Add item", command=lambda: self.add_item())
        self.add_button.pack(side="top", padx=10, pady=10, anchor="w")
        self.new_item_field = tk.Entry(self.checkbutton_frame)
        self.input_card_path_field.bind("<Return>", self.add_item)
        self.new_item_field.pack(side="top", padx=10, pady=10, anchor="w")

    def add_item(self):
        item_list = self.new_item_field.get().split()
        for item in item_list:
            self.objects_listbox.insert('end', item)
        self.new_item_field.delete(0, 'end')

    def del_last(self):
        select = list(self.objects_listbox.curselection())
        select.reverse()
        for i in select:
            self.objects_listbox.delete(i)




    def __set_run_frame(self):
        self.run_button = tk.Button(self.run_frame, text="Run", bg="red", command=lambda: self.run_frame_update())
        self.run_button.pack(side="left", padx=10, pady=10)

    def run_frame_update(self):
        self.operation_numerator_label = tk.Label(self.run_frame, text="Operation")
        self.operation_numerator_label.pack(side="left", padx=10, pady=10)
        self.operation_numerator = tk.Label(self.run_frame, text="0/0")
        self.operation_numerator.pack(side="left", padx=10, pady=10)
        self.operation_name = tk.Label(self.run_frame, text="Operation Name")
        self.operation_name.pack(side="left", padx=10, pady=10)
        self.stop_btn = tk.Button(self.run_frame, text="Stop", bg='red', command=lambda: self.stop())
        self.stop_btn.pack(side='left', fill='x', padx=10, pady=10)
        self.progressbar_value_var = tk.IntVar()
        self.progressbar_value_var.set(0)
        self.progressbar =  ttk.Progressbar(self.run_frame, orient="horizontal", variable=self.progressbar_value_var)
        self.progressbar.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        self.percents = tk.Label(self.run_frame, text=f'0 %')
        self.percents.pack(side="left", padx=10, pady=10)
        self.run_button.configure(state='disabled', bg='gray')
        self.run()

    def run(self):
        self.progressbar.start(1000)

    def stop(self):
        if askyesno(title="Processing stop!", message="Do you really want to stop the processing? All created temporary files will NOT be deleted."):
            self.stop_processing()
            self.run_frame.destroy()
            self.run_frame = tk.LabelFrame(self.main_frame, text="Run", bd=2)
            self.run_frame.pack(fill="both", expand=False, padx=10, pady=10)
            self.__set_run_frame()

    def stop_processing(self):
        pass

    def frame_activator(self, from_manual_to_automatic=True):
        if from_manual_to_automatic:
            self.input_card_path_button.configure(state='normal')
            for child in chain(self.object_list_frame.winfo_children(), self.checkbutton_frame.winfo_children()):
                child.configure(state='disabled')
        elif not from_manual_to_automatic:
            self.input_card_path_button.configure(state='disabled')
            for child in chain(self.object_list_frame.winfo_children(), self.checkbutton_frame.winfo_children()):
                child.configure(state='normal')

    def set_path(self, path_field):
        if path_field['state'] == 'disabled':
            path_field.configure(state='normal')
            path_field.update()

    def change_input_card_path(self, event):
        self.input_card_path = self.input_card_path_field.get()
        self.input_card_path_field.configure(state='disabled')
        self.input_card_path_field.update()

    def change_data_directory_path(self, event):
        self.data_directory_path = self.data_directory_path_field.get()
        self.data_directory_path_field.configure(state='disabled')
        self.data_directory_path_field.update()

    def change_temp_directory_path(self, event):
        self.temp_directory_path = self.temp_directory_path_field.get()
        self.temp_directory_path_field.configure(state='disabled')
        self.temp_directory_path_field.update()

    def get_pathes(self):
        if platform == 'win32':
            with open(os.getcwd() + "\Manticore_3.14\\data_directory.conf", "r") as dir_config:
                data_directory = dir_config.readline().strip()
            with open(os.getcwd() + "\Manticore_3.14\\temporary_files_directory.conf", "r") as temp_dir_config:
                temp_files_directory = temp_dir_config.readline().strip()
            return os.getcwd() + "\Manticore_3.14\\input_card.conf", data_directory, temp_files_directory
        elif platform in ['linux', 'darwin']:
            with open(os.getcwd() + "/data_directory.conf", "r") as dir_config:
                data_directory = dir_config.readline().strip()
            with open(os.getcwd() + "/temporary_files_directory.conf", "r") as temp_dir_config:
                temp_files_directory = temp_dir_config.readline().strip()
            return os.getcwd() + "/input_card.conf", data_directory, temp_files_directory


if __name__ == "__main__":
    Manticore_GUI().mainloop()