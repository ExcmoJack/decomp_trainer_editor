#! /usr/bin/env python3

import tkinter as tk
import os
from modules.classes import Trainer, Pokemon, AiFlagList
from modules.ProjectSelection import ask_project
from modules.SaveTrainerData import *
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
    def __init__(self):
        self.trainers = []
        self.expansion = False
        self.ai_flags = AiFlagList()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.init_window_data()    

    def init_window_data(self):
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
        help_menu.add_command(label="Documentation")
        help_menu.add_command(label="About")

        # Adding all menus to the menubar and configuring the root window to use it
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Edit", menu=edit_menu, state=tk.DISABLED)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=self.menubar)


    def create_window_layout(self):
        # The main windows layout is divided in 3 columns. One will permit to select the trainer to edit,
        # the second will show trainer general info and the third will show the selected Pokémon info from the party.
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        ##############################
        # COLUMN 1 - Trainer ID List #
        ##############################

        # Trainer list container. It will have a fixed width and scrollbars as the ID don't use to be too long.
        col1_kwargs = {"width": 340,"bd": 2, "relief": tk.GROOVE}
        col1 = tk.Frame(self.main_frame, **col1_kwargs)
        col1.pack(side=tk.LEFT, fill=tk.Y)
        col1.pack_propagate(False)
        # Trainer list container set up.
        listbox_frame = tk.Frame(col1)
        listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Internal frame to hold the listbox and the horizontal scrollbar below it
        listbox_pack_frame = tk.Frame(listbox_frame)
        listbox_pack_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_trainers_id = tk.Listbox(listbox_pack_frame, selectmode=tk.SINGLE)
        self.listbox_trainers_id.bind("<<ListboxSelect>>", self.update_trainer_fields_trigger)
        scrollbar_x = tk.Scrollbar(listbox_pack_frame, orient=tk.HORIZONTAL, command=self.listbox_trainers_id.xview)
        self.listbox_trainers_id.config(xscrollcommand=scrollbar_x.set)
        self.listbox_trainers_id.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar_x.pack(side=tk.TOP, fill=tk.X)
        # Add vertical scrollbar to the right of the listbox
        scrollbar_y = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.listbox_trainers_id.yview)
        self.listbox_trainers_id.config(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        ############################
        # COLUMN 2 - Trainer Setup #
        ############################

        # Trainer info container. Info is supposed to be updated when selecting a trainer from the listbox. Maybe lacks of a save button?
        col2_kwargs = {"bd": 2, "relief": tk.GROOVE}
        col2 = tk.Frame(self.main_frame, **col2_kwargs)
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.gender_options = ["MALE", "FEMALE"]

        # Show trainer picture at the top left
        try:
            self.trainer_img = tk.PhotoImage(file=(TRAINER_PIC_PLACEHOLDER))
            img_label = ttk.Label(col2, image=self.trainer_img)
            img_label.grid(row=0, column=0, rowspan=2)
        except Exception:
            # In case the image is not found or can't be loaded, show a blank canvas instead
            self.trainer_canvas = tk.Canvas(col2, width=64, height=64, bg="#cccccc", highlightthickness=0)
            self.trainer_canvas.grid(row=0, column=0, rowspan=2)

        # Trainer ID and Name showed at the top right. Think about letting modify the ID.
        # Maybe let be editable after clicking a button or the field itself. Read only by now.
        row = 0
        self.id_entry = ttk.Entry(col2)
        self.id_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.id_entry.config(state='readonly')
        row += 1

        self.name_entry = ttk.Entry(col2)
        self.name_entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.name_entry.config(state='readonly')
        row += 1

        # Radio buttons for gender. This will be saved in self.current_trainer_gender_var.
        self.current_trainer_gender_var = tk.StringVar(value=self.gender_options[0])
        gender_frame = ttk.Frame(col2)
        gender_frame.grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=2)
        self.radio_gender = []
        for i, opt in enumerate(self.gender_options):
            rb = ttk.Radiobutton(gender_frame, text=opt, variable=self.current_trainer_gender_var, value=opt, state="disabled")
            self.radio_gender.append(rb)
            rb.pack(side=tk.LEFT, padx=5)
        row += 1

        # Combobox for each remaining field. Empty values by default before loading a project.
        ttk.Label(col2, text="Trainer Pic:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.trainer_pic_cb = ttk.Combobox(col2, values=[], state="disabled")
        self.trainer_pic_cb.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        self.trainer_pic_cb.bind("<<ComboboxSelected>>", self.set_trainer_pic_trigger)
        row += 1

        ttk.Label(col2, text="Trainer Class:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.trainer_class_cb = ttk.Combobox(col2, values=[], state="disabled")
        self.trainer_class_cb.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        row += 1

        ttk.Label(col2, text="Encounter Music:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.encounter_music_cb = ttk.Combobox(col2, values=[], state="disabled")
        self.encounter_music_cb.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        row += 1

        self.double_battle_var = tk.BooleanVar(value=False)
        self.double_battle_check = ttk.Checkbutton(col2, text="Double Battle", variable=self.double_battle_var, state="disabled")
        self.double_battle_check.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        row += 1

        # Here we will have a tabbed notebook with 3 tabs: Pokémon & Items, AI Flags and Places where the trainer battle is found.
        # It is important to pay attention to this part as it is the most complex of the UI.
        tabbed_notebook = ttk.Notebook(col2)
        tabbed_notebook.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        # ------------------- #
        # Party and Items tab #
        # ------------------- #
        party_items_tab = ttk.Frame(tabbed_notebook)
        tabbed_notebook.add(party_items_tab, text="Party and Items")

        # Party and Items container. It will have two columns: Party on the left and Items on the right.
        poke_items_frame = ttk.Frame(party_items_tab)
        poke_items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # In the first column we will have the party listbox and buttons below it.
        party_frame = ttk.Frame(poke_items_frame)
        party_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 20))

        # Here we have the party listbox. It is supposed to be populated with the Pokémon species in the party.
        # Always with the limit of 6 Pokémon in the party.
        ttk.Label(party_frame, text="Party").pack(anchor="w", pady=(0, 5))
        self.party_listbox = tk.Listbox(party_frame, height=6)
        self.party_listbox.pack(fill=tk.BOTH, expand=True)
        self.party_listbox.bind("<<ListboxSelect>>", self.update_mon_fields_trigger)


        # Now this buttons may allow to move up/down the selected Pokémon in the party, add a new one or remove the selected one.
        # They must be disabled if there is no project opened.
        btns_frame = ttk.Frame(party_frame)
        btns_frame.pack(fill=tk.X, pady=(8, 0))
        self.party_button_up     = ttk.Button(btns_frame, text="Up", state=tk.DISABLED, command=self.move_up_party_mon)
        self.party_button_down   = ttk.Button(btns_frame, text="Down", state=tk.DISABLED, command=self.move_down_party_mon)
        self.party_button_add    = ttk.Button(btns_frame, text="Add", state=tk.DISABLED, command=self.add_party_mon)
        self.party_button_remove = ttk.Button(btns_frame, text="Remove", state=tk.DISABLED, command=self.del_party_mon)

        self.party_button_up.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.party_button_down.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.party_button_remove.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.party_button_add.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # The second column will have the four items comboboxes.
        items_frame = ttk.Frame(poke_items_frame)
        items_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(items_frame, text="Items").pack(anchor="w", pady=(0, 5))

        # In this case we will define the items as a list of comboboxes.
        self.item_cbs = []
        for i in range(4):
            cb = ttk.Combobox(items_frame, values=[], state="disabled")
            cb.pack(fill=tk.X, pady=2)
            self.item_cbs.append(cb)

        poke_items_frame.columnconfigure(1, weight=1)

        # -------------------- #
        # Trainer AI flags tab #
        # -------------------- #
        self.ai_tab = ttk.Frame(tabbed_notebook)
        tabbed_notebook.add(self.ai_tab, text="AI Flags")
        self.ai_flag_vars = []
        # In pokeemerald expansion there are some presets for AI flags. We will add a combobox to select one and a button to apply them
        # only if the project is based on pokeemerald expansion. Currently always shown as we don't detect the project type.
        preset_frame = ttk.Frame(self.ai_tab)
        preset_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(preset_frame, text="Preset:").pack(side=tk.LEFT, padx=(0, 5))
        self.preset_cb = ttk.Combobox(preset_frame, values=["Basic Trainer", "Smart Trainer", "Predict"], state="disabled")
        self.preset_cb.pack(side=tk.LEFT, padx=(0, 5))
        self.apply_btn = ttk.Button(preset_frame, text="Apply", state=tk.DISABLED)
        self.apply_btn.pack(side=tk.LEFT)
        
        # ---------- #
        # Places tab #
        # ---------- #
        place_tab = ttk.Frame(tabbed_notebook)
        tabbed_notebook.add(place_tab, text="Found at...")
        # List of maps where the trainer battle is found.
        # The idea is to scan all /data/maps/scripts.inc to find all ocurrences of the trainer ID. Pending implementation.
        ttk.Label(place_tab, text="Maps where the trainer was found").pack(anchor="w", pady=(10, 5), padx=10)
        self.places_listbox = tk.Listbox(place_tab, height=8)
        self.places_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        row += 1

        self.save_trainer_button = ttk.Button(col2, text="Save Trainer", state=tk.DISABLED, command=self.save_trainer_data)
        self.save_trainer_button.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        ####################################
        # COLUMN 3 - Pokemon configuration #
        ####################################
        col3_kwargs = {"bd": 2, "relief": tk.GROOVE}
        col3 = tk.Frame(self.main_frame, **col3_kwargs)
        col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Data container for all Pokémon fields. Comboboxes to be populated at project load. Individual Pokémon data
        # to be loaded when selecting a Pokémon from the party listbox.
        poke_fields_frame = ttk.Frame(col3)
        poke_fields_frame.pack(pady=10, padx=20, fill=tk.X)

        # Show mon picture at the top. If the image can't be loaded, show a blank canvas instead.
        try:
            self.mon_img = tk.PhotoImage(file=MON_PIC_PLACEHOLDER)
            mon_img_label = ttk.Label(poke_fields_frame, image=self.mon_img)
            mon_img_label.grid(row=0, column=0, columnspan=2)
        except Exception:
            mon_canvas = tk.Canvas(poke_fields_frame, width=64, height=64, bg="#cccccc", highlightthickness=0)
            mon_canvas.grid(row=0, column=0, columnspan=2)

        # Species
        ttk.Label(poke_fields_frame, text="Species:").grid(row=1, column=0, sticky="w", pady=4)
        self.species_cb = ttk.Combobox(poke_fields_frame, values=[], state="disabled")
        self.species_cb.grid(row=1, column=1, sticky="ew", pady=4)
        self.species_cb.bind("<<ComboboxSelected>>", self.set_mon_pic_trigger)

        # Level
        ttk.Label(poke_fields_frame, text="Level:").grid(row=2, column=0, sticky="w", pady=4)
        self.level_sb = tk.Spinbox(poke_fields_frame, from_=1, to=100, width=5, state="disabled")
        self.level_sb.grid(row=2, column=1, sticky="w", pady=4)

        # Held Item
        ttk.Label(poke_fields_frame, text="Held Item:").grid(row=3, column=0, sticky="w", pady=4)
        self.held_item_cb = ttk.Combobox(poke_fields_frame, values=[], state="disabled")
        self.held_item_cb.grid(row=3, column=1, sticky="ew", pady=4)

        # Ability
        ttk.Label(poke_fields_frame, text="Ability:").grid(row=4, column=0, sticky="w", pady=4)
        self.ability_cb = ttk.Combobox(poke_fields_frame, values=["RANDOM", "FIRST", "SECOND", "HIDDEN"], state="disabled")
        self.ability_cb.grid(row=4, column=1, sticky="ew", pady=4)

        # Nature
        ttk.Label(poke_fields_frame, text="Nature:").grid(row=5, column=0, sticky="w", pady=4)
        self.nature_cb = ttk.Combobox(poke_fields_frame, values=[], state="disabled")
        self.nature_cb.grid(row=5, column=1, sticky="ew", pady=4)

        # Moves
        ttk.Label(poke_fields_frame, text="Moves:").grid(row=6, column=0, sticky="w", pady=(12, 4))
        # Moves label and "Default moves" checkbox side by side in a frame
        moves_label_frame = ttk.Frame(poke_fields_frame)
        moves_label_frame.grid(row=6, column=0, columnspan=2, sticky="w", pady=(12, 4))
        ttk.Label(moves_label_frame, text="Moves:").pack(side=tk.LEFT)
        self.default_moves_var = tk.BooleanVar(value=False)
        self.default_moves_check = ttk.Checkbutton(moves_label_frame, text="Default moves", variable=self.default_moves_var, state="disabled", command=self.set_default_moves)
        self.default_moves_check.pack(side=tk.LEFT, padx=10)
        self.move_cbs = []
        for i in range(4):
            cb = ttk.Combobox(poke_fields_frame, values=[], state="disabled", width=16)
            cb.grid(row=7 + i, column=0, sticky="ew", pady=2, columnspan=2)
            cb.bind('<<ComboboxSelected>>', self.uncheck_default_moves)
            self.move_cbs.append(cb)

        # IVs
        ttk.Label(poke_fields_frame, text="IVs:").grid(row=21, column=0, sticky="w", pady=(12, 4), columnspan=4)
        ivs_frame = ttk.Frame(poke_fields_frame)
        ivs_frame.grid(row=22, column=0, columnspan=4, sticky="w")
        self.ivs_spinboxes = {}
        iv_stats = ["HP", "ATK", "DEF", "SPD", "SPATK", "SPDEF"]
        for idx, stat in enumerate(iv_stats):
            col = 0 if idx < 3 else 1
            row = idx % 3
            ttk.Label(ivs_frame, text=stat+":").grid(row=row, column=col*2, sticky="e", padx=(6,1))
            sb = tk.Spinbox(ivs_frame, from_=0, to=31, width=5, state="disabled")
            sb.grid(row=row, column=col*2+1, sticky="w", pady=2)
            self.ivs_spinboxes[stat] = sb

        # EVs
        ttk.Label(poke_fields_frame, text="EVs:").grid(row=31, column=0, sticky="w", pady=(12, 4), columnspan=4)
        evs_frame = ttk.Frame(poke_fields_frame)
        evs_frame.grid(row=32, column=0, columnspan=4, sticky="w")
        self.evs_spinboxes = {}
        for idx, stat in enumerate(iv_stats):
            col = 0 if idx < 3 else 1
            row = idx % 3
            ttk.Label(evs_frame, text=stat+":").grid(row=row, column=col*2, sticky="e", padx=(6,1))
            sb = tk.Spinbox(evs_frame, from_=0, to=255, width=5, state="disabled")
            sb.grid(row=row, column=col*2+1, sticky="w", pady=2)
            self.evs_spinboxes[stat] = sb

        self.save_mon_button = ttk.Button(poke_fields_frame, text="Save Pokémon", state=tk.DISABLED, command=self.save_mon_data)
        self.save_mon_button.grid(row=33, column=0, columnspan=4, pady=6)

        poke_fields_frame.columnconfigure(1, weight=1)


    def create_status_bar(self):
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
                messagebox.showinfo(message="Could not identify the project type. Try opening another folder.", icon='warning')
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
                except:
                    messagebox(message="Could not identify the project type. Try opening another folder.", icon='warning')


    def save_project(self):
        save_obj = TrainerDataFile(self.project_data.trainers, self.project_type)
        save_obj.init_file()
        save_obj.create_files(os.path.join(get_current_directory(), "assets"))
    

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
            self.trainer_pic_cb,
            self.trainer_class_cb,
            self.encounter_music_cb,
        ] + self.item_cbs

        trainer_ui_buttons = [
            self.party_button_up,
            self.party_button_down,
            self.party_button_add,
            self.party_button_remove,
            self.save_trainer_button
        ]

        self.file_menu.entryconfig(1, state=tk.NORMAL)
        self.menubar.entryconfig("Edit", state="normal")
        self.name_entry.config(state="normal")
        self.double_battle_check.config(state="normal")

        for rb in self.radio_gender:
            rb.config(state="normal")

        for cb in trainer_ui_comboboxes:
            cb.config(state="readonly")

        for btn in trainer_ui_buttons:
            btn.config(state=tk.NORMAL)


    def enable_partymon_editing(self):
        ''' Enable all UI elements to edit trainer data. '''
        partymon_ui_comboboxes = [
            self.species_cb,
            self.trainer_class_cb,
            self.held_item_cb,
        ] + self.move_cbs

        partymon_ui_spinners = [
            self.level_sb,
            self.ivs_spinboxes["HP"]
        ]

        if self.project_data.expansion:
            partymon_ui_comboboxes.append(self.nature_cb)
            partymon_ui_comboboxes.append(self.ability_cb)
            partymon_ui_spinners += self.ivs_spinboxes["ATK"]
            partymon_ui_spinners += self.ivs_spinboxes["DEF"]
            partymon_ui_spinners += self.ivs_spinboxes["SPD"]
            partymon_ui_spinners += self.ivs_spinboxes["SPATK"]
            partymon_ui_spinners += self.ivs_spinboxes["SPDEF"]
            partymon_ui_spinners += self.evs_spinboxes
        else:
            ivs_frame = self.ivs_spinboxes["HP"].master
            for widget in ivs_frame.winfo_children():
                if isinstance(widget, ttk.Label) and widget.cget("text") == "HP:":
                    widget.config(text="Total:")

        self.default_moves_check.config(state="normal")

        for cb in partymon_ui_comboboxes:
            cb.config(state="readonly")

        for spinner in partymon_ui_spinners:
            spinner.config(state="normal")

        self.save_mon_button.config(state=tk.NORMAL)


    def check_expansion(self):
        ''' Check if the project is based on pokeemerald expansion. WIP. '''
        pass


    def data_adquisition(self):
        ''' WIP '''
        # Load all necessary data from the project files to populate the UI elements.
        self.populate_trainer_list()
        self.populate_trainer_info()
        self.populate_item_list()
        self.populate_ai_flags()
        self.populate_species_list()
        self.populate_moves_list()
        self.get_trainer_pic_list()
        self.get_mon_pic_list()
        # Only if the project is based on pokeemerald expansion
        if self.project_data.expansion:
            self.populate_nature_list()
        
        self.get_trainer_data()
        if self.listbox_trainers_id.size() > 0:
            self.listbox_trainers_id.select_set(0, 0)
            self.listbox_trainers_id.event_generate("<<ListboxSelect>>")


    def populate_trainer_list(self):
        ''' Populate the trainer ID listbox from constants/opponents.h file. '''
        trainer_id_list = []

        with open(os.path.join(self.project_path, self.project_files["opponents"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define TRAINER_"):
                trainer_name = line.split()[1]
                trainer_id_list.append(trainer_name)

        trainer_id_list = trainer_id_list[1:] # Remove TRAINER_NONE

        for trainer_name in trainer_id_list:
            self.listbox_trainers_id.insert(tk.END, trainer_name)
    

    def populate_trainer_info(self):
        ''' Populate the trainer info comboboxes from constants/trainers.h file. '''
        trainer_pic_id_list = []
        trainer_class_id_list = []
        encounter_music_id_list = []

        with open(os.path.join(self.project_path, self.project_files["trainer_info"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define TRAINER_PIC_"):
                trainer_pic_id = line.split()[1]
                trainer_pic_id_list.append(trainer_pic_id)
            elif line.startswith("#define TRAINER_CLASS_"):
                trainer_class_id = line.split()[1]
                trainer_class_id_list.append(trainer_class_id)
            elif line.startswith("#define TRAINER_ENCOUNTER_MUSIC_"):
                trainer_encounter_music_id = line.split()[1]
                encounter_music_id_list.append(trainer_encounter_music_id)
        
        self.trainer_pic_cb['values'] = trainer_pic_id_list
        self.trainer_class_cb['values'] = trainer_class_id_list
        self.encounter_music_cb['values'] = encounter_music_id_list


    def populate_item_list(self):
        ''' Populate the item comboboxes from constants/items.h file.'''
        item_id_list = []

        with open(os.path.join(self.project_path, self.project_files["items"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        for line in full_content:
            if line.startswith("#define ITEM_"):
                item_id = line.split()[1]
                item_id_list.append(item_id)
            
        for line in full_content:
            if line.startswith("#define ITEMS_COUNT"):
                item_count = int(line.split()[2])
                item_id_list = item_id_list[:item_count]
        
        for cb in self.item_cbs:
            cb['values'] = item_id_list
            if item_id_list:
                cb.set(item_id_list[0])
        
        self.held_item_cb['values'] = item_id_list
        if item_id_list:
            self.held_item_cb.set(item_id_list[0])


    def populate_ai_flags(self):
        ''' Populate the AI flags from constants/battle_ai.h file. '''
        with open(os.path.join(self.project_path, self.project_files["battle_ai"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        ai_flag = None

        for line in full_content:
            if line.startswith("#define AI_SCRIPT_"):
                ai_flag = line.split()[1]
                self.project_data.ai_flags.add_flag(ai_flag)
                ai_flag = None
        
        for i, flag in enumerate(self.project_data.ai_flags.flags):
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(self.ai_tab, text=flag[10:], variable=var)
            checkbox.grid(row=1 + i//2, column=i%2, sticky="w", padx=2, pady=1)
            self.ai_flag_vars.append((flag, var))
        
        if self.project_data.expansion:
            self.preset_cb.config(state="readonly")
            self.apply_btn.config(state="normal")


    def populate_species_list(self):
        ''' Populate the trainer info comboboxes from constants/species.h file. '''
        species_id_list = []

        with open(os.path.join(self.project_path, self.project_files["species"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define SPECIES_"):
                species_id = line.split()[1]
                species_id_list.append(species_id)
        
        self.species_cb['values'] = species_id_list[1:] # Remove SPECIES_NONE
    

    def populate_moves_list(self):
        ''' Populate the trainer info comboboxes from constants/moves.h file. '''
        move_id_list = []

        with open(os.path.join(self.project_path, self.project_files["moves"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define MOVE_"):
                move_id = line.split()[1]
                move_id_list.append(move_id)
        
        for line in full_content:
            if line.startswith("#define MOVES_COUNT"):
                moves_count = int(line.split()[2])
                move_id_list = move_id_list[:moves_count]
        
        for cb in self.move_cbs:
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
        
        self.nature_cb['values'] = natures_id_list


    def get_trainer_pic_list(self):
        self.trainer_pics = []
        with open(os.path.join(self.project_path, self.project_files["trainer_pics_ptr"].lstrip("/")), "r") as f:
            full_content = f.readlines()
    
        for line in full_content:
            if line.strip().startswith('TRAINER_SPRITE'):
                data = line.strip()[15:-2]
                entry = data.split(', ')
                new_pic = {'id': 'TRAINER_PIC_' + entry[0], 'pointer': entry[1], 'path': ''}
                self.trainer_pics.append(new_pic)

        with open(os.path.join(self.project_path, self.project_files["trainer_pics_dir"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.strip().startswith('const u32 gTrainerFrontPic_'):
                dir_info = line.strip()[10:-3].replace('[]', '').replace('INCBIN_U32("', '').replace('.4bpp.lz', '.png').split(' = ')
                for pic in self.trainer_pics:
                    if pic['pointer'] == dir_info[0]:
                        pic['path'] = dir_info[1]
    

    def get_mon_pic_list(self):
        self.mon_pics = []
        with open(os.path.join(self.project_path, self.project_files["mon_pics_ptr"].lstrip("/")), "r") as f:
            full_content = f.readlines()
    
        for line in full_content:
            if line.strip().startswith('SPECIES_SPRITE('):
                data = line.strip()[15:-2].replace(' ', '')
                entry = data.split(',')
                new_pic = {'species': 'SPECIES_' + entry[0], 'pointer': entry[1], 'path': ''}
                self.mon_pics.append(new_pic)

        with open(os.path.join(self.project_path, self.project_files["mon_pics_dir"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.strip().startswith('const u32 gMonFrontPic_'):
                dir_info = line.strip()[10:-3].replace('[]', '').replace('INCBIN_U32("', '').replace('.4bpp.lz', '.png').split(' = ')
                for pic in self.mon_pics:
                    if pic['pointer'] == dir_info[0]:
                        if pic['species'] in ['SPECIES_CASTFORM']:
                            pic['path'] = ''
                            path_list = dir_info[1].split('/')
                            path_list.insert(-1, 'normal')
                            for item in path_list:
                                if item == path_list[0]:
                                    pic['path'] += item
                                else:
                                    pic['path'] += '/' + item
                        else:
                            pic['path'] = dir_info[1]


    def get_trainer_data(self):
        ''' Get the trainer info from data/trainers.h file and process it to self.project_data. '''

        with open(os.path.join(self.project_path, self.project_files["trainer_data"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        # .partyFlags - It will be adquired from party macros
        # .trainerClass
        # .encounterMusic_gender
        # .trainerPic
        # .trainerName
        # .items
        # .doubleBattle
        # .aiFlags
        # .partySize - It will be adquired from party macros
        # .party

        new_trainer = None
        for line in full_content:
            data = line.strip().split(" ")
            field = data[0]
            if field[:9] == '[TRAINER_':
                new_trainer = Trainer(line.strip().split(" ")[0][1:-1])
                uses_party_macro = True
            elif field == '.trainerClass':
                new_trainer.trainer_class = data[2].strip('",')
            elif field == '.encounterMusic_gender':
                new_trainer.gender = self.gender_options[0]
                for stuff in data[2:]:
                    if stuff.startswith("TRAINER_ENCOUNTER_MUSIC_"):
                        new_trainer.encounter_music = stuff.strip('",')
                    elif stuff == "F_TRAINER_FEMALE":
                        new_trainer.gender = self.gender_options[1]
            elif field == '.trainerPic':
                new_trainer.trainer_pic = data[2].strip('",')
            elif field == '.trainerName':
                new_trainer.name = line.split('"')[1]
            elif field == '.items':
                for item in data[2:]:
                    if item.strip('",{}') != '':
                        new_trainer.items.append(item.strip('",{}'))
                while len(new_trainer.items) < 4:
                    new_trainer.items.append('ITEM_NONE')
            elif field == '.doubleBattle':
                if data[2] == 'TRUE,':
                    new_trainer.double_battle = True
                else:
                    new_trainer.double_battle = False
            elif field == '.aiFlags':
                for flag in data[2:]:
                    if self.project_data.ai_flags.is_flag(flag.strip('",{}')):
                        new_trainer.ai_flags.append(flag.strip('",'))
            elif field == '.partyFlags':
                uses_party_macro = False
            elif field == '.partySize':
                uses_party_macro = False
            elif field == '.party':
                if uses_party_macro:
                    party_pointer = data[2].split('(')[1].strip('),')
                    new_trainer.party_name = party_pointer
                    new_trainer.pokemon = self.get_partymon_data(party_pointer)
            elif field == '},':
                self.project_data.trainers.append(new_trainer)
                new_trainer = None


    def get_partymon_data(self, pointer):
        ''' Get the party Pokémon data from data/trainer_parties.h file and process it to return as a Pokémon list. '''

        with open(os.path.join(self.project_path, self.project_files["trainer_parties"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        party = []
        new_mon = None
        
        party_pointer_found = False
        for line in full_content:
            data = line.strip().split(" ")
            field = data[0]
            if line.strip().startswith('static const struct') and (pointer + '[]') in line.split(" "):
                party_pointer_found = True
            if party_pointer_found:
                if field == '}' or field == '},':
                    new_mon = Pokemon(mon_struct['species'])
                    new_mon.level = int(mon_struct['lvl'])
                    new_mon.held_item = mon_struct['heldItem']
                    new_mon.iv = int(mon_struct['iv'])
                    new_mon.moves = mon_struct['moves']
                    party.append(new_mon)
                    new_mon = None
                    mon_struct = None
                if field == '{':
                    mon_struct = {
                        'iv': '', # Somehow up to 255
                        'lvl': '',
                        'species': '',
                        'heldItem': 'ITEM_NONE',
                        'moves': ['MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE']
                    }
                if field == '.iv':
                    mon_struct['iv'] = int(data[2].strip(','))
                if field == '.lvl':
                    mon_struct['lvl'] = int(data[2].strip(','))
                if field == '.species':
                    mon_struct['species'] = data[2].strip('",')
                if field == '.heldItem':
                    mon_struct['heldItem'] = data[2].strip('",')
                if field == '.moves':
                    moves = []
                    for move in data[2:]:
                        if move.strip('",{}') != '':
                            moves.append(move.strip('",{}'))
                    while len(moves) < 4:
                        moves.append('MOVE_NONE')
                    mon_struct['moves'] = moves
                if line.strip().startswith('};'):
                    party_pointer_found = False
    
        return party


    def update_trainer_fields_trigger(self, event):
        ''' Update the trainer fields in the UI with the data from self.current_trainer.'''
        selected_idx = self.listbox_trainers_id.curselection()
        if selected_idx:
            self.current_trainer_id = self.get_trainer_from_selected_id(selected_idx[0] + 1) # +1 to skip TRAINER_NONE
            self.update_trainer_fields(self.current_trainer_id)
            if self.party_listbox.size() > 0:
                self.party_listbox.select_set(0, 0)
                self.party_listbox.event_generate("<<ListboxSelect>>")


    def update_trainer_fields(self, trainer_id):
        # Insert the ID
        self.id_entry.config(state="normal")
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, self.project_data.trainers[trainer_id].id)
        self.id_entry.config(state="readonly")
        # Insert the name
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.project_data.trainers[trainer_id].name)
        # Set the gender
        self.current_trainer_gender_var.set(self.project_data.trainers[trainer_id].gender)
        for i, opt in enumerate(self.gender_options):
            self.radio_gender[i].config(variable=self.current_trainer_gender_var, value=opt)
        # Set the trainer pic
        self.set_trainer_pic(self.project_data.trainers[trainer_id].trainer_pic)
        # Set the trainer class
        self.trainer_class_cb.set(self.project_data.trainers[trainer_id].trainer_class)
        # Set the encounter music
        self.encounter_music_cb.set(self.project_data.trainers[trainer_id].encounter_music)
        # Set the double battle checkbox
        self.double_battle_var.set(self.project_data.trainers[trainer_id].double_battle)
        # Set the party list
        self.update_party_list(trainer_id)

        # Set the items
        for i in range(4):
            if i < len(self.project_data.trainers[trainer_id].items):
                self.item_cbs[i].set(self.project_data.trainers[trainer_id].items[i])
        
        # Set the AI flags
        for flag, var in self.ai_flag_vars:
            flag_exists = False
            for trainer_flag in self.project_data.trainers[trainer_id].ai_flags:
                if flag == trainer_flag:
                    flag_exists = True
                else:
                    flag_exists = flag_exists or False

            var.set(flag_exists)


    def update_party_list(self, trainer_id):
        self.party_listbox.delete(0, tk.END)
        for mon in self.project_data.trainers[trainer_id].pokemon:
            self.party_listbox.insert(tk.END, mon.species)


    def update_mon_fields_trigger(self, event):
        selected_idx = self.party_listbox.curselection()
        if selected_idx:
            self.current_trainer_mon = self.get_mon_from_selected_id(selected_idx[0])
            self.update_mon_fields(self.current_trainer_mon)


    def update_mon_fields(self, mon_id):
        # Set the mon species
        self.species_cb.set(self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].species)
        # Set the mon pic
        self.set_mon_pic(self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].species)
        # Set the level
        self.level_sb.delete(0, tk.END)
        self.level_sb.insert(0, self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].level)
        # Set the held item
        self.held_item_cb.set(self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].held_item)
        # Set the moves
        if self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].moves == ['MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE']:
            self.default_moves_var.set(True)
        else:
            self.default_moves_var.set(False)
        
        for i in range(4):
            self.move_cbs[i].set(self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].moves[i])
        # Set the IVs
        self.ivs_spinboxes['HP'].delete(0, tk.END)
        self.ivs_spinboxes['HP'].insert(0, self.project_data.trainers[self.current_trainer_id].pokemon[mon_id].iv)


    def get_trainer_from_selected_id(self, id):
        '''This function does innecessary operations to get the same ID it's provided, just because using the selected index
           will make the program crazy. TkInter uses the same focus for both listboxes, so somehow they collide and gets
           changed in runtime. We better use this functions to get a constant integer as ID.'''
        index = 0
        trainer_id = self.project_data.trainers[id].id
        for trainer in self.project_data.trainers:
            if trainer_id == trainer.id:
                return index
            else:
                index += 1
    

    def get_mon_from_selected_id(self, id):
        for i in range(6):
            if id == i:
                return i


    def set_trainer_pic_trigger(self, event):
        trainer_pic_id = self.trainer_pic_cb.get()
        self.set_trainer_pic(trainer_pic_id)


    def set_trainer_pic(self, trainer_pic_id):
        self.trainer_pic_cb.set(trainer_pic_id)
        try:
            pic_dir = os.path.join(self.project_path, self.get_trainer_pic_path_from_id(trainer_pic_id))
            img_path = pic_dir if os.path.exists(pic_dir) else TRAINER_PIC_PLACEHOLDER
            self.trainer_img.config(file=img_path)
        except Exception:
            pass


    def get_trainer_pic_path_from_id(self, id):
        for pic in self.trainer_pics:
            if pic['id'] == id:
                return pic['path']


    def set_mon_pic_trigger(self, event):
        mon_species = self.species_cb.get()
        self.set_mon_pic(mon_species)


    def set_mon_pic(self, mon_species):
        try:
            pic_dir = os.path.join(self.project_path, self.get_mon_pic_path_from_species(mon_species))
            if os.path.exists(pic_dir):
                img_path = pic_dir
            else:
                img_path = MON_PIC_PLACEHOLDER
            self.mon_img.config(file=img_path, height=64, width=64)
        except Exception:
            pass


    def set_default_moves(self):
        if self.default_moves_var.get() == 1:
            for move in self.move_cbs:
                move.set("MOVE_NONE")
    

    def uncheck_default_moves(self, event):
        is_default = True
        for move in self.move_cbs:
            if move.get() != "MOVE_NONE":
                self.default_moves_var.set(0)
                is_default = False
        if is_default:
            self.default_moves_var.set(1)


    def get_mon_pic_path_from_species(self, species):
        for pic in self.mon_pics:
            if pic['species'] == species:
                return pic['path']


    def save_mon_data(self):
        mon = self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
        mon.species = self.species_cb.get()
        mon.level = int(self.level_sb.get())
        mon.held_item = self.held_item_cb.get()
        for move_index in range(0,4):
            mon.moves[move_index] = self.move_cbs[move_index].get()

        if self.check_expansion():
            mon.ivs = None
            mon.evs = None
            mon.nature = None
            mon.ability = None
        else:
            mon.iv = int(self.ivs_spinboxes['HP'].get())

        self.update_party_list(self.current_trainer_id)


    def add_party_mon(self):
        if len(self.project_data.trainers[self.current_trainer_id].pokemon) < 6:
            new_mon = Pokemon("SPECIES_BULBASAUR")
            self.project_data.trainers[self.current_trainer_id].pokemon.append(new_mon)
            self.update_party_list(self.current_trainer_id)

    
    def del_party_mon(self):
        if len(self.project_data.trainers[self.current_trainer_id].pokemon) > 1:
            self.project_data.trainers[self.current_trainer_id].pokemon.remove(self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon])
            self.update_party_list(self.current_trainer_id)
            self.party_listbox.selection_set(0, 0)
            self.party_listbox.event_generate("<<ListboxSelect>>")
    

    def move_up_party_mon(self):
        if len(self.project_data.trainers[self.current_trainer_id].pokemon) > 1:
            if self.current_trainer_mon > 0:
                mon = self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
                self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
                self.project_data.trainers[self.current_trainer_id].pokemon.remove(self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon])
                self.project_data.trainers[self.current_trainer_id].pokemon.insert(self.current_trainer_mon - 1, mon)
                self.update_party_list(self.current_trainer_id)
                self.party_listbox.selection_set(self.current_trainer_mon - 1, self.current_trainer_mon - 1)
                self.party_listbox.event_generate("<<ListboxSelect>>")


    def move_down_party_mon(self):
        if len(self.project_data.trainers[self.current_trainer_id].pokemon) > 1:
            if self.current_trainer_mon < 5:
                mon = self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
                self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon]
                self.project_data.trainers[self.current_trainer_id].pokemon.remove(self.project_data.trainers[self.current_trainer_id].pokemon[self.current_trainer_mon])
                self.project_data.trainers[self.current_trainer_id].pokemon.insert(self.current_trainer_mon + 1, mon)
                self.update_party_list(self.current_trainer_id)
                if self.current_trainer_mon + 1 < len(self.project_data.trainers[self.current_trainer_id].pokemon):
                    self.party_listbox.selection_set(self.current_trainer_mon + 1, self.current_trainer_mon + 1)
                else:
                    self.party_listbox.selection_set(len(self.project_data.trainers[self.current_trainer_id].pokemon) - 1, len(self.project_data.trainers[self.current_trainer_id].pokemon) - 1)
                self.party_listbox.event_generate("<<ListboxSelect>>")


    def save_trainer_data(self):
        trainer = self.project_data.trainers[self.current_trainer_id]
        trainer.name = self.name_entry.get()
        trainer.trainer_class = self.trainer_class_cb.get()
        trainer.trainer_pic = self.trainer_pic_cb.get()
        trainer.encounter_music = self.encounter_music_cb.get()
        trainer.gender = 'MALE' if self.current_trainer_gender_var == self.gender_options[0] else 'FEMALE'
        trainer.double_battle = True if self.double_battle_var.get() == True else False
        
        trainer_items = []
        for item in self.item_cbs:
            trainer_items.append(item.get())
        trainer.items = trainer_items

        trainer_ai_flags = []

        for flag in self.ai_flag_vars:
            if flag[1].get() == True:
                trainer_ai_flags.append(flag[0])

        trainer.ai_flags = trainer_ai_flags
        # trainer.party_name =
        trainer.maps = []


if __name__ == "__main__":
    app = App()
    app.mainloop()

