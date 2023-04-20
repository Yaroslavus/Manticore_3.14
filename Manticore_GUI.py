import tkinter as tk
#from datetime import datetime
#from tkinter.messagebox import askyesno
#import webbrowser
#import tkinter.font as tkFont
import os
from itertools import chain
from sys import platform


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

    def __set_automatic_settings_frame(self):
        self.input_card_path_label = tk.Label(self.automatic_settings_frame, text="Path to input card:")
        self.input_card_path_label.pack(side="left", padx=10, pady=10)
        self.input_card_path_field = tk.Entry(self.automatic_settings_frame)
        self.input_card_path_field.insert('end', self.input_card_path)
        self.input_card_path_field.pack(side="left", padx=10, pady=10)
        self.input_card_path_field.bind("<Return>", self.change_input_card_path)
        self.input_card_path_button = tk.Button(self.automatic_settings_frame, text="Change path", command=lambda: self.set_path(self.input_card_path_field))
        self.input_card_path_button.pack(side="left", padx=10, pady=10)
        self.data_directory_path_label = tk.Label(self.automatic_settings_frame, text="Data directory:")
        self.data_directory_path_label.pack(side="left", padx=10, pady=10)
        self.data_directory_path_field = tk.Entry(self.automatic_settings_frame)
        self.data_directory_path_field.insert('end', self.data_directory_path)
        self.data_directory_path_field.pack(side="left", padx=10, pady=10)
        self.data_directory_path_field.bind("<Return>", self.change_data_directory_path)
        self.data_directory_path_button = tk.Button(self.automatic_settings_frame, text="Change path", command=lambda: self.set_path(self.data_directory_path_field))
        self.data_directory_path_button.pack(side="left", padx=10, pady=10)
        self.temp_directory_path_label = tk.Label(self.automatic_settings_frame, text="Directory for temporary files:")
        self.temp_directory_path_label.pack(side="left", padx=10, pady=10)
        self.temp_directory_path_field = tk.Entry(self.automatic_settings_frame)
        self.temp_directory_path_field.insert('end', self.temp_directory_path)
        self.temp_directory_path_field.pack(side="left", padx=10, pady=10)
        self.temp_directory_path_field.bind("<Return>", self.change_temp_directory_path)
        self.temp_directory_path_button = tk.Button(self.automatic_settings_frame, text="Change path", command=lambda: self.set_path(self.temp_directory_path_field))
        self.temp_directory_path_button.pack(side="left", padx=10, pady=10)

    def __set_manual_settings_frame(self):
        self.object_list_frame = tk.LabelFrame(self.manual_settings_frame, text="List of objects to process", bd=2)
        self.object_list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.presets_frame = tk.LabelFrame(self.manual_settings_frame, text="Presets", bd=2)
        self.presets_frame.pack(side="left", padx=10, pady=10, anchor="n")

        self.checkbutton_frame = tk.Frame(self.presets_frame, bd=2)
        self.checkbutton_frame.pack(side="top", padx=10, pady=10, anchor="nw")

        self.objects_listbox = tk.Listbox(self.object_list_frame, selectmode='extended', )
        self.objects_listbox.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.set_1 = tk.Checkbutton(self.checkbutton_frame, text="Delete existing temporary files before processing and start with new raw processing")
        self.set_1.pack(side="top", padx=10, pady=10, anchor="nw")
        self.set_2 = tk.Checkbutton(self.checkbutton_frame, text="To leave all the temporary files after processing finish")
        self.set_2.pack(side="top", padx=10, pady=10, anchor="nw")

        self.data_dir_frame = tk.Frame(self.presets_frame)
        self.data_dir_frame.pack(side="top", padx=10, pady=10, anchor="nw")

        for c in range(3): self.data_dir_frame.columnconfigure(index=c, weight=1, uniform="group1")

        self.data_directory_path_label = tk.Label(self.data_dir_frame, text="Data directory:")
#        self.data_directory_path_label.pack(side="left", padx=10, pady=10)
        self.data_directory_path_field = tk.Entry(self.data_dir_frame)
        self.data_directory_path_field.insert('end', self.data_directory_path)
#        self.data_directory_path_field.pack(side="left", padx=10, pady=10)
        self.data_directory_path_field.bind("<Return>", self.change_data_directory_path)
        self.data_directory_path_button = tk.Button(self.data_dir_frame, text="Change path", command=lambda: self.set_path(self.data_directory_path_field))
#        self.data_directory_path_button.pack(side="left", padx=10, pady=10)

        self.data_directory_path_label.grid(row=0, column=0)
        self.data_directory_path_field.grid(row=0, column=1)
        self.data_directory_path_button.grid(row=0, column=2)


        self.temp_dir_frame = tk.Frame(self.presets_frame)
        self.temp_dir_frame.pack(side="top", padx=10, pady=10, anchor="nw")

        for c in range(3): self.temp_dir_frame.columnconfigure(index=c, weight=1, uniform="group1")

        self.temp_directory_path_label = tk.Label(self.temp_dir_frame, text="Directory for temporary files:")
#        self.temp_directory_path_label.pack(side="left", padx=10, pady=10)
        self.temp_directory_path_field = tk.Entry(self.temp_dir_frame)
        self.temp_directory_path_field.insert('end', self.temp_directory_path)
#        self.temp_directory_path_field.pack(side="left", padx=10, pady=10)
        self.temp_directory_path_field.bind("<Return>", self.change_temp_directory_path)
        self.temp_directory_path_button = tk.Button(self.temp_dir_frame, text="Change path", command=lambda: self.set_path(self.temp_directory_path_field))
#        self.temp_directory_path_button.pack(side="left", padx=10, pady=10)

        self.temp_directory_path_label.grid(row=0, column=0)
        self.temp_directory_path_field.grid(row=0, column=1)
        self.temp_directory_path_button.grid(row=0, column=2)

    def __set_run_frame(self):
        self.run_button = tk.Button(self.run_frame, text="Run", bg="red", command=lambda: self.run())
        self.run_button.pack(side="left", padx=10, pady=10)

    def run(self):
        pass

    def frame_activator(self, from_manual_to_automatic=True):
        if from_manual_to_automatic:
            for child in self.automatic_settings_frame.winfo_children():
                child.configure(state='normal')
            for child in chain(self.object_list_frame.winfo_children(), self.checkbutton_frame.winfo_children(), self.data_dir_frame.winfo_children(), self.temp_dir_frame.winfo_children()):
                child.configure(state='disabled')
        elif not from_manual_to_automatic:
            for child in self.automatic_settings_frame.winfo_children():
                child.configure(state='disabled')
            for child in chain(self.object_list_frame.winfo_children(), self.checkbutton_frame.winfo_children(), self.data_dir_frame.winfo_children(), self.temp_dir_frame.winfo_children()):
                child.configure(state='normal')

    def set_path(self, path_field):
        if path_field['state'] == 'disabled':
            path_field.configure(state='normal')
            path_field.update()
        elif path_field['state'] == 'normal':
            path_field.configure(state='disabled')
            path_field.update()

    def change_input_card_path(self, event):
        global input_card_path
        input_card_path = self.input_card_path_field.get()
        self.input_card_path_field.configure(state='disabled')
        self.input_card_path_field.update()

    def change_data_directory_path(self, event):
        global data_directory_path
        data_directory_path = self.data_directory_path_field.get()
        self.data_directory_path_field.configure(state='disabled')
        self.data_directory_path_field.update()

    def change_temp_directory_path(self, event):
        global temp_directory_path
        temp_directory_path = self.temp_directory_path_field.get()
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