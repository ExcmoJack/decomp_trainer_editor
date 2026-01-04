#! /usr/bin/env python3

import tkinter as tk
import os
from modules.classes import Trainer, Pokemon, AiFlagList
from modules.ProjectSelection import ask_project
from modules.SaveTrainerData import *
from modules.ParseRepoData import *
from tkinter import ttk
from tkinter import filedialog, messagebox

def get_current_directory():
    ''' Get the directory where the script is located '''
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_last_opened_project():
    ''' Retrieve the last opened project path from config.json '''
    config_path = os.path.join(get_current_directory(), "assets", "config.json")
    if os.path.exists(config_path):
        import json
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("last_opened_project", "")
    return ""

def set_last_opened_project(path):
    ''' Save the last opened project path to config.json '''
    config_path = os.path.join(get_current_directory(), "assets", "config.json")
    config = {}
    if os.path.exists(config_path):
        import json
        with open(config_path, "r") as f:
            config = json.load(f)
    config["last_opened_project"] = path
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

TRAINER_PIC_PLACEHOLDER = os.path.join(get_current_directory(), "assets", "trainer_placeholder.png")
MON_PIC_PLACEHOLDER = os.path.join(get_current_directory(), "assets", "pokemon_placeholder.png")

class ProjectData():
    '''
    Stores project-wide data such as trainers, expansion flag, and AI flags.
    '''
    def __init__(self):
        '''
        Initializes the ProjectData with empty trainers list, expansion flag set to False, and a new AiFlagList.
        '''
        self.trainers = []
        self.expansion = False
        self.ai_flags = AiFlagList()

