import tkinter as tk
from tkinter import ttk
import time
import os
from itertools import chain
import sys
from tkinter.messagebox import askyesno


def time_check(start_time):
    current_time = time.time() - start_time
    return f'[ {int(current_time//60//60):2} h {int(current_time//60%60):2} m {int(current_time%60):2} s ]'


class ManticoreGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Manticore 3.14")
        self.input_card_path, self.data_directory_path, self.temp_directory_path = self.__get_pathes()
        self.objects_list = []
        self.set_1, self.set_2 = tk.IntVar(), tk.IntVar()
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
        self.__frame_activator(from_manual_to_automatic=0)

    def __set_head_frame(self):
        self.settings_choose_var = tk.BooleanVar()
        self.settings_choose_var.set(1)
        automatic_settings_radiobutton = tk.Radiobutton(self.head_frame, text='Input card', variable=self.settings_choose_var, value=False, command=lambda: self.__frame_activator(from_manual_to_automatic=1))
        manual_settings_radiobutton = tk.Radiobutton(self.head_frame, text='Set manually', variable=self.settings_choose_var, value=True, command=lambda: self.__frame_activator(from_manual_to_automatic=0))
        automatic_settings_radiobutton.pack(side="left", padx=10, pady=10)
        manual_settings_radiobutton.pack(side="left", padx=10, pady=10)

        # TODO: It is necessary to have smth here to separate! But ttk.Separator can not be 'disabled'
        # self.head_separator = ttk.Separator(self.head_frame, orient='vertical')
        # self.head_separator.pack(side="left", fill='y', padx=5, pady=5)

        self.data_directory_path_label = tk.Label(self.head_frame, text="Data directory:")
        self.data_directory_path_label.pack(side="left", padx=10, pady=10)
        self.data_directory_path_field = tk.Entry(self.head_frame, width=30)
        self.data_directory_path_field.insert('end', self.data_directory_path)
        self.data_directory_path_field.configure(state='disabled')
        self.data_directory_path_field.pack(side="left", padx=5, pady=10)
        self.data_directory_path_field.bind("<Return>", self.__change_data_directory_path)
        self.data_directory_path_button = tk.Button(self.head_frame, text="Change path", command=lambda: self.__set_path(self.data_directory_path_field))
        self.data_directory_path_button.pack(side="left", padx=5, pady=10)

        self.temp_directory_path_label = tk.Label(self.head_frame, text="Temporary files directory:")
        self.temp_directory_path_label.pack(side="left", padx=15, pady=10)
        self.temp_directory_path_field = tk.Entry(self.head_frame, width=30)
        self.temp_directory_path_field.insert('end', self.temp_directory_path)
        self.temp_directory_path_field.configure(state='disabled')
        self.temp_directory_path_field.pack(side="left", padx=5, pady=10)
        self.temp_directory_path_field.bind("<Return>", self.__change_temp_directory_path)
        self.temp_directory_path_button = tk.Button(self.head_frame, text="Change path", command=lambda: self.__set_path(self.temp_directory_path_field))
        self.temp_directory_path_button.pack(side="left", padx=5, pady=10)

    def __set_automatic_settings_frame(self):
        self.input_card_path_label = tk.Label(self.automatic_settings_frame, text="Path to input card:")
        self.input_card_path_label.pack(side="left", padx=10, pady=10)
        self.input_card_path_field = tk.Entry(self.automatic_settings_frame, width=60)
        self.input_card_path_field.insert('end', self.input_card_path)
        self.input_card_path_field.configure(state='disabled')
        self.input_card_path_field.pack(side="left", padx=10, pady=10)
        self.input_card_path_field.bind("<Return>", self.__change_input_card_path)
        self.input_card_path_button = tk.Button(self.automatic_settings_frame, text="Change path", command=lambda: self.__set_path(self.input_card_path_field))
        self.input_card_path_button.pack(side="left", padx=10, pady=10)

    def __set_manual_settings_frame(self):
        self.object_list_frame = tk.LabelFrame(self.manual_settings_frame, text="List of objects to process", bd=2)
        self.object_list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.presets_frame = tk.LabelFrame(self.manual_settings_frame, text="Presets", bd=2)
        self.presets_frame.pack(side="left", padx=10, pady=10, anchor="n")
        self.checkbutton_frame = tk.Frame(self.presets_frame, bd=2)
        self.checkbutton_frame.pack(side="top", padx=10, pady=10, anchor="nw")
        self.objects_var = tk.StringVar(value=self.objects_list)
        self.objects_listbox = tk.Listbox(self.object_list_frame, listvariable=self.objects_var, selectmode='extended')
        self.objects_listbox.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.objects_listbox.bind("<BackSpace>", self.__del_selected_from_listbox)
        self.set_1_check = tk.Checkbutton(self.checkbutton_frame, variable=self.set_1, text="Delete existing temporary files before processing and start with new raw processing")
        self.set_1_check.pack(side="top", padx=10, pady=10, anchor="nw")
        self.set_2_check = tk.Checkbutton(self.checkbutton_frame, variable=self.set_2, text="To leave all the temporary files after processing finish")
        self.set_2_check.pack(side="top", padx=10, pady=10, anchor="nw")
        self.add_button = tk.Button(self.checkbutton_frame, text="Add item", command=lambda: self.__add_item_to_listbox(event=None))
        self.add_button.pack(side="top", padx=10, pady=10, anchor="w")
        self.new_item_field = tk.Entry(self.checkbutton_frame)
        self.new_item_field.bind("<Return>", self.__add_item_to_listbox)
        self.new_item_field.pack(side="top", padx=10, pady=10, anchor="w")

    def __add_item_to_listbox(self, event):
        item_list = self.new_item_field.get().split()
        for item in item_list:
            self.objects_listbox.insert('end', item)
            self.objects_list.append(item)
        self.new_item_field.delete(0, 'end')

    def __del_selected_from_listbox(self, event):
        select = list(self.objects_listbox.curselection())
        select.reverse()
        for i in select:
            self.objects_listbox.delete(i)
            self.objects_list.pop(i)

    def __set_run_frame(self):
        self.run_button = tk.Button(self.run_frame, text="Run", bg="red", command=lambda: self.__run_frame_update())
        self.run_button.pack(side="left", padx=10, pady=10)

    def __run_frame_update(self):
        self.operation_numerator_label = tk.Label(self.run_frame, text="Operation")
        self.operation_numerator_label.pack(side="left", padx=10, pady=10)
        self.operation_numerator = tk.Label(self.run_frame, text="0/0")
        self.operation_numerator.pack(side="left", padx=10, pady=10)
        self.operation_name = tk.Label(self.run_frame, text="Operation Name")
        self.operation_name.pack(side="left", padx=10, pady=10)
        self.stop_btn = tk.Button(self.run_frame, text="Stop", bg='red', command=lambda: self.__stop())
        self.stop_btn.pack(side='left', fill='x', padx=10, pady=10)
        self.START_TIME = time.time()
        self.progressbar_value_var = tk.IntVar()
        self.progressbar_value_var.set(0)
        self.progressbar =  ttk.Progressbar(self.run_frame, orient="horizontal", variable=self.progressbar_value_var, maximum=100)
        self.progressbar.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        self.percents = tk.Label(self.run_frame, text=f'{self.progressbar_value_var.get()} %')
        self.percents.pack(side="left", padx=10, pady=10)
        self.time_label = tk.Label(self.run_frame, text=time_check(self.START_TIME))
        self.time_label.pack(side="left", padx=10, pady=10)
        self.run_button.configure(state='disabled', bg='gray')
        self.input_card_path_button.configure(state='disabled')
        for child in chain(self.object_list_frame.winfo_children(), self.checkbutton_frame.winfo_children()):
            child.configure(state='disabled')
        for child in self.head_frame.winfo_children():
                child.configure(state='disabled')
        self.__run()

    def __run(self):
        ManticoreController(self.set_1.get(), self.set_2.get(), self.objects_list, self.run_frame,
                            self.operation_name, self.operation_numerator, self.progressbar_value_var,
                            self.percents, self.START_TIME, self.time_label, self.input_card_path,
                            self.data_directory_path, self.temp_directory_path)

    def __stop(self):
        if askyesno(title="Processing stop!", message="Do you really want to stop the processing? All created temporary files will NOT be deleted."):
            self.__stop_processing()
            self.run_frame.destroy()
            self.run_frame = tk.LabelFrame(self.main_frame, text="Run", bd=2)
            self.run_frame.pack(fill="both", expand=False, padx=10, pady=10)
            for child in self.head_frame.winfo_children():
                child.configure(state='normal')
            self.__set_run_frame()
            self.__frame_activator(from_manual_to_automatic=0)

    def __stop_processing(self):
        pass

    def __frame_activator(self, from_manual_to_automatic=True):
        if from_manual_to_automatic:
            self.input_card_path_button.configure(state='normal')
            for child in chain(self.object_list_frame.winfo_children(), self.checkbutton_frame.winfo_children()):
                child.configure(state='disabled')
        elif not from_manual_to_automatic:
            self.input_card_path_button.configure(state='disabled')
            for child in chain(self.object_list_frame.winfo_children(), self.checkbutton_frame.winfo_children()):
                child.configure(state='normal')

    def __set_path(self, path_field):
        if path_field['state'] == 'disabled':
            path_field.configure(state='normal')
            path_field.update()

    def __change_input_card_path(self, event):
        self.input_card_path = self.input_card_path_field.get()
        self.input_card_path_field.configure(state='disabled')
        self.input_card_path_field.update()

    def __change_data_directory_path(self, event):
        self.data_directory_path = self.data_directory_path_field.get()
        self.data_directory_path_field.configure(state='disabled')
        self.data_directory_path_field.update()

    def __change_temp_directory_path(self, event):
        self.temp_directory_path = self.temp_directory_path_field.get()
        self.temp_directory_path_field.configure(state='disabled')
        self.temp_directory_path_field.update()

    def __get_pathes(self):
        if sys.platform.startswith('win32'):
            with open(os.getcwd() + "\Manticore_3.14\\data_directory.conf", "r") as dir_config:
                data_directory = dir_config.readline().strip()
            with open(os.getcwd() + "\Manticore_3.14\\temporary_files_directory.conf", "r") as temp_dir_config:
                temp_files_directory = temp_dir_config.readline().strip()
            return os.getcwd() + "\Manticore_3.14\\input_card.conf", data_directory, temp_files_directory
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            with open(os.getcwd() + "/data_directory.conf", "r") as dir_config:
                data_directory = dir_config.readline().strip()
            with open(os.getcwd() + "/temporary_files_directory.conf", "r") as temp_dir_config:
                temp_files_directory = temp_dir_config.readline().strip()
            return os.getcwd() + "/input_card.conf", data_directory, temp_files_directory


