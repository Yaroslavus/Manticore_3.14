import tkinter as tk
from tkinter import ttk
import time
import os
from itertools import chain
from tkinter.messagebox import askyesno
import pathlib
from tqdm import tqdm
import struct
import numpy as np
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class Settings:
    data_path: pathlib.WindowsPath = None
    temp_path: pathlib.WindowsPath = None
    create_stat_ped_file: int = 1
    create_dyn_ped_file: int = 1
    calculate_clean_ampls: int = 1
    calculate_stat_ampls: int = 1
    calculate_dyn_ampls: int = 1
    object_list: list = field(default_factory=list)
    all_data: int = 0


@dataclass
class Day:
    name: str = None
    tails_dict: dict = field(default_factory=dict)          # dict = {str: list[min_event, max_event]}
    tails_list: list = field(default_factory=list)
    tails_number: int = 0
    path: pathlib.WindowsPath = None                        # str <----> pathlib.WindowsPath object
    files_list: list = field(default_factory=list)          # list[str, str...str]. Items are "stems" - file names without path and suffix

    stat_peds_average: list = field(default_factory=list)   # after calculating and reshaping - numpy array with
    stat_peds_sigma: list = field(default_factory=list)     # shape = (tails_number, BSM_number, number_of_codes)
    stat_ignore_pack: list = field(default_factory=list)    # each element is float

    dyn_peds_average: list = field(default_factory=list)    # after calculating and reshaping - numpy array with
    dyn_peds_sigma: list = field(default_factory=list)      # shape = (tails_number, BSM_number, number_of_codes)
    dyn_ignore_pack: list = field(default_factory=list)     # each element is float


@dataclass(frozen=True)
class Constants:
    number_of_codes: int = 64
    chunk_size: int = 156
    codes_beginning_byte: int = 24
    codes_ending_byte: int = 152
    number_1_beginning_byte = 4
    number_1_ending_byte = 8
    maroc_number_byte = 20
    channel_threshold = 3000
    test_pedestal_bunch_size = 100
    IACT_float: np.dtype = np.float32 # np.float16, np.float32 (default in OS and preferable here), np.float64, np.float128, etc.
    IACT_ignore_int: np.dtype = np.uint8 # 0...255
    IACT_codes_int: np.dtype = np.int16 # -32768...32767
    BSM_number = 22
    BSM_list: list = field(default_factory=lambda: [f'BSM{"0"*(2-len(str(i)))}{i}' for i in range(1, Constants.BSM_number + 1)])


class ManticoreTools:
    def read_input_card() -> Settings:
        script_directory = pathlib.Path(__file__).parent
        input_card_path = script_directory.joinpath('input_card.conf')
        with open(input_card_path, "r") as input_card:
            settings = [line.strip() for line in input_card.readlines() if not line.startswith('#')]
        set_all_data = 1 if settings[7] == "a" else 0
        return Settings(data_path=pathlib.Path(settings[0]), temp_path=pathlib.Path(settings[1]),
                        create_stat_ped_file=int(settings[2]), create_dyn_ped_file=int(settings[3]),
                        calculate_clean_ampls=int(settings[4]), calculate_stat_ampls=int(settings[5]),
                        calculate_dyn_ampls=int(settings[6]), object_list=settings[7].split(),
                        all_data=set_all_data)

    def time_check(start_time: float) -> str:
        current_time = time.time() - start_time
        return f'[ {int(current_time//60//60):2} h {int(current_time//60%60):2} m {int(current_time%60):2} s ]'


class LauncherManipulators:
    def parser_gui_outside_manipulator(gui) -> enumerate:
        gui.operation_name_parent_label.configure(text="Parsing input elements pathes")
        gui.operation_numerator_parent_label.configure(text=f'1/5')
        return enumerate(gui.list_of_objects)

    def parser_gui_inside_manipulator(gui, i: int) -> None:
        gui.progressbar_parent_value_var.set((i+1)*100//gui.list_of_objects_size)
        gui.percent_parent_value_label.configure(text=f'{gui.progressbar_parent_value_var.get()} %')
        gui.time_from_start_parent_label.configure(text=ManticoreTools.time_check(gui.start_time))
        gui.run_frame_parent.update()

    def parser_console_outside_manipulator(console) -> enumerate:
        return enumerate(tqdm(console.list_of_objects, desc="1/5 Parsing input elements pathes"))

    def parser_console_inside_manipulator(console, i: int) -> None:
        pass


    def static_pedestals_gui_outside_manipulator(gui, day_name: str, list_of_ped_files: list) -> enumerate:
        gui.operation_name_parent_label.configure(text=f'{day_name}: Making static pedestals')
        gui.operation_numerator_parent_label.configure(text=f'2/5')
        return enumerate(list_of_ped_files)

    def static_pedestals_gui_inside_manipulator(gui, i: int, list_of_ped_files_size: int) -> None:
        gui.progressbar_parent_value_var.set((i+1)*100//list_of_ped_files_size)
        gui.percent_parent_value_label.configure(text=f'{gui.progressbar_parent_value_var.get()} %')
        gui.time_from_start_parent_label.configure(text=ManticoreTools.time_check(gui.start_time))
        gui.run_frame_parent.update()

    def static_pedestals_console_outside_manipulator(console, day_name: str, list_of_ped_files: list) -> enumerate:
        return enumerate(tqdm(list_of_ped_files, desc=f'{day_name}: 2/5 Making static pedestals'))

    def static_pedestals_console_inside_manipulator(console, i: int, list_of_ped_files: list) -> None:
        pass


    def dynamic_pedestals_gui_outside_manipulator(gui, day_name: str, list_of_ped_files: list) -> enumerate:
        gui.operation_name_parent_label.configure(text=f'{day_name}: Making dynamic pedestals')
        gui.operation_numerator_parent_label.configure(text=f'3/5')
        return enumerate(list_of_ped_files)

    def dynamic_pedestals_gui_inside_manipulator(gui, i: int, list_of_ped_files_size: list) -> None:
        gui.progressbar_parent_value_var.set((i+1)*100//list_of_ped_files_size)
        gui.percent_parent_value_label.configure(text=f'{gui.progressbar_parent_value_var.get()} %')
        gui.time_from_start_parent_label.configure(text=ManticoreTools.time_check(gui.start_time))
        gui.run_frame_parent.update()

    def dynamic_pedestals_console_outside_manipulator(console, day_name: str, list_of_tails: list) -> enumerate:
        return enumerate(tqdm(list_of_tails, desc=f'{day_name}: 3/5 Making dynamic pedestals'))

    def dynamic_pedestals_console_inside_manipulator(console, i: int, list_of_tails: list) -> None:
        pass


    def tails_gui_outside_manipulator(gui, day_name: str, list_of_ped_files: list) -> enumerate:
        gui.operation_name_parent_label.configure(text=f'{day_name}: Filling tails dictionary')
        gui.operation_numerator_parent_label.configure(text=f'4/5')
        return enumerate(list_of_ped_files)

    def tails_gui_inside_manipulator(gui, i: int, list_of_ped_files_size: list) -> None:
        gui.progressbar_parent_value_var.set((i+1)*100//list_of_ped_files_size)
        gui.percent_parent_value_label.configure(text=f'{gui.progressbar_parent_value_var.get()} %')
        gui.time_from_start_parent_label.configure(text=ManticoreTools.time_check(gui.start_time))
        gui.run_frame_parent.update()

    def tails_console_outside_manipulator(console, day_name: str, list_of_tails: list) -> enumerate:
        return enumerate(tqdm(list_of_tails, desc=f'{day_name}: 4/5 Filling tails dictionary'))

    def tails_console_inside_manipulator(console, i: int, list_of_tails: list) -> None:
        pass


    def amplitudes_gui_outside_manipulator(gui, day_name: str, tails_list: list) -> enumerate:
        gui.operation_name_parent_label.configure(text=f'{day_name}: Making events amplitudes')
        gui.operation_numerator_parent_label.configure(text=f'5/5')
        # first_tail = list(tails_dict.keys())[0]
        # last_tail = list(tails_dict.keys())[-1]
        # return range(tails_dict[first_tail][0], tails_dict[last_tail][1])
        return enumerate(tails_list)

    def amplitudes_gui_inside_manipulator(gui, i: int, list_of_ped_files_size: list) -> None:
        gui.progressbar_parent_value_var.set((i+1)*100//list_of_ped_files_size)
        gui.percent_parent_value_label.configure(text=f'{gui.progressbar_parent_value_var.get()} %')
        gui.time_from_start_parent_label.configure(text=ManticoreTools.time_check(gui.start_time))
        gui.run_frame_parent.update()

    def amplitudes_console_outside_manipulator(console, day_name: str, tails_list: list) -> enumerate:
        # first_tail = list(tails_dict.keys())[0]
        # last_tail = list(tails_dict.keys())[-1]
        # return tqdm(range(tails_dict[first_tail][0], tails_dict[last_tail][1]),
        #             desc=f'{day_name}: 5/5 Making events amplitudes...')
        return enumerate(tqdm(tails_list, desc=f'{day_name}: 5/5 Making events amplitudes'))

    def amplitudes_console_inside_manipulator(console, i: int, list_of_tails: list) -> None:
        pass


class ManticoreConsole:
    def __init__(self):
        self.settings = ManticoreTools.read_input_card()
        self.START_TIME = time.time()
        print("Launching Manticore 3.14 Controller...")
        ManticoreController(self, "console")


class ManticoreGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Manticore 3.14")
        self.settings = ManticoreTools.read_input_card()
        self.input_card_path = pathlib.Path(__file__).parent
        self.data_path = self.settings.data_path
        self.temp_path = self.settings.temp_path
        self.object_list = []
        self.set_create_stat_ped_file = tk.IntVar()
        self.set_create_dyn_ped_file = tk.IntVar()
        self.set_calculate_clean_ampls = tk.IntVar()
        self.set_calculate_stat_ampls = tk.IntVar()
        self.set_calculate_dyn_ampls = tk.IntVar()
        self.set_all_data_var = tk.IntVar()
        self.set_all_data = self.settings.all_data
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
        self.__frame_activator(from_manual_to_automatic=False)

    def __set_head_frame(self):
        self.settings_choose_var = tk.BooleanVar()
        self.settings_choose_var.set(1)
        automatic_settings_radiobutton = tk.Radiobutton(self.head_frame,
                                                        text='Input card',
                                                        variable=self.settings_choose_var,
                                                        value=False,
                                                        command=lambda: self.__frame_activator(
                                                            from_manual_to_automatic=True)
                                                        )
        manual_settings_radiobutton = tk.Radiobutton(self.head_frame,
                                                     text='Set manually',
                                                     variable=self.settings_choose_var,
                                                     value=True,
                                                     command=lambda: self.__frame_activator(
                                                         from_manual_to_automatic=False)
                                                     )
        automatic_settings_radiobutton.pack(side="left", padx=10, pady=10)
        manual_settings_radiobutton.pack(side="left", padx=10, pady=10)

        self.data_path_label = tk.Label(self.head_frame, text="Data directory:")
        self.data_path_label.pack(side="left", padx=10, pady=10)
        self.data_path_field = tk.Entry(self.head_frame, width=30)
        self.data_path_field.insert('end', self.data_path)
        self.data_path_field.configure(state='disabled')
        self.data_path_field.pack(side="left", padx=5, pady=10)
        self.data_path_field.bind("<Return>", self.__change_data_path)
        self.data_path_button = tk.Button(self.head_frame,
                                                    text="Change path",
                                                    command=lambda: self.__set_path(
                                                        self.data_path_field)
                                                    )
        self.data_path_button.pack(side="left", padx=5, pady=10)

        self.temp_path_label = tk.Label(self.head_frame,
                                                  text="Temporary files directory:")
        self.temp_path_label.pack(side="left", padx=15, pady=10)
        self.temp_path_field = tk.Entry(self.head_frame, width=30)
        self.temp_path_field.insert('end', self.temp_path)
        self.temp_path_field.configure(state='disabled')
        self.temp_path_field.pack(side="left", padx=5, pady=10)
        self.temp_path_field.bind("<Return>", self.__change_temp_path)
        self.temp_path_button = tk.Button(self.head_frame,
                                                    text="Change path",
                                                    command=lambda: self.__set_path(
                                                        self.temp_path_field)
                                                    )
        self.temp_path_button.pack(side="left", padx=5, pady=10)

    def __set_automatic_settings_frame(self):
        self.input_card_path_label = tk.Label(self.automatic_settings_frame,
                                              text="Path to input card:")
        self.input_card_path_label.pack(side="left", padx=10, pady=10)
        self.input_card_path_field = tk.Entry(self.automatic_settings_frame, width=60)
        self.input_card_path_field.insert('end', self.input_card_path)
        self.input_card_path_field.configure(state='disabled')
        self.input_card_path_field.pack(side="left", padx=10, pady=10)
        self.input_card_path_field.bind("<Return>", self.__change_input_card_path)
        self.input_card_path_button = tk.Button(self.automatic_settings_frame,
                                                text="Change path",
                                                command=lambda: self.__set_path(
                                                    self.input_card_path_field)
                                                )
        self.input_card_path_button.pack(side="left", padx=10, pady=10)

    def __set_manual_settings_frame(self):
        self.object_list_frame = tk.LabelFrame(self.manual_settings_frame,
                                               text="List of objects to process", bd=2)
        self.object_list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.presets_frame = tk.LabelFrame(self.manual_settings_frame, text="Presets", bd=2)
        self.presets_frame.pack(side="left", padx=10, pady=10, anchor="n")
        self.checkbutton_frame = tk.Frame(self.presets_frame, bd=2)
        self.checkbutton_frame.pack(side="top", padx=10, pady=10, anchor="nw")
        self.objects_var = tk.StringVar(value=self.object_list)
        self.object_listbox = tk.Listbox(self.object_list_frame,
                                          listvariable=self.objects_var,
                                          selectmode='extended')
        self.object_listbox.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.object_listbox.bind("<BackSpace>", self.__del_selected_from_listbox)
        self.set_1_check = tk.Checkbutton(
            self.checkbutton_frame, variable=self.set_create_stat_ped_file,
            text="Create file with static pedestals")
        self.set_1_check.pack(side="top", padx=10, pady=10, anchor="nw")
        self.set_2_check = tk.Checkbutton(
            self.checkbutton_frame, variable=self.set_create_dyn_ped_file,
            text="Create file with dynamic pedestals")
        self.set_2_check.pack(side="top", padx=10, pady=10, anchor="nw")
        self.set_3_check = tk.Checkbutton(
            self.checkbutton_frame, variable=self.set_calculate_clean_ampls,
            text="Create file with clean amplitudes")
        self.set_3_check.pack(side="top", padx=10, pady=10, anchor="nw")
        self.set_4_check = tk.Checkbutton(
            self.checkbutton_frame, variable=self.set_calculate_stat_ampls,
            text="Create file with amplitudes normalized for static pedestals")
        self.set_4_check.pack(side="top", padx=10, pady=10, anchor="nw")
        self.set_5_check = tk.Checkbutton(
            self.checkbutton_frame, variable=self.set_calculate_dyn_ampls,
            text="Create file with amplitudes normalized for dynamic pedestals")
        self.set_5_check.pack(side="top", padx=10, pady=10, anchor="nw")
        self.set_all = tk.Checkbutton(
            self.checkbutton_frame, variable=self.set_all_data_var,
            text="Process all data", command=self.__choose_all_data)
        self.set_all.pack(side="top", padx=10, pady=25, anchor="nw")
        self.add_button = tk.Button(self.checkbutton_frame, text="Add item",
                                    command=lambda: self.__add_item_to_listbox(event=None)
                                    )
        self.add_button.pack(side="top", padx=10, pady=10, anchor="w")
        self.new_item_field = tk.Entry(self.checkbutton_frame)
        self.new_item_field.bind("<Return>", self.__add_item_to_listbox)
        self.new_item_field.pack(side="top", padx=10, pady=10, anchor="w")

    def __choose_all_data(self):
        if self.add_button['state'] == 'normal':
            self.add_button.configure(state='disabled')
            self.new_item_field.configure(state='disabled')
            self.object_listbox.configure(state='disabled')
        else:
            self.add_button.configure(state='normal')
            self.new_item_field.configure(state='normal')
            self.object_listbox.configure(state='normal')

    def __add_item_to_listbox(self, event):
        item_list = self.new_item_field.get().split()
        for item in item_list:
            self.object_listbox.insert('end', item)
            self.object_list.append(item)
        self.new_item_field.delete(0, 'end')

    def __del_selected_from_listbox(self, event):
        select = list(self.object_listbox.curselection())
        select.reverse()
        for i in select:
            self.object_listbox.delete(i)
            self.object_list.pop(i)

    def __set_run_frame(self):
        self.run_button = tk.Button(
            self.run_frame, text="Run", bg="red", command=lambda: self.__run_frame_update())
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
        self.progressbar =  ttk.Progressbar(self.run_frame, orient="horizontal",
                                            variable=self.progressbar_value_var, maximum=100)
        self.progressbar.pack(side='left', fill='x', expand=True, padx=10, pady=10)
        self.percents = tk.Label(self.run_frame, text=f'{self.progressbar_value_var.get()} %')
        self.percents.pack(side="left", padx=10, pady=10)
        self.time_label = tk.Label(self.run_frame, text=ManticoreTools.time_check(self.START_TIME))
        self.time_label.pack(side="left", padx=10, pady=10)
        self.run_button.configure(state='disabled', bg='gray')
        self.input_card_path_button.configure(state='disabled')
        for child in chain(self.object_list_frame.winfo_children(), self.checkbutton_frame.winfo_children()):
            child.configure(state='disabled')
        for child in self.head_frame.winfo_children():
                child.configure(state='disabled')
        self.__run()

    def __run(self):
        self.set_all_data = 1 if (self.object_list == ["a"] or self.set_all_data_var.get()) else 0
        self.settings = Settings(data_path=self.data_path, temp_path=self.temp_path,
                                 create_stat_ped_file=self.set_create_stat_ped_file.get(),
                                 create_dyn_ped_file=self.set_create_dyn_ped_file.get(),
                                 calculate_clean_ampls=self.set_calculate_clean_ampls.get(),
                                 calculate_stat_ampls=self.set_calculate_stat_ampls.get(),
                                 calculate_dyn_ampls=self.set_calculate_dyn_ampls.get(),
                                 object_list=self.object_list, all_data=self.set_all_data)
        ManticoreController(self, "gui")

    def __stop(self):
        if askyesno(title="Processing stop!",
                    message="Do you really want to stop the processing? All created files will NOT be deleted."):
            self.__stop_processing()
            self.run_frame.destroy()
            self.run_frame = tk.LabelFrame(self.main_frame, text="Run", bd=2)
            self.run_frame.pack(fill="both", expand=False, padx=10, pady=10)
            for child in self.head_frame.winfo_children():
                if child not in [self.data_path_field, self.temp_path_field]:
                    child.configure(state='normal')
            self.__set_run_frame()
            self.__frame_activator(from_manual_to_automatic=False)

    def __stop_processing(self):
        pass

    def __frame_activator(self, from_manual_to_automatic: bool = True):
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
        self.input_card_path = pathlib.Path(self.input_card_path_field.get())
        self.input_card_path_field.configure(state='disabled')
        self.input_card_path_field.update()

    def __change_data_path(self, event):
        self.data_path = pathlib.Path(self.data_path_field.get())
        self.data_path_field.configure(state='disabled')
        self.data_path_field.update()

    def __change_temp_path(self, event):
        self.temp_path = pathlib.Path(self.temp_path_field.get())
        self.temp_path_field.configure(state='disabled')
        self.temp_path_field.update()


class ManticoreController:
    def __init__(self, launcher, launcher_type: str):
        self.start_time = launcher.START_TIME
        self.settings = launcher.settings
        self.files_list = []    # pure names without suffixes, not pathes
        # self.set_all_data = launcher.set_all_data
        self.constants = Constants()
        if launcher_type == "gui":
            self.run_frame_parent = launcher.run_frame
            self.operation_name_parent_label = launcher.operation_name
            self.operation_numerator_parent_label = launcher.operation_numerator
            self.progressbar_parent_value_var = launcher.progressbar_value_var
            self.percent_parent_value_label = launcher.percents
            self.time_from_start_parent_label = launcher.time_label
        if self.settings.all_data:
            self.list_of_objects = [Day(name=day, path=self.settings.data_path.joinpath(day)) for day in self.settings.data_path.iterdir() if os.path.isdir(day)]
        else:
            self.list_of_objects = [Day(name=day, path=self.settings.data_path.joinpath(day)) for day in self.settings.object_list if os.path.isdir(self.settings.data_path.joinpath(day))]
        self.list_of_objects_size = len(self.list_of_objects)
        self.start_engine(launcher_type)

    def start_engine(self, launcher_type):
        integer_settings = [self.settings.create_stat_ped_file,
                            self.settings.create_dyn_ped_file,
                            self.settings.calculate_clean_ampls,
                            self.settings.calculate_stat_ampls,
                            self.settings.calculate_dyn_ampls]
        if launcher_type == "gui":
            if any(integer_settings):
                ManticoreEngine.parser(self, [LauncherManipulators.parser_gui_outside_manipulator,
                                            LauncherManipulators.parser_gui_inside_manipulator])
                for i in range(self.list_of_objects_size):
                    if any(self.settings.create_stat_ped_file,
                           self.settings.calculate_stat_ampls):
                        ManticoreEngine.static_pedestals(self, i,
                            [LauncherManipulators.static_pedestals_gui_outside_manipulator,
                            LauncherManipulators.static_pedestals_gui_inside_manipulator],
                            record_flag=bool(self.settings.create_stat_ped_file)
                            )
                    if any([self.settings.create_dyn_ped_file,
                           self.settings.calculate_dyn_ampls]):
                        ManticoreEngine.dynamic_pedestals(self, i,
                            [LauncherManipulators.dynamic_pedestals_gui_outside_manipulator,
                            LauncherManipulators.dynamic_pedestals_gui_inside_manipulator],
                            record_flag=bool(self.settings.create_dyn_ped_file)
                            )
                    if any([self.settings.calculate_stat_ampls,
                           self.settings.calculate_dyn_ampls,
                           self.settings.calculate_clean_ampls]):
                        ManticoreEngine.fill_tails_dict(
                            self, i,
                            [LauncherManipulators.tails_gui_outside_manipulator,
                            LauncherManipulators.tails_gui_inside_manipulator]
                            )
                        ped_flag = 0
                        if self.settings.calculate_clean_ampls:
                            ped_flag += 1
                            # take part in [1, 3, 5, 7] => bin =>
                            # 1, 11, 101, 111 - we take [-1] digit
                        if self.settings.calculate_stat_ampls:
                            ped_flag += 2
                            # take part in [2, 3, 6, 7] => bin =>
                            # 10, 110, 11, 111 - we take [-2] digit
                        if self.settings.calculate_dyn_ampls:
                            ped_flag += 4
                            # take part in [4, 5, 6, 7] => bin =>
                            # 100, 110, 101, 111 - we take [-3] digit
                        ManticoreEngine.amplitudes_to_file(
                            self, i,
                            [LauncherManipulators.amplitudes_gui_outside_manipulator,
                            LauncherManipulators.amplitudes_gui_inside_manipulator],
                            ped_flag=ped_flag
                            )
        elif launcher_type == "console":
            if any(integer_settings):
                ManticoreEngine.parser(self, [LauncherManipulators.parser_console_outside_manipulator,
                                            LauncherManipulators.parser_console_inside_manipulator])
                for i in range(self.list_of_objects_size):
                    if any([self.settings.create_stat_ped_file,
                           self.settings.calculate_stat_ampls]):
                        ManticoreEngine.static_pedestals(self, i,
                            [LauncherManipulators.static_pedestals_console_outside_manipulator,
                            LauncherManipulators.static_pedestals_console_inside_manipulator],
                            record_flag=bool(self.settings.create_stat_ped_file)
                            )
                    if any([self.settings.create_dyn_ped_file,
                           self.settings.calculate_dyn_ampls]):
                        ManticoreEngine.dynamic_pedestals(self, i,
                            [LauncherManipulators.dynamic_pedestals_console_outside_manipulator,
                            LauncherManipulators.dynamic_pedestals_console_inside_manipulator],
                            record_flag=bool(self.settings.create_dyn_ped_file)
                            )
                    if any([self.settings.calculate_stat_ampls,
                           self.settings.calculate_dyn_ampls,
                           self.settings.calculate_clean_ampls]):
                        ManticoreEngine.fill_tails_dict(
                            self, i,
                            [LauncherManipulators.tails_console_outside_manipulator,
                            LauncherManipulators.tails_console_inside_manipulator]
                            )
                        ped_flag = 0
                        if self.settings.calculate_clean_ampls:
                            ped_flag += 1
                            # take part in [1, 3, 5, 7] => bin =>
                            # 1, 11, 101, 111 - we take [-1] digit
                        if self.settings.calculate_stat_ampls:
                            ped_flag += 2
                            # take part in [2, 3, 6, 7] => bin =>
                            # 10, 110, 11, 111 - we take [-2] digit
                        if self.settings.calculate_dyn_ampls:
                            ped_flag += 4
                            # take part in [4, 5, 6, 7] => bin =>
                            # 100, 110, 101, 111 - we take [-3] digit
                        ManticoreEngine.amplitudes_to_file(
                            self, i,
                            [LauncherManipulators.amplitudes_console_outside_manipulator,
                            LauncherManipulators.amplitudes_console_inside_manipulator],
                            ped_flag=ped_flag
                            )

class ManticoreEngine:
    def parser(controller, manipulators: list[callable, callable]) -> None:
        outside_launcher_manipulator, inside_launcher_manipulator = manipulators
        controller.settings.temp_path.mkdir(parents = False, exist_ok = True) # IS FULL REWRITE??? OLD FILES ARE GONE???
        list_of_objects_iterator = outside_launcher_manipulator(controller)
        for i, day_directory in list_of_objects_iterator:
            day_files = set()
            for j, (root, dirs, files) in enumerate(os.walk(day_directory.path)):
                if root[-5:-2] == "BSM":
                    for file in files:
                        file = pathlib.Path(file)
                        day_files.add(file.stem)
                        controller.list_of_objects[i].tails_dict[file.suffix] = []
            inside_launcher_manipulator(controller, i)
            controller.list_of_objects[i].files_list = sorted(list(day_files))
            controller.list_of_objects[i].tails_list = list(controller.list_of_objects[i].tails_dict.keys())
            controller.list_of_objects[i].tails_number = len(controller.list_of_objects[i].tails_list)

    def static_pedestals(controller, number_of_day_in_total_list: int, manipulators: list[callable, callable], record_flag: bool) -> None:
        day = controller.list_of_objects[number_of_day_in_total_list]
        outside_launcher_manipulator, inside_launcher_manipulator = manipulators
        day_ped_path_contains = sorted(day.path.joinpath("PED").iterdir())
        day_ped_path_contains_size = len(day_ped_path_contains)
        assert day_ped_path_contains_size == controller.constants.BSM_number, "Something wrong!"
        list_of_ped_files_iterator = outside_launcher_manipulator(controller, day.name, day_ped_path_contains)
        for k, ped_file in list_of_ped_files_iterator:
            PED = np.zeros([1, controller.constants.number_of_codes], dtype=controller.constants.IACT_float)
            counter = 0
            with open(ped_file, "rb") as ped_fin:
                chunk = ped_fin.read(controller.constants.chunk_size)
                while chunk:
                    ped_array = np.array(
                        struct.unpack(
                            "<64h",
                            chunk[controller.constants.codes_beginning_byte:controller.constants.codes_ending_byte]
                            ),
                        dtype=controller.constants.IACT_float
                        ).reshape(1, controller.constants.number_of_codes)/4
                    PED = np.vstack((PED, ped_array))
                    counter += 1
                    chunk = ped_fin.read(controller.constants.chunk_size)
            PED = PED[1:]
            PED_av = np.divide(np.sum(PED, axis=0), counter, where=counter!=0).reshape(1, controller.constants.number_of_codes)
            PED_sigma = np.sum(np.divide(np.absolute(PED - PED_av), counter, where=counter!=0), axis=0).reshape(1, controller.constants.number_of_codes)
            sigma_av = np.average(PED_sigma)
            sigma_sigma = np.sqrt(np.sum((np.average(PED_sigma) - PED_sigma)**2)/len(PED_sigma))
            ignore_status = np.array([(i%2 + 1) if (np.absolute(PED_sigma[0][i]) > sigma_av + 3*sigma_sigma) else 0 for i in range(len(PED_av[0]))]).reshape(1, controller.constants.number_of_codes)
            inside_launcher_manipulator(controller, k, day_ped_path_contains_size)
            day.stat_peds_average.append([PED_av[0] for i in range(day.tails_number)])
            day.stat_peds_sigma.append([PED_sigma[0] for i in range(day.tails_number)])
            day.stat_ignore_pack.append([ignore_status[0] for i in range(day.tails_number)])
        # (BSM_number, tails_number, number_of_codes) -> (tails_number, BSM_number, number_of_codes)
        day.stat_peds_average = np.array(day.stat_peds_average).swapaxes(0, 1)
        day.stat_peds_sigma = np.array(day.stat_peds_sigma).swapaxes(0, 1)
        day.stat_ignore_pack = np.array(day.stat_ignore_pack).swapaxes(0, 1)
        if record_flag:
            root = controller.settings.temp_path
            out_csv_file = root.joinpath(pathlib.Path(day.name + "_static_pedestals").with_suffix(".csv"))
            out_csv_file.touch(exist_ok = True)
            out_csv_file.write_text("")
            for i, tail in enumerate(day.stat_peds_average):
                for j, BSM_codes in enumerate(tail):
                    pd.DataFrame(BSM_codes).T.to_csv(out_csv_file, mode='a', index=False, header=False)

    def dynamic_pedestals(controller, number_of_day_in_total_list: int, manipulators: list[callable, callable], record_flag: bool) -> None:
        day = controller.list_of_objects[number_of_day_in_total_list]
        outside_launcher_manipulator, inside_launcher_manipulator = manipulators
        day.dyn_peds_average = [[] for i in range(controller.constants.BSM_number)]
        day.dyn_peds_sigma = [[] for i in range(controller.constants.BSM_number)]
        day.dyn_ignore_pack = [[] for i in range(controller.constants.BSM_number)]
        list_of_tails_iterator = outside_launcher_manipulator(controller, day.name, day.tails_list)
        for k, tail in list_of_tails_iterator:
            for j, BSM_number in enumerate(controller.constants.BSM_list):
                next_file_in_current_tail_bunch = day.path.joinpath(
                    controller.constants.BSM_list[j]).joinpath(day.files_list[j]).with_suffix(tail)
                counter = np.zeros([1, controller.constants.number_of_codes], dtype=controller.constants.IACT_float)
                PED = np.zeros([1, controller.constants.number_of_codes], dtype=controller.constants.IACT_float)
                chunk_counter = 0
                with open(next_file_in_current_tail_bunch, "rb") as codes_fin:
                    chunk = codes_fin.read(controller.constants.chunk_size)
                    while chunk and chunk_counter < controller.constants.test_pedestal_bunch_size:
                                                    # work value = np.inf, test value = 50...200
                        codes_array = np.array(
                            struct.unpack(
                                "<64h",
                                chunk[controller.constants.codes_beginning_byte:controller.constants.codes_ending_byte]
                                ), # int because later we need the last bit of the each code
                            dtype=controller.constants.IACT_codes_int
                            ).reshape(1, controller.constants.number_of_codes)
                        for i in range(0, len(codes_array[0]), 2):
                            if int(bin(codes_array[0][i])[-1]) == 1:  # trigger indicator == 1
                                codes_array[0][i:i+2] = 0
                            else:
                                counter[0][i:i+2] += 1
                        # if simply "codes_array /= 4", python cannot broadcast datatype int --> float
                        codes_array = np.divide(codes_array, 4, dtype=controller.constants.IACT_float)
                        PED = np.vstack((PED, codes_array))
                        chunk = codes_fin.read(controller.constants.chunk_size)
                        chunk_counter += 1
                PED = PED[1:]
                PED_av = np.divide(np.sum(PED, axis=0), counter, where=(counter != 0)).reshape(1, controller.constants.number_of_codes)
                PED_sigma = np.sum(np.divide(np.absolute(PED - PED_av), counter, where=(counter != 0)), axis=0).reshape(1, controller.constants.number_of_codes)
                sigma_av = np.average(PED_sigma)
                sigma_sigma = np.sqrt(np.sum((sigma_av - PED_sigma[0])**2)/len(PED_sigma[0]))
                ignore_status = np.array(
                    [(i%2 + 1) if (
                        np.absolute(PED_sigma[0][i]) > sigma_av + 3*sigma_sigma) else 0 for i in range(
                        len(PED_av[0]))]).reshape(1, controller.constants.number_of_codes)
                day.dyn_peds_average[j].append(PED_av[0])
                day.dyn_peds_sigma[j].append(PED_sigma[0])
                day.dyn_ignore_pack[j].append(ignore_status[0])
            inside_launcher_manipulator(controller, k, day.tails_number)
        day.dyn_peds_average = np.array(day.dyn_peds_average).swapaxes(0, 1)
        day.dyn_peds_sigma = np.array(day.dyn_peds_sigma).swapaxes(0, 1)
        day.dyn_ignore_pack = np.array(day.dyn_ignore_pack).swapaxes(0, 1)
        if record_flag:
            root = controller.settings.temp_path
            out_csv_file = root.joinpath(pathlib.Path(day.name + "_dynamic_pedestals").with_suffix(".csv"))
            out_csv_file.touch(exist_ok = True)
            out_csv_file.write_text("")
            for i, tail in enumerate(day.dyn_peds_average):
                for j, BSM_codes in enumerate(tail):
                    pd.DataFrame(BSM_codes).T.to_csv(out_csv_file, mode='a', index=False, header=False)

    def fill_tails_dict(controller, number_of_day_in_total_list: int, manipulators: list[callable, callable]) -> None:
        outside_launcher_manipulator, inside_launcher_manipulator = manipulators
        day = controller.list_of_objects[number_of_day_in_total_list]
        root = controller.settings.temp_path
        out_csv_file = root.joinpath(pathlib.Path(day.name + "_event_number_ranges").with_suffix(".csv"))
        out_csv_file.touch(exist_ok = True)
        out_csv_file.write_text("")
        list_of_tails_iterator = outside_launcher_manipulator(controller, day.name, day.tails_list)
        for k, tail in list_of_tails_iterator:
            opened_files_bunch = []
            for j in range(controller.constants.BSM_number):
                next_file_in_current_tail_bunch = day.path.joinpath(
                    controller.constants.BSM_list[j]).joinpath(day.files_list[j]).with_suffix(tail)
                opened_files_bunch.append(open(next_file_in_current_tail_bunch, 'rb'))
            for file in opened_files_bunch:
                chunk = file.read(controller.constants.chunk_size)
                event_number = struct.unpack('I', chunk[controller.constants.number_1_beginning_byte:controller.constants.number_1_ending_byte])[0]
                day.tails_dict[tail].append(event_number)
                chunk = file.read(controller.constants.chunk_size)
                while chunk:
                    event_number = struct.unpack('I', chunk[controller.constants.number_1_beginning_byte:controller.constants.number_1_ending_byte])[0]
                    chunk = file.read(controller.constants.chunk_size)
                day.tails_dict[tail].append(event_number)
            inside_launcher_manipulator(controller, k, day.tails_number)
        for key, key_list in day.tails_dict.items():
            day.tails_dict[key] = [np.min(key_list), np.max(key_list)]
            pd.DataFrame([int(key[1:]), *day.tails_dict[key]]).T.to_csv(out_csv_file, mode='a', index=False, header=False)

    def amplitudes_to_file(controller, number_of_day_in_total_list: int, manipulators: list[callable, callable], ped_flag: int) -> None:
        dyn_flag, stat_flag, clean_flag = list(bin(ped_flag)[2:])
        day = controller.list_of_objects[number_of_day_in_total_list]
        root = controller.settings.temp_path
        if clean_flag:
            clean_out_csv_file = root.joinpath(pathlib.Path(day.name + "_clean_amplitudes").with_suffix(".csv"))
            clean_out_csv_file.touch(exist_ok = True)
            clean_out_csv_file.write_text("")
        if stat_flag:
            static_out_csv_file = root.joinpath(pathlib.Path(day.name + "_static_amplitudes").with_suffix(".csv"))
            static_out_csv_file.touch(exist_ok = True)
            static_out_csv_file.write_text("")
        if dyn_flag:
            dynamic_out_csv_file = root.joinpath(pathlib.Path(day.name + "_dynamic_amplitudes").with_suffix(".csv"))
            dynamic_out_csv_file.touch(exist_ok = True)
            dynamic_out_csv_file.write_text("")
        coinscidence_dict = {}
        for BSM_number in range(controller.constants.BSM_number):
            coinscidence_dict[BSM_number] = 0
        outside_launcher_manipulator, inside_launcher_manipulator = manipulators
        day = controller.list_of_objects[number_of_day_in_total_list]
        list_of_tails_iterator = outside_launcher_manipulator(controller, day.name, day.tails_list)
        for k, tail in list_of_tails_iterator:
            opened_files_bunch = []
            for j in range(controller.constants.BSM_number):
                next_file_in_current_tail_bunch = day.path.joinpath(
                    controller.constants.BSM_list[j]).joinpath(day.files_list[j]).with_suffix(tail)
                opened_files_bunch.append(open(next_file_in_current_tail_bunch, 'rb'))
            chunk_array = [file.read(controller.constants.chunk_size) for file in opened_files_bunch]
            for i in tqdm(range(day.tails_dict[tail][0], day.tails_dict[tail][1]+1), desc=f'Events: '):
                clean_event, static_event, dynamic_event = [i], [i], [i]
                coinscidence_counter = 0
                for x, chunk in enumerate(chunk_array):
                    if chunk:
                        event_number = struct.unpack(
                            'I',
                            chunk[controller.constants.number_1_beginning_byte:controller.constants.number_1_ending_byte])[0]
                        if event_number == i:
                            clean_amplitudes = np.zeros([1, controller.constants.number_of_codes], dtype=controller.constants.IACT_float)
                            coinscidence_counter += 1
                            time_array = struct.unpack('hhhh', chunk[12:20])
                            maroc_number = struct.unpack('h', chunk[20:22])[0]
                            ns = (time_array[0] & 0x7f)*10
                            mks = (time_array[0] & 0xff80) >> 7
                            mks |= (time_array[1] & 1) << 9
                            mls = (time_array[1] & 0x7fe) >> 1
                            s = (time_array[1] & 0xf800) >> 11
                            s |= (time_array[2] & 1) << 5
                            m = (time_array[2] & 0x7e) >> 1
                            h = (time_array[2] & 0xf80) >> 7
                            time_string = "{}:{}:{}.{}.{}.{}".format(h, m, s, mls, mks, ns)
                            codes_array = np.array(
                                struct.unpack(
                                    "<64h",
                                    chunk[controller.constants.codes_beginning_byte:controller.constants.codes_ending_byte]
                                    ),
                                dtype=controller.constants.IACT_float
                                ).reshape(1, controller.constants.number_of_codes)
                            for m in range(0, len(clean_amplitudes[0]), 2):
                                if codes_array[0][m] <= controller.constants.channel_threshold:
                                    clean_amplitudes[0][m] = codes_array[0][m]/4
                                else:
                                    clean_amplitudes[0][m:m+2] = codes_array[0][m+1]/4, 1
                            if clean_flag:
                                clean_event += [maroc_number, time_string,
                                                *clean_amplitudes[0]]
                            if stat_flag:
                                static_event += [maroc_number, time_string,
                                                 *(clean_amplitudes[0] - day.stat_peds_average[k][maroc_number])]
                            if dyn_flag:
                                dynamic_event += [maroc_number, time_string,
                                                  *(clean_amplitudes[0] - day.dyn_peds_average[k][maroc_number])]
                            chunk_array[x] = opened_files_bunch[x].read(controller.constants.chunk_size)
                            if not chunk_array[x]:
                                chunk_array[x] = None
                coinscidence_dict[coinscidence_counter] += 1
                if clean_flag:
                    pd.DataFrame(clean_event).T.to_csv(clean_out_csv_file, mode='a', index=False, header=False)
                if stat_flag:
                    pd.DataFrame(static_event).T.to_csv(static_out_csv_file, mode='a', index=False, header=False)
                if dyn_flag:
                    pd.DataFrame(dynamic_event).T.to_csv(dynamic_out_csv_file, mode='a', index=False, header=False)
            inside_launcher_manipulator(controller, k, day.tails_number)
        coin_file = root.joinpath(pathlib.Path(day.name + "_coinscidens").with_suffix(".csv"))
        coin_file.touch(exist_ok = True)
        coin_file.write_text("")
        pd.DataFrame.from_dict(coinscidence_dict).to_csv(coin_file, mode='a', index=False, header=False)


if __name__ == "__main__":
    ManticoreConsole()
    # ManticoreGUI().mainloop()