class App(tk.Tk):
    def __init__(self):
        '''
        Initializes the main application and sets up the main window.
        Calls init_window_data to prepare the data and graphical interface.
        '''
        super().__init__()
        self.init_window_data()    


    def init_window_data(self):
        '''
        Initializes window-related data and prepares the main interface components.
        This method sets up variables, widgets, and any necessary state for the main window.
        '''
        self.title("Decomp Trainer Editor")
        self.geometry("1366x768")
        self.project_path = None
        self.project_type = None
        self.project_files = {}
        self.project_data = ProjectData()
        self.showdown_type_output = False
        self.current_trainer_id = 1
        self.current_trainer_mon = 0
        self.resizable(False, False)

        self.create_menubar()
        self.create_window_layout()
        self.create_status_bar()


    def create_menubar(self):
        '''
        Creates and configures the application's menu bar.
        This method sets up the main menu options and attaches them to the window.
        '''
        ############
        # MENU BAR #
        ############

        # Defining the top menu bar container
        self.menubar = tk.Menu(self)

        # File menu: It allows to open/save projects and exit the app.
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu_open = self.file_menu.add_command(label="Open project", command=self.open_project)
        file_menu_save = self.file_menu.add_command(label="Save project", command=self.save_project, state=tk.DISABLED)
        self.file_menu.add_separator()
        file_menu_exit = self.file_menu.add_command(label="Exit", command=self.quit)

        # Edit menu: It allows to copy/paste trainer settings or just Pokémon data. It will be disabled by default until a project is opened.
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="Copy trainer")
        edit_menu.add_command(label="Paste trainer")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy Pokémon")
        edit_menu.add_command(label="Paste Pokémon")

        # Help menu: It allows to access documentation and see info about the app.
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.launch_documentation)
        help_menu.add_command(label="About", command=self.show_about_dialog)

        # Adding all menus to the menubar and configuring the root window to use it
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Edit", menu=edit_menu, state=tk.DISABLED)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=self.menubar)


    def create_window_layout(self):
        '''
        Creates and arranges the main window layout.

        Sets up the three main columns: trainer selection, trainer info, and Pokémon info.
        Initializes all widgets and containers for user interaction.
        '''
        # The main windows layout is divided in 3 columns. One will permit to select the trainer to edit,
        # the second will show trainer general info and the third will show the selected Pokémon info from the party.
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        ##############################
        # COLUMN 1 - Trainer ID List #
        ##############################

        # Trainer list container. It will have a fixed width and scrollbars as the ID don't use to be too long.
        column1_format = {"width": 340,"bd": 2, "relief": tk.GROOVE}
        column1 = tk.Frame(self.main_frame, **column1_format)
        column1.pack(side=tk.LEFT, fill=tk.Y)
        column1.pack_propagate(False)
        # Trainer list container set up.
        listbox_frame = tk.Frame(column1)
        listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Internal frame to hold the listbox and the horizontal scrollbar below it
        listbox_pack_frame = tk.Frame(listbox_frame)
        listbox_pack_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_trainers_id = tk.Listbox(listbox_pack_frame, selectmode=tk.SINGLE)
        self.listbox_trainers_id.bind("<<ListboxSelect>>", self.update_trainer_fields_trigger)
        scrollbar_listbox_trainers_id_x = tk.Scrollbar(listbox_pack_frame, orient=tk.HORIZONTAL, command=self.listbox_trainers_id.xview)
        self.listbox_trainers_id.config(xscrollcommand=scrollbar_listbox_trainers_id_x.set)
        self.listbox_trainers_id.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar_listbox_trainers_id_x.pack(side=tk.TOP, fill=tk.X)
        # Add vertical scrollbar to the right of the listbox
        scrollbar_listbox_trainers_id_y = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.listbox_trainers_id.yview)
        self.listbox_trainers_id.config(yscrollcommand=scrollbar_listbox_trainers_id_y.set)
        scrollbar_listbox_trainers_id_y.pack(side=tk.RIGHT, fill=tk.Y)

        ############################
        # COLUMN 2 - Trainer Setup #
        ############################

        # Trainer info container. Info is supposed to be updated when selecting a trainer from the listbox. Maybe lacks of a save button?
        column2_format = {"bd": 2, "relief": tk.GROOVE}
        column2 = tk.Frame(self.main_frame, **column2_format)
        column2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.list_gender_options = ["MALE", "FEMALE"]

        # Show trainer picture at the top left
        try:
            self.photoimage_trainer_pic = tk.PhotoImage(file=(TRAINER_PIC_PLACEHOLDER))
            img_label = ttk.Label(column2, image=self.photoimage_trainer_pic)
            img_label.grid(row=0, column=0, rowspan=2)
        except Exception:
            # In case the image is not found or can't be loaded, show a blank canvas instead
            self.canvas_trainer_pic_when_file_missing = tk.Canvas(column2, width=64, height=64, bg="#cccccc", highlightthickness=0)
            self.canvas_trainer_pic_when_file_missing.grid(row=0, column=0, rowspan=2)

        # Trainer ID and Name showed at the top right. Think about letting modify the ID.
        # Maybe let be editable after clicking a button or the field itself. Read only by now.
        row = 0
        self.text_entry_trainer_id = ttk.Entry(column2)
        self.text_entry_trainer_id.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.text_entry_trainer_id.config(state='readonly')
        row += 1

        self.text_entry_trainer_name = ttk.Entry(column2)
        self.text_entry_trainer_name.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.text_entry_trainer_name.config(state='readonly')
        row += 1

        # Radio buttons for gender. This will be saved in self.current_trainer_gender_var.
        self.current_trainer_gender_var = tk.StringVar(value=self.list_gender_options[0])
        frame_gender_options = ttk.Frame(column2)
        frame_gender_options.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=2)
        self.radio_gender = []
        for i, opt in enumerate(self.list_gender_options):
            rb = ttk.Radiobutton(frame_gender_options, text=opt, variable=self.current_trainer_gender_var, value=opt, state="disabled")
            self.radio_gender.append(rb)
            rb.pack(side=tk.LEFT, padx=5)
        row += 1

        # Combobox for each remaining field. Empty values by default before loading a project.
        ttk.Label(column2, text="Trainer Pic:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.combobox_trainer_pic = ttk.Combobox(column2, values=[], state="disabled")
        self.combobox_trainer_pic.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.combobox_trainer_pic.bind("<<ComboboxSelected>>", self.set_trainer_pic_trigger)
        row += 1

        ttk.Label(column2, text="Trainer Class:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.combobox_trainer_class = ttk.Combobox(column2, values=[], state="disabled")
        self.combobox_trainer_class.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        row += 1

        ttk.Label(column2, text="Encounter Music:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.combobox_trainer_encounter_music = ttk.Combobox(column2, values=[], state="disabled")
        self.combobox_trainer_encounter_music.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        row += 1

        self.bool_double_battle = tk.BooleanVar(value=False)
        self.checkbox_double_battle = ttk.Checkbutton(column2, text="Double Battle", variable=self.bool_double_battle, state="disabled")
        self.checkbox_double_battle.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        row += 1

        # Here we will have a tabbed notebook with 3 tabs: Pokémon & Items, AI Flags and Places where the trainer battle is found.
        # It is important to pay attention to this part as it is the most complex of the UI.
        notebook_trainer_battle_settings = ttk.Notebook(column2)
        notebook_trainer_battle_settings.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        # ------------------- #
        # Party and Items tab #
        # ------------------- #
        tab_party_and_items = ttk.Frame(notebook_trainer_battle_settings)
        notebook_trainer_battle_settings.add(tab_party_and_items, text="Party and Items")

        # Party and Items container. It will have two columns: Party on the left and Items on the right.
        frame_party_and_items = ttk.Frame(tab_party_and_items)
        frame_party_and_items.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # In the first column we will have the party listbox and buttons below it.
        frame_party = ttk.Frame(frame_party_and_items)
        frame_party.grid(row=0, column=0, sticky="nsw", padx=(0, 20))

        # Here we have the party listbox. It is supposed to be populated with the Pokémon species in the party.
        # Always with the limit of 6 Pokémon in the party.
        ttk.Label(frame_party, text="Party").pack(anchor="w", pady=(0, 5))
        self.listbox_mons_in_party = tk.Listbox(frame_party, height=6)
        self.listbox_mons_in_party.pack(fill=tk.BOTH, expand=True)
        self.listbox_mons_in_party.bind("<<ListboxSelect>>", self.update_mon_fields_trigger)


        # Now this buttons may allow to move up/down the selected Pokémon in the party, add a new one or remove the selected one.
        # They must be disabled if there is no project opened.
        frame_party_list_management = ttk.Frame(frame_party)
        frame_party_list_management.pack(fill=tk.X, pady=(8, 0))

        self.button_party_mon_up     = ttk.Button(frame_party_list_management, text="Up", state=tk.DISABLED, command=self.move_up_party_mon)
        self.button_party_mon_down   = ttk.Button(frame_party_list_management, text="Down", state=tk.DISABLED, command=self.move_down_party_mon)
        self.button_party_add_mon    = ttk.Button(frame_party_list_management, text="Add", state=tk.DISABLED, command=self.add_party_mon)
        self.button_party_remove_mon = ttk.Button(frame_party_list_management, text="Remove", state=tk.DISABLED, command=self.del_party_mon)

        self.button_party_mon_up.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.button_party_mon_down.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.button_party_remove_mon.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.button_party_add_mon.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # The second column will have the four items comboboxes.
        frame_trainer_items = ttk.Frame(frame_party_and_items)
        frame_trainer_items.grid(row=0, column=1, sticky="nsew")

        ttk.Label(frame_trainer_items, text="Items").pack(anchor="w", pady=(0, 5))

        # In this case we will define the items as a list of comboboxes.
        self.list_combobox_trainer_item = []
        for i in range(4):
            combobox_trainer_item = ttk.Combobox(frame_trainer_items, values=[], state="disabled")
            combobox_trainer_item.pack(fill=tk.X, pady=2)
            self.list_combobox_trainer_item.append(combobox_trainer_item)

        frame_party_and_items.columnconfigure(1, weight=1)

        # -------------------- #
        # Trainer AI flags tab #
        # -------------------- #
        self.tab_trainer_ai_flags = ttk.Frame(notebook_trainer_battle_settings)
        notebook_trainer_battle_settings.add(self.tab_trainer_ai_flags, text="AI Flags")
        self.list_ai_flag = []
        # In pokeemerald expansion there are some presets for AI flags. We will add a combobox to select one and a button to apply them
        # only if the project is based on pokeemerald expansion. Currently always shown as we don't detect the project type.
        frame_ai_flags_presets = ttk.Frame(self.tab_trainer_ai_flags)
        frame_ai_flags_presets.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(frame_ai_flags_presets, text="Preset:").pack(side=tk.LEFT, padx=(0, 5))
        self.combobox_ai_flags_presets = ttk.Combobox(frame_ai_flags_presets, values=["Basic Trainer", "Smart Trainer", "Predict"], state="disabled")
        self.combobox_ai_flags_presets.pack(side=tk.LEFT, padx=(0, 5))
        self.button_apply_ai_flags_preset = ttk.Button(frame_ai_flags_presets, text="Apply", state=tk.DISABLED)
        self.button_apply_ai_flags_preset.pack(side=tk.LEFT)
        
        # ---------- #
        # Places tab #
        # ---------- #
        tab_trainer_places = ttk.Frame(notebook_trainer_battle_settings)
        notebook_trainer_battle_settings.add(tab_trainer_places, text="Found at...")
        # List of maps where the trainer battle is found.
        # The idea is to scan all /data/maps/scripts.inc to find all ocurrences of the trainer ID. Pending implementation.
        ttk.Label(tab_trainer_places, text="Maps where the trainer was found").pack(anchor="w", pady=(10, 5), padx=10)
        self.listbox_trainer_map_appereances = tk.Listbox(tab_trainer_places, height=8)
        self.listbox_trainer_map_appereances.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.button_find_trainer_in_maps = ttk.Button(tab_trainer_places, text="Find trainer", state=tk.DISABLED, command=self.find_trainer_in_maps)
        self.button_find_trainer_in_maps.pack(side=tk.BOTTOM, pady=(0, 10))
        row += 1

        self.button_save_trainer = ttk.Button(column2, text="Save Trainer", state=tk.DISABLED, command=self.save_trainer_object)
        self.button_save_trainer.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        ####################################
        # COLUMN 3 - Pokemon configuration #
        ####################################
        column3_format = {"bd": 2, "relief": tk.GROOVE}
        column3 = tk.Frame(self.main_frame, **column3_format)
        column3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Data container for all Pokémon fields. Comboboxes to be populated at project load. Individual Pokémon data
        # to be loaded when selecting a Pokémon from the party listbox.
        frame_selected_mon_data = ttk.Frame(column3)
        frame_selected_mon_data.pack(pady=10, padx=20, fill=tk.X)

        # Show mon picture at the top. If the image can't be loaded, show a blank canvas instead.
        try:
            self.photoimage_mon_pic = tk.PhotoImage(file=MON_PIC_PLACEHOLDER)
            label_mon_pic = ttk.Label(frame_selected_mon_data, image=self.photoimage_mon_pic)
            label_mon_pic.grid(row=0, column=0, columnspan=2)
        except Exception:
            canvas_mon_pic_when_files_missing = tk.Canvas(frame_selected_mon_data, width=64, height=64, bg="#cccccc", highlightthickness=0)
            canvas_mon_pic_when_files_missing.grid(row=0, column=0, columnspan=2)

        # Species
        ttk.Label(frame_selected_mon_data, text="Species:").grid(row=1, column=0, sticky="w", pady=4)
        self.combobox_mon_species = ttk.Combobox(frame_selected_mon_data, values=[], state="disabled")
        self.combobox_mon_species.grid(row=1, column=1, sticky="ew", pady=4)
        self.combobox_mon_species.bind("<<ComboboxSelected>>", self.set_mon_pic_trigger)

        # Level
        ttk.Label(frame_selected_mon_data, text="Level:").grid(row=2, column=0, sticky="w", pady=4)
        self.spinbox_mon_level = tk.Spinbox(frame_selected_mon_data, from_=1, to=100, width=5, state="disabled")
        self.spinbox_mon_level.grid(row=2, column=1, sticky="w", pady=4)

        # Held Item
        ttk.Label(frame_selected_mon_data, text="Held Item:").grid(row=3, column=0, sticky="w", pady=4)
        self.combobox_mon_held_item = ttk.Combobox(frame_selected_mon_data, values=[], state="disabled")
        self.combobox_mon_held_item.grid(row=3, column=1, sticky="ew", pady=4)

        # Ability
        ttk.Label(frame_selected_mon_data, text="Ability:").grid(row=4, column=0, sticky="w", pady=4)
        self.combobox_mon_ability = ttk.Combobox(frame_selected_mon_data, values=["RANDOM", "FIRST", "SECOND", "HIDDEN"], state="disabled")
        self.combobox_mon_ability.grid(row=4, column=1, sticky="ew", pady=4)

        # Nature
        ttk.Label(frame_selected_mon_data, text="Nature:").grid(row=5, column=0, sticky="w", pady=4)
        self.combobox_mon_nature = ttk.Combobox(frame_selected_mon_data, values=[], state="disabled")
        self.combobox_mon_nature.grid(row=5, column=1, sticky="ew", pady=4)

        # Moves
        ttk.Label(frame_selected_mon_data, text="Moves:").grid(row=6, column=0, sticky="w", pady=(12, 4))
        # Moves label and "Default moves" checkbox side by side in a frame
        frame_mon_moves_label = ttk.Frame(frame_selected_mon_data)
        frame_mon_moves_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(12, 4))
        ttk.Label(frame_mon_moves_label, text="Moves:").pack(side=tk.LEFT)
        self.bool_mon_default_moves = tk.BooleanVar(value=False)
        self.checkbox_mon_default_moves = ttk.Checkbutton(frame_mon_moves_label, text="Default moves", variable=self.bool_mon_default_moves, state="disabled", command=self.set_default_moves)
        self.checkbox_mon_default_moves.pack(side=tk.LEFT, padx=10)
        self.combobox_mon_movements = []
        for i in range(4):
            combobox_mon_movement = ttk.Combobox(frame_selected_mon_data, values=[], state="disabled", width=16)
            combobox_mon_movement.grid(row=7 + i, column=0, sticky="ew", pady=2, columnspan=2)
            combobox_mon_movement.bind('<<ComboboxSelected>>', self.uncheck_default_moves)
            self.combobox_mon_movements.append(combobox_mon_movement)

        # IVs
        ttk.Label(frame_selected_mon_data, text="IVs:").grid(row=21, column=0, sticky="w", pady=(12, 4), columnspan=4)
        frame_mon_ivs = ttk.Frame(frame_selected_mon_data)
        frame_mon_ivs.grid(row=22, column=0, columnspan=4, sticky="w")
        self.dict_spinboxes_ivs = {}
        list_mon_stats = ["HP", "ATK", "DEF", "SPD", "SPATK", "SPDEF"]
        for idx, stat in enumerate(list_mon_stats):
            col = 0 if idx < 3 else 1
            row = idx % 3
            ttk.Label(frame_mon_ivs, text=stat+":").grid(row=row, column=col*2, sticky="e", padx=(6,1))
            spinbox = tk.Spinbox(frame_mon_ivs, from_=0, to=31, width=5, state="disabled")
            spinbox.grid(row=row, column=col*2+1, sticky="w", pady=2)
            self.dict_spinboxes_ivs[stat] = spinbox

        # EVs
        ttk.Label(frame_selected_mon_data, text="EVs:").grid(row=31, column=0, sticky="w", pady=(12, 4), columnspan=4)
        frame_mon_evs = ttk.Frame(frame_selected_mon_data)
        frame_mon_evs.grid(row=32, column=0, columnspan=4, sticky="w")
        self.dict_spinboxes_evs = {}
        for idx, stat in enumerate(list_mon_stats):
            col = 0 if idx < 3 else 1
            row = idx % 3
            ttk.Label(frame_mon_evs, text=stat+":").grid(row=row, column=col*2, sticky="e", padx=(6,1))
            spinbox = tk.Spinbox(frame_mon_evs, from_=0, to=255, width=5, state="disabled")
            spinbox.grid(row=row, column=col*2+1, sticky="w", pady=2)
            self.dict_spinboxes_evs[stat] = spinbox

        self.button_save_mon = ttk.Button(frame_selected_mon_data, text="Save Pokémon", state=tk.DISABLED, command=self.save_mon_object)
        self.button_save_mon.grid(row=33, column=0, columnspan=4, pady=6)

        frame_selected_mon_data.columnconfigure(1, weight=1)


    def create_status_bar(self):
        '''
        Creates and displays the status bar at the bottom of the main window.

        The status bar is used to show messages and feedback to the user.
        '''
        # Status bar at the bottom of the window to show messages to the user.
        self.status = tk.Label(self, text="Project not opened.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)


    def open_project(self):
        ''' Open a folder dialog to select the project path and load its data. WIP.'''
        path = filedialog.askdirectory(title="Select project folder", initialdir=get_last_opened_project())
        if path:
            self.menubar.destroy()
            self.main_frame.destroy()
            self.status.destroy()
            self.init_window_data()
            self.project_type = ask_project(self)
            if self.project_type == None:
                messagebox.showinfo(message='Could not identify the project type. Try opening another folder.', icon='warning')
            else:
                try:
                    self.set_project_paths()
                    set_last_opened_project(path)
                    self.project_path = path
                    self.status.config(text=f"Project opened: {path}")
                    self.check_expansion()
                    self.enable_trainer_editing()
                    self.enable_partymon_editing()
                    self.data_adquisition()
                except Exception:
                    messagebox(message="Could not identify the project type. Try opening another folder or selecting another type of project.", icon='error')


    def save_project(self):
        save_obj = TrainerDataFile(self.project_data.trainers, self.project_type)
        save_obj.init_file()
        save_obj.create_files((self.project_path, self.project_files['trainer_data'], self.project_files['trainer_parties']))
    

    def set_project_paths(self):
        config_path = os.path.join(get_current_directory(), "assets", "project_files.json")
        if os.path.exists(config_path):
            import json
            with open(config_path, "r") as f:
                config = json.load(f)
                self.project_files = config.get(self.project_type, "")


    def enable_trainer_editing(self):
        ''' Enable all UI elements to edit trainer data. '''
        trainer_ui_comboboxes = [
            self.combobox_trainer_pic,
            self.combobox_trainer_class,
            self.combobox_trainer_encounter_music,
        ] + self.list_combobox_trainer_item

        trainer_ui_buttons = [
            self.button_party_mon_up,
            self.button_party_mon_down,
            self.button_party_add_mon,
            self.button_party_remove_mon,
            self.button_save_trainer,
            self.button_find_trainer_in_maps
        ]

        self.file_menu.entryconfig(1, state=tk.NORMAL)
        self.menubar.entryconfig("Edit", state="normal")
        self.text_entry_trainer_name.config(state="normal")
        self.checkbox_double_battle.config(state="normal")

        for rb in self.radio_gender:
            rb.config(state="normal")

        for cb in trainer_ui_comboboxes:
            cb.config(state="readonly")

        for btn in trainer_ui_buttons:
            btn.config(state=tk.NORMAL)


    def enable_partymon_editing(self):
        ''' Enable all UI elements to edit trainer data. '''
        partymon_ui_comboboxes = [
            self.combobox_mon_species,
            self.combobox_trainer_class,
            self.combobox_mon_held_item,
        ] + self.combobox_mon_movements

        partymon_ui_spinners = [
            self.spinbox_mon_level,
            self.dict_spinboxes_ivs["HP"]
        ]

        if self.project_data.expansion:
            partymon_ui_comboboxes.append(self.combobox_mon_nature)
            partymon_ui_comboboxes.append(self.combobox_mon_ability)
            partymon_ui_spinners += self.dict_spinboxes_ivs["ATK"]
            partymon_ui_spinners += self.dict_spinboxes_ivs["DEF"]
            partymon_ui_spinners += self.dict_spinboxes_ivs["SPD"]
            partymon_ui_spinners += self.dict_spinboxes_ivs["SPATK"]
            partymon_ui_spinners += self.dict_spinboxes_ivs["SPDEF"]
            partymon_ui_spinners += self.dict_spinboxes_evs
        else:
            ivs_frame = self.dict_spinboxes_ivs["HP"].master
            for widget in ivs_frame.winfo_children():
                if isinstance(widget, ttk.Label) and widget.cget("text") == "HP:":
                    widget.config(text="Total:")

        self.checkbox_mon_default_moves.config(state="normal")

        for cb in partymon_ui_comboboxes:
            cb.config(state="readonly")

        for spinner in partymon_ui_spinners:
            spinner.config(state="normal")

        self.button_save_mon.config(state=tk.NORMAL)


    def check_expansion(self):
        if self.project_type == 'pokeemerald-expansion':
            return True
        else:
            return False


    def data_adquisition(self):
        ''' WIP '''
        # Load all necessary data from the project files to populate the UI elements.
        if self.project_type != 'pokeemerald-expansion':
            self.parse_repo_data = ParseRepoDataVanilla(self.project_path, self.project_files, self.project_type)
        else:
            self.parse_repo_data = ParseRepoDataExpansion(self.project_path, self.project_files, self.project_type)
        self.populate_listbox_trainers_id()
        self.populate_trainer_info()
        self.populate_item_list()
        self.populate_ai_flags()
        self.populate_species_list()
        self.populate_moves_list()
        # Only if the project is based on pokeemerald expansion
        if self.project_data.expansion:
            self.populate_nature_list()
        
        self.get_trainer_data_from_files()
        if self.listbox_trainers_id.size() > 0:
            self.listbox_trainers_id.select_set(0, 0)
            self.listbox_trainers_id.event_generate("<<ListboxSelect>>")


    def populate_listbox_trainers_id(self):
        ''' Populate the trainer ID listbox 'opponents' file. '''
        trainer_id_list = self.parse_repo_data.parse_opponents_file()

        for trainer_name in trainer_id_list:
            self.listbox_trainers_id.insert(tk.END, trainer_name)
    

    def populate_trainer_info(self):
        ''' Populate the trainer info comboboxes from constants/trainers.h file. '''
        trainer_info = self.parse_repo_data.parse_trainer_info_file()
        
        self.combobox_trainer_pic['values'] = trainer_info['TRAINER_PIC']
        self.combobox_trainer_class['values'] = trainer_info['TRAINER_CLASS']
        self.combobox_trainer_encounter_music['values'] = trainer_info['TRAINER_ENCOUNTER_MUSIC']


    def populate_item_list(self):
        ''' Populate the item comboboxes from constants/items.h file.'''
        item_id_list = self.parse_repo_data.parse_items_file()
        
        for combobox in self.list_combobox_trainer_item:
            combobox['values'] = item_id_list
            if item_id_list:
                combobox.set(item_id_list[0])
        
        self.combobox_mon_held_item['values'] = item_id_list
        if item_id_list:
            self.combobox_mon_held_item.set(item_id_list[0])


    def populate_ai_flags(self):
        ''' Populate the AI flags from constants/battle_ai.h file. '''
        ai_flag_id_list = self.parse_repo_data.parse_battle_ai_file()

        for flag in ai_flag_id_list:
            self.project_data.ai_flags.add_flag(flag)
        
        for i, flag in enumerate(self.project_data.ai_flags.flags):
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(self.tab_trainer_ai_flags, text=flag[10:], variable=var)
            checkbox.grid(row=1 + i//2, column=i%2, sticky="w", padx=2, pady=1)
            self.list_ai_flag.append((flag, var))
        
        if self.project_data.expansion:
            self.combobox_ai_flags_presets.config(state="readonly")
            self.button_apply_ai_flags_preset.config(state="normal")


    def populate_species_list(self):
        ''' Populate the trainer info comboboxes from constants/species.h file. '''
        species_id_list = self.parse_repo_data.parse_species_file()
        
        self.combobox_mon_species['values'] = species_id_list
    

    def populate_moves_list(self):
        ''' Populate the trainer info comboboxes from constants/moves.h file. '''
        move_id_list = self.parse_repo_data.parse_moves_file()
        
        for cb in self.combobox_mon_movements:
            cb['values'] = move_id_list


    def populate_nature_list(self):
        ''' Populate the trainer info comboboxes from constants/pokemon.h file. '''
        natures_id_list = []

        with open(os.path.join(self.project_path, self.project_files["natures"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define NATURE_"):
                nature_id = line.split()[1]
                natures_id_list.append(nature_id)
        
        self.combobox_mon_nature['values'] = natures_id_list


    def get_trainer_data_from_files(self):
        ''' Get the trainer info from project_files file and process it to self.project_data. '''
        self.trainer_pics = self.parse_repo_data.parse_trainer_pic_files()
        self.mon_pics = self.parse_repo_data.parse_mon_pic_files()
        self.project_data.trainers = self.parse_repo_data.parse_trainer_data_file(self.project_data.ai_flags, self.list_gender_options)


    def update_trainer_fields_trigger(self, event):
        ''' Update the trainer fields in the UI with the data from self.current_trainer.'''
        selected_idx = self.listbox_trainers_id.curselection()
        if selected_idx:
            self.current_trainer_id = self.get_trainer_from_selected_id(selected_idx[0] + 1) # +1 to skip TRAINER_NONE
            self.update_trainer_fields(self.current_trainer_id)
            if self.listbox_mons_in_party.size() > 0:
                self.listbox_mons_in_party.select_set(0, 0)
                self.listbox_mons_in_party.event_generate("<<ListboxSelect>>")


    def update_trainer_fields(self, trainer_id):
        '''
        Updates the trainer fields in the UI with the data from the selected trainer.

        Sets all relevant widgets (ID, name, gender, picture, class, encounter music, double battle, party, items, and AI flags)
        to reflect the current state of the trainer with the given ID.
        '''
        # Insert the ID
        self.text_entry_trainer_id.config(state="normal")
        self.text_entry_trainer_id.delete(0, tk.END)
        self.text_entry_trainer_id.insert(0, self.project_data.trainers[trainer_id].id)
        self.text_entry_trainer_id.config(state="readonly")
        # Insert the name
        self.text_entry_trainer_name.delete(0, tk.END)
        self.text_entry_trainer_name.insert(0, self.project_data.trainers[trainer_id].name)
        # Set the gender
        self.current_trainer_gender_var.set(self.project_data.trainers[trainer_id].gender)
        for i, opt in enumerate(self.list_gender_options):
            self.radio_gender[i].config(variable=self.current_trainer_gender_var, value=opt)
        # Set the trainer pic
        self.set_trainer_pic(self.project_data.trainers[trainer_id].trainer_pic)
        # Set the trainer class
        self.combobox_trainer_class.set(self.project_data.trainers[trainer_id].trainer_class)
        # Set the encounter music
        self.combobox_trainer_encounter_music.set(self.project_data.trainers[trainer_id].encounter_music)
        # Set the double battle checkbox
        self.bool_double_battle.set(self.project_data.trainers[trainer_id].double_battle)
        # Set the party list
        self.update_party_list(trainer_id)

        # Set the items
        for i in range(4):
            if i < len(self.project_data.trainers[trainer_id].items):
                self.list_combobox_trainer_item[i].set(self.project_data.trainers[trainer_id].items[i])
        
        # Set the AI flags
        for flag, var in self.list_ai_flag:
            flag_exists = False
            for trainer_flag in self.project_data.trainers[trainer_id].ai_flags:
                if flag == trainer_flag:
                    flag_exists = True
                else:
                    flag_exists = flag_exists or False

            var.set(flag_exists)


    def update_party_list(self, trainer_id):
        '''
        Updates the party listbox with the Pokémon species of the selected trainer.

        Clears the current list and inserts each Pokémon species from the trainer's party.
        '''
        self.listbox_mons_in_party.delete(0, tk.END)
        for mon in self.project_data.trainers[trainer_id].pokemon:
            self.listbox_mons_in_party.insert(tk.END, mon.species)


    def update_mon_fields_trigger(self, event):
        '''
        Updates the UI fields with the data of the selected Pokémon in the trainer's party.

        Sets species, picture, level, held item, moves, and IVs for the selected Pokémon.
        '''
        selected_idx = self.listbox_mons_in_party.curselection()
        if selected_idx:
            self.current_trainer_mon = self.get_mon_from_selected_id(selected_idx[0])
            self.update_mon_fields(self.current_trainer_mon)


    def update_mon_fields(self, mon_id):
        '''
        Updates the UI fields with the data of the selected Pokémon in the trainer's party.

        Sets species, picture, level, held item, moves, and IVs for the selected Pokémon.
        '''
        # Set the mon species
        self.combobox_mon_species.set(self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].species)
        # Set the mon pic
        self.set_mon_pic(self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].species)
        # Set the level
        self.spinbox_mon_level.delete(0, tk.END)
        self.spinbox_mon_level.insert(0, self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].level)
        # Set the held item
        self.combobox_mon_held_item.set(self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].held_item)
        # Set the moves
        if self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].moves == ['MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE']:
            self.bool_mon_default_moves.set(True)
        else:
            self.bool_mon_default_moves.set(False)
        
        for i in range(4):
            self.combobox_mon_movements[i].set(self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].moves[i])
        # Set the IVs
        self.dict_spinboxes_ivs['HP'].delete(0, tk.END)
        self.dict_spinboxes_ivs['HP'].insert(0, self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].iv)


    def get_trainer_from_selected_id(self, id):
        '''
        This function does innecessary operations to get the same ID it's provided, just because using the selected index
        will make the program crazy. TkInter uses the same focus for both listboxes, so somehow they collide and gets
        changed in runtime. We better use this functions to get a constant integer as ID.
        '''
        index = 0
        trainer_id = self.project_data.trainers[id].id
        for trainer in self.project_data.trainers:
            if trainer_id == trainer.id:
                return index
            else:
                index += 1
    

    def get_mon_from_selected_id(self, id):
        '''
        Returns the index of the Pokémon in the party corresponding to the given ID.

        Used to map the selected index from the party listbox to the actual Pokémon index.
        '''
        for i in range(6):
            if id == i:
                return i


    def set_trainer_pic_trigger(self, event):
        '''
        Handles the event when a new trainer picture is selected from the combobox.

        Updates the trainer picture displayed in the UI.
        '''
        trainer_pic_id = self.combobox_trainer_pic.get()
        self.set_trainer_pic(trainer_pic_id)


    def set_trainer_pic(self, trainer_pic_id):
        '''
        Updates the trainer picture displayed in the UI.
        '''
        self.combobox_trainer_pic.set(trainer_pic_id)
        try:
            pic_dir = os.path.join(self.project_path, self.get_trainer_pic_path_from_id(trainer_pic_id))
            img_path = pic_dir if os.path.exists(pic_dir) else TRAINER_PIC_PLACEHOLDER
            self.photoimage_trainer_pic.config(file=img_path)
        except Exception:
            pass


    def get_trainer_pic_path_from_id(self, id):
        '''
        Returns the file path for the trainer picture corresponding to the given trainer picture ID.

        Searches the loaded trainer pictures for a matching ID and returns its path.
        '''
        for pic in self.trainer_pics:
            if pic['id'] == id:
                return pic['path']


    def set_mon_pic_trigger(self, event):
        '''
        Handles the event when a new Pokémon species is selected from the combobox.

        Updates the Pokémon picture displayed in the UI.
        '''
        mon_species = self.combobox_mon_species.get()
        self.set_mon_pic(mon_species)


    def set_mon_pic(self, mon_species):
        '''
        Updates the Pokémon picture displayed in the UI.

        Sets the Pokémon picture based on the given species. If the image is not found, uses a placeholder.
        '''
        try:
            pic_dir = self.get_mon_pic_path_from_species(mon_species)
            if pic_dir != None and pic_dir != '':
                full_pic_dir = os.path.join(self.project_path, pic_dir)
                img_path = full_pic_dir
            else:
                img_path = MON_PIC_PLACEHOLDER
            self.photoimage_mon_pic.config(file=img_path, height=64, width=64)
        except Exception:
            pass


    def set_default_moves(self):
        '''
        Sets all move comboboxes to "MOVE_NONE" if the default moves checkbox is selected.

        This method is used to quickly reset the moves of the selected Pokémon to their default state.
        '''
        if self.bool_mon_default_moves.get() == 1:
            for move in self.combobox_mon_movements:
                move.set("MOVE_NONE")
    

    def uncheck_default_moves(self, event):
        '''
        Unchecks the "Default moves" checkbox if any move combobox is set to a value other than "MOVE_NONE".

        If all move comboboxes are set to "MOVE_NONE", the checkbox is checked.
        '''
        is_default = True
        for move in self.combobox_mon_movements:
            if move.get() != "MOVE_NONE":
                self.bool_mon_default_moves.set(0)
                is_default = False
        if is_default:
            self.bool_mon_default_moves.set(1)


    def get_mon_pic_path_from_species(self, species):
        '''
        Returns the file path for the Pokémon picture corresponding to the given species.

        Searches the loaded Pokémon pictures for a matching species and returns its path.
        '''
        for pic in self.mon_pics:
            if pic['species'] == species:
                return pic['path']


    def save_mon_object(self):
        '''
        Saves the current Pokémon's data from the UI fields to the trainer's party.

        Updates species, level, held item, moves, and IVs for the selected Pokémon.
        Handles expansion-specific fields if applicable.
        '''
        mon = self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
        mon.species = self.combobox_mon_species.get()
        mon.level = int(self.spinbox_mon_level.get())
        mon.held_item = self.combobox_mon_held_item.get()
        for move_index in range(0,4):
            mon.moves[move_index] = self.combobox_mon_movements[move_index].get()

        if self.check_expansion():
            mon.ivs = None
            mon.evs = None
            mon.nature = None
            mon.ability = None
        else:
            mon.iv = int(self.dict_spinboxes_ivs['HP'].get())

        self.update_party_list(self.current_trainer_id)


    def add_party_mon(self):
        '''
        Adds a new Pokémon to the current trainer's party if there are fewer than six.

        The new Pokémon is initialized as a Bulbasaur by default and the party list is updated.
        '''
        if len(self.project_data.trainers[self.current_trainer_id].pokemon) < 6:
            new_mon = Pokemon("SPECIES_BULBASAUR")
            self.project_data.trainers[self.current_trainer_id].pokemon.append(new_mon)
            self.update_party_list(self.current_trainer_id)

    
    def del_party_mon(self):
        '''
        Removes the currently selected Pokémon from the trainer's party if more than one remains.

        Updates the party list and selects the first Pokémon in the list after removal.
        '''
        if len(self.project_data.trainers[self.current_trainer_id].pokemon) > 1:
            self.project_data.trainers[self.current_trainer_id].pokemon.remove(self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon])
            self.update_party_list(self.current_trainer_id)
            self.listbox_mons_in_party.selection_set(0, 0)
            self.listbox_mons_in_party.event_generate("<<ListboxSelect>>")
    

    def move_up_party_mon(self):
        '''
        Moves the currently selected Pokémon one position up in the trainer's party list.

        Updates the party list and selection accordingly.
        '''
        if len(self.project_data.trainers[self.current_trainer_id].pokemon) > 1:
            if self.current_trainer_mon > 0:
                mon = self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
                self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
                self.project_data.trainers[self.current_trainer_id].pokemon.remove(self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon])
                self.project_data.trainers[self.current_trainer_id].pokemon.insert(self.current_trainer_mon - 1, mon)
                self.update_party_list(self.current_trainer_id)
                self.listbox_mons_in_party.selection_set(self.current_trainer_mon - 1, self.current_trainer_mon - 1)
                self.listbox_mons_in_party.event_generate("<<ListboxSelect>>")


    def move_down_party_mon(self):
        '''
        Moves the currently selected Pokémon one position down in the trainer's party list.

        Updates the party list and selection accordingly.
        '''
        if len(self.project_data.trainers[self.current_trainer_id].pokemon) > 1:
            if self.current_trainer_mon < 5:
                mon = self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
                self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
                self.project_data.trainers[self.current_trainer_id].pokemon.remove(self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon])
                self.project_data.trainers[self.current_trainer_id].pokemon.insert(self.current_trainer_mon + 1, mon)
                self.update_party_list(self.current_trainer_id)
                if self.current_trainer_mon + 1 < len(self.project_data.trainers[self.current_trainer_id].pokemon):
                    self.listbox_mons_in_party.selection_set(self.current_trainer_mon + 1, self.current_trainer_mon + 1)
                else:
                    self.listbox_mons_in_party.selection_set(len(self.project_data.trainers[self.current_trainer_id].pokemon) - 1, len(self.project_data.trainers[self.current_trainer_id].pokemon) - 1)
                self.listbox_mons_in_party.event_generate("<<ListboxSelect>>")


    def save_trainer_object(self):
        '''
        Saves the current trainer's data from the UI fields to the trainer object.

        Updates name, class, picture, encounter music, gender, double battle flag, items, and AI flags.
        '''
        trainer = self.project_data.trainers[self.current_trainer_id]
        trainer.name = self.text_entry_trainer_name.get()
        trainer.trainer_class = self.combobox_trainer_class.get()
        trainer.trainer_pic = self.combobox_trainer_pic.get()
        trainer.encounter_music = self.combobox_trainer_encounter_music.get()
        trainer.gender = 'MALE' if self.current_trainer_gender_var == self.list_gender_options[0] else 'FEMALE'
        trainer.double_battle = True if self.bool_double_battle.get() == True else False
        
        trainer_items = []
        for item in self.list_combobox_trainer_item:
            trainer_items.append(item.get())
        trainer.items = trainer_items

        trainer_ai_flags = []

        for flag in self.list_ai_flag:
            if flag[1].get() == True:
                trainer_ai_flags.append(flag[0])

        trainer.ai_flags = trainer_ai_flags
        # trainer.party_name =
        trainer.maps = []


    def find_trainer_in_maps(self):
        '''
        Searches for the current trainer's ID in map script files and updates the UI with the locations found.

        Populates the listbox with all maps where the trainer battle is referenced.
        '''
        trainer = self.project_data.trainers[self.current_trainer_id]
        maps_found = self.parse_repo_data.parse_data_inc_files_for_trainerbattle(trainer.id)
        self.listbox_trainer_map_appereances.delete(0, tk.END)
        for map in maps_found:
            self.listbox_trainer_map_appereances.insert(tk.END, map)

    def show_about_dialog(self):
        '''
        Displays the "About" dialog with information about the application.
        '''
        messagebox.showinfo(title="About Decomp Trainer Editor", message="Decomp Trainer Editor\n\nA simple GUI application to edit trainer data in decompiled Pokémon GBA games.\n\nDeveloped by Excmojack.\n\n2025 © All rights reserved.\n\nVersion 0.1.0: Released 20th December 2025")


    def launch_documentation(self):
        '''
        Opens the default web browser to the application's documentation page.
        '''
        import webbrowser
        webbrowser.open_new_tab("https://github.com/ExcmoJack/decomp_trainer_editor/blob/main/README.md")

if __name__ == "__main__":
    app = App()
    app.mainloop()