class ManticoreController:
    def __init__(self, set_1: int, set_2: int, set_3: list, run_frame, operation_name_label,
                 operation_numerator_label, progressbar_value_var, percent_label, start_time,
                 time_from_start_label, input_card_path, data_dir_path, temp_dir_path):

        self.need_to_remove_all_temp_files = set_1
        self.need_to_leave_temp_files_after_processing = set_2
        self.list_of_objects = set_3
        self.run_frame_parent = run_frame
        self.operation_name_parent_label = operation_name_label
        self.operation_numerator_parent_label = operation_numerator_label
        self.progressbar_parent_value_var = progressbar_value_var
        self.percent_parent_value_label = percent_label
        self.start_time = start_time
        self.time_from_start_parent_label = time_from_start_label
        self.input_card_path = input_card_path
        self.data_directory_path = data_dir_path
        self.temp_directory_path = temp_dir_path
        self.files_list = []

        if self.need_to_remove_all_temp_files: self.__preset_1_execution()

        self.__parser()

    def __preset_1_execution(self):
        self.operation_name_parent_label.configure(text="Deleting old temporary files...")
        self.operation_numerator_parent_label.configure(text=f'1/10')
        if not os.path.exists(self.temp_directory_path):
            pass
        else:
            temp_folder_contain = os.listdir(self.temp_directory_path)
            temp_folder_size = len(temp_folder_contain)
            for i, file in enumerate(temp_folder_contain):
                self.progressbar_parent_value_var.set(i*100//temp_folder_size)
                self.percent_parent_value_label.configure(text=f'{self.progressbar_parent_value_var.get()} %')
                self.time_from_start_parent_label.configure(text=time_check(self.start_time))
                self.run_frame_parent.update()
                os.remove(file)

    def __parser(self):
        if sys.platform.startswith('win32'):
            for i, item in enumerate(self.list_of_objects):
                self.list_of_objects[i] = item.replace("/", "\\")


        # manticore_parser.parser(SET_3, START_TIME)
        # manticore_tools.is_preprocessing_needed(SET_1, START_TIME)

    def dd():
        pass

if __name__ == "__main__":
    ManticoreGUI().mainloop()