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
# from collections import namedtuple


@dataclass
class Day:
    name: str = None
    tails_dict: dict = field(default_factory=dict)
    path: pathlib.WindowsPath = None
    static_pedestals: list = field(default_factory=list)
    stat_peds_average: list = field(default_factory=list)
    stat_peds_sigma: list = field(default_factory=list)
    stat_ignore_pack: list = field(default_factory=list)


class ManticoreTools:
    def get_pathes():
        script_directory = pathlib.Path(__file__).parent
        input_card_path = script_directory.joinpath('input_card.conf')
        data_directory_conf_path = script_directory.joinpath('data_directory.conf')
        temp_files_directory_conf_path = script_directory.joinpath('temporary_files_directory.conf')
        data_directory_path = pathlib.Path(data_directory_conf_path.read_text().strip())
        temp_files_directory_path = pathlib.Path(temp_files_directory_conf_path.read_text().strip())
        return input_card_path, data_directory_path, temp_files_directory_path

    def time_check(start_time):
        current_time = time.time() - start_time
        return f'[ {int(current_time//60//60):2} h {int(current_time//60%60):2} m {int(current_time%60):2} s ]'

    def read_input_card(input_card_path):
        with open(input_card_path, "r") as input_card:
            ans_list = []
            for line in input_card.readlines():
                if line[0] != '#':
                    ans_list.append(line[:-1])
        return [ans for ans in ans_list]


class LauncherManipulators:
    def parser_gui_outside_manipulator(gui):
        gui.operation_name_parent_label.configure(text="Parsing input elements pathes...")
        gui.operation_numerator_parent_label.configure(text=f'1/10')
        return enumerate(gui.list_of_objects)

    def parser_gui_inside_manipulator(gui, i):
        gui.progressbar_parent_value_var.set((i+1)*100//gui.list_of_objects_size)
        gui.percent_parent_value_label.configure(text=f'{gui.progressbar_parent_value_var.get()} %')
        gui.time_from_start_parent_label.configure(text=ManticoreTools.time_check(gui.start_time))
        gui.run_frame_parent.update()

    def parser_console_outside_manipulator(console):
        return enumerate(tqdm(console.list_of_objects, desc="Parsing input elements pathes..."))

    def parser_console_inside_manipulator(console, i):
        pass

    def static_pedestals_gui_outside_manipulator(gui, day_name, list_of_ped_files):
        gui.operation_name_parent_label.configure(text=f'{day_name}: Making static pedestals...')
        gui.operation_numerator_parent_label.configure(text=f'2/10')
        return enumerate(list_of_ped_files)

    def static_pedestals_gui_inside_manipulator(gui, i, list_of_ped_files_size):
        gui.progressbar_parent_value_var.set((i+1)*100//list_of_ped_files_size)
        gui.percent_parent_value_label.configure(text=f'{gui.progressbar_parent_value_var.get()} %')
        gui.time_from_start_parent_label.configure(text=ManticoreTools.time_check(gui.start_time))
        gui.run_frame_parent.update()

    def static_pedestals_console_outside_manipulator(console, day_name, list_of_ped_files):
        return enumerate(tqdm(list_of_ped_files, desc=f'{day_name}: Making static pedestals...'))

    def static_pedestals_console_inside_manipulator(console, i, list_of_ped_files):
        pass


class ManticoreConsole:
    def __init__(self):
        self.input_card_path, self.data_directory_path, self.temp_directory_path = ManticoreTools.get_pathes()
        self.set_1, self.set_2, self.set_3 = ManticoreTools.read_input_card(self.input_card_path)
        self.need_to_remove_all_temp_files = int(self.set_1)
        self.need_to_leave_temp_files_after_processing = int(self.set_2)
        self.objects_list = self.set_3.split()
        self.set_all_data = 1 if self.objects_list == ["a"] else 0
        self.START_TIME = time.time()
        print("Launching Manticore 3.14 Controller...")
        ManticoreController(self, "console")


class ManticoreGUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("Manticore 3.14")
        self.input_card_path, self.data_directory_path, self.temp_directory_path = ManticoreTools.get_pathes()
        self.objects_list = []
        self.set_1, self.set_2, self.set_all_data_var = tk.IntVar(), tk.IntVar(), tk.IntVar()
        self.set_all_data = 0
        self.need_to_remove_all_temp_files = 0
        self.need_to_leave_temp_files_after_processing = 0
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
        self.set_all = tk.Checkbutton(self.checkbutton_frame, variable=self.set_all_data_var, text="Process all data", command=self.__choose_all_data)
        self.set_all.pack(side="top", padx=10, pady=25, anchor="nw")
        self.add_button = tk.Button(self.checkbutton_frame, text="Add item", command=lambda: self.__add_item_to_listbox(event=None))
        self.add_button.pack(side="top", padx=10, pady=10, anchor="w")
        self.new_item_field = tk.Entry(self.checkbutton_frame)
        self.new_item_field.bind("<Return>", self.__add_item_to_listbox)
        self.new_item_field.pack(side="top", padx=10, pady=10, anchor="w")

    def __choose_all_data(self):
        if self.add_button['state'] == 'normal':
            self.add_button.configure(state='disabled')
            self.new_item_field.configure(state='disabled')
            self.objects_listbox.configure(state='disabled')
        else:
            self.add_button.configure(state='normal')
            self.new_item_field.configure(state='normal')
            self.objects_listbox.configure(state='normal')

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
        self.set_all_data = 1 if (self.objects_list == ["a"] or self.set_all_data_var) else 0
        self.need_to_remove_all_temp_files = self.set_1.get()
        self.need_to_leave_temp_files_after_processing = self.set_2.get()
        ManticoreController(self, "gui")

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
        self.input_card_path = pathlib.Path(self.input_card_path_field.get())
        self.input_card_path_field.configure(state='disabled')
        self.input_card_path_field.update()

    def __change_data_directory_path(self, event):
        self.data_directory_path = pathlib.Path(self.data_directory_path_field.get())
        self.data_directory_path_field.configure(state='disabled')
        self.data_directory_path_field.update()

    def __change_temp_directory_path(self, event):
        self.temp_directory_path = pathlib.Path(self.temp_directory_path_field.get())
        self.temp_directory_path_field.configure(state='disabled')
        self.temp_directory_path_field.update()


class ManticoreController:
    def __init__(self, launcher, launcher_type):
        self.start_time = launcher.START_TIME
        self.input_card_path = launcher.input_card_path
        self.data_directory_path = launcher.data_directory_path
        self.temp_directory_path = launcher.temp_directory_path
        self.files_list_file = self.temp_directory_path.joinpath('files_list.txt')
        self.files_list = []
        self.set_all_data = launcher.set_all_data
        self.need_to_remove_all_temp_files = launcher.need_to_remove_all_temp_files
        self.need_to_leave_temp_files_after_processing = launcher.need_to_leave_temp_files_after_processing
        if launcher_type == "gui":
            self.run_frame_parent = launcher.run_frame
            self.operation_name_parent_label = launcher.operation_name
            self.operation_numerator_parent_label = launcher.operation_numerator
            self.progressbar_parent_value_var = launcher.progressbar_value_var
            self.percent_parent_value_label = launcher.percents
            self.time_from_start_parent_label = launcher.time_label
        if self.set_all_data:
            self.list_of_objects = [Day(name=day, path=self.data_directory_path.joinpath(day)) for day in self.data_directory_path.iterdir() if os.path.isdir(day)]
        else:
            self.list_of_objects = [Day(name=day, path=self.data_directory_path.joinpath(day)) for day in launcher.objects_list if os.path.isdir(self.data_directory_path.joinpath(day))]
        self.list_of_objects_size = len(self.list_of_objects)
        self.start_engine(launcher_type)
        # for object in self.list_of_objects:
        #     print(object, '\n')

    def start_engine(self, launcher_type):
        if launcher_type == "gui":
            ManticoreEngine.parser(self, [LauncherManipulators.parser_gui_outside_manipulator,
                                          LauncherManipulators.parser_gui_inside_manipulator])
            for i in range(self.list_of_objects_size):
                ManticoreEngine.static_pedestals(self, i, [LauncherManipulators.static_pedestals_gui_outside_manipulator,
                                                        LauncherManipulators.static_pedestals_gui_inside_manipulator])

        elif launcher_type == "console":
            ManticoreEngine.parser(self, [LauncherManipulators.parser_console_outside_manipulator,
                                          LauncherManipulators.parser_console_inside_manipulator])
            for i in range(self.list_of_objects_size):
                ManticoreEngine.static_pedestals(self, i, [LauncherManipulators.static_pedestals_console_outside_manipulator,
                                                        LauncherManipulators.static_pedestals_console_inside_manipulator])


class ManticoreEngine:
    def parser(controller, manipulators):
        outside_launcher_manipulator, inside_launcher_manipulator = manipulators
        controller.temp_directory_path.mkdir(parents = False, exist_ok = True) # FULL REWRITE. OLD FILES ARE GONE !!!
        controller.files_list_file.touch(exist_ok = True) # FULL REWRITE !!!
        list_of_objects_iterator = outside_launcher_manipulator(controller)
        for i, day_directory in list_of_objects_iterator:
            for j, (root, dirs, files) in enumerate(os.walk(day_directory.path)):
                if root[-5:-2] == "BSM":
                    for file in files:
                        file = pathlib.Path(root).joinpath(file)
                        tail = file.suffix[1:]
                        controller.files_list.append(file)
                        controller.list_of_objects[i].tails_dict[tail] = []
            inside_launcher_manipulator(controller, i)
        controller.files_list.sort()
        controller.files_list_file.write_text("\n".join([str(file) for file in controller.files_list]))

    def static_pedestals(controller, number_of_day_in_total_list, manipulators):
        outside_launcher_manipulator, inside_launcher_manipulator = manipulators
        day_path = controller.list_of_objects[number_of_day_in_total_list].path
        day_name = controller.list_of_objects[number_of_day_in_total_list].name
        day_ped_path_contains = sorted(day_path.joinpath("PED").iterdir())
        day_ped_path_contains_size = len(day_ped_path_contains)
        list_of_ped_files_iterator = outside_launcher_manipulator(controller, day_name, day_ped_path_contains)
        for k, ped_file in list_of_ped_files_iterator:
            counter = 0
            number_of_codes = 64
            PED = []
            PED_av = [0]*number_of_codes
            PED_sum = [0]*number_of_codes
            PED_sigma = [0]*number_of_codes
            sigma_sigma = 0
            ignore_status = [0]*number_of_codes
            chunk_size = 156
            codes_beginning_byte = 24
            codes_ending_byte = 152

            with open(ped_file, "rb") as ped_fin:
                chunk = ped_fin.read(chunk_size)
                while chunk:
                    ped_array = np.array(struct.unpack("<64h", chunk[codes_beginning_byte:codes_ending_byte]))
            # ? ----------------------------------------------
            # ?         for i in range(number_of_codes):
            # ?             PED.append(ped_array)
            # ?             PED_av[i] += ped_array[i]/4
            # ? ----------------------------------------------
                    for i in range(number_of_codes):          #
                        ped_array[i] /= 4                     #
                    PED.append(ped_array)                     #
                    for i in range(number_of_codes):          #
                        PED_av[i] += ped_array[i]             #
            # ------------------------------------------------
                    counter += 1
                    chunk = ped_fin.read(chunk_size)

            for i in range(number_of_codes):
                PED_av[i] /= counter

            # ? ---------------------------------------------------------------------
            # ? for line in PED:
            # ?     for i in range(len(line)):
            # ?         PED_sum[i] += abs(line[i] - PED_av[i])
            # ? ---------------------------------------------------------------------
            for line in PED:                                                         #
                for i in range(len(line)):                                           #
                    line[i] = np.sqrt((line[i] - PED_av[i])*(line[i] - PED_av[i]))   #
            for line in PED:                                                         #
                for i in range(len(line)):                                           #
                    PED_sum[i] += line[i]                                            #
            # -----------------------------------------------------------------------

            for i in range(number_of_codes):
                PED_sigma[i] = PED_sum[i]/counter
            sigma_av = sum(PED_sigma)/len(PED_sigma)
            for item in PED_sigma:
                sigma_sigma += (sigma_av - item)**2
            sigma_sigma = np.sqrt(sigma_sigma/len(PED_sigma))
            for i in range(len(PED_av)):
                if not (-1*sigma_av - 3*sigma_sigma < PED_sigma[i] < sigma_av + 3*sigma_sigma):
                    ignore_status[i] += (i%2 +1)

            ignore_pack = struct.pack('<64B', *ignore_status)
            peds_average = struct.pack('<64f', *PED_av)
            peds_sigma = struct.pack('<64f', *PED_sigma)

            inside_launcher_manipulator(controller, k, day_ped_path_contains_size)

            controller.list_of_objects[number_of_day_in_total_list].stat_peds_average.append(peds_average)
            controller.list_of_objects[number_of_day_in_total_list].stat_peds_sigma.append(peds_sigma)
            controller.list_of_objects[number_of_day_in_total_list].stat_ignore_pack.append(ignore_pack)


if __name__ == "__main__":
    ManticoreConsole()
    # ManticoreGUI().mainloop()
