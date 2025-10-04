#! /usr/bin/env python3

import tkinter as tk
import os
from modules.classes import Trainer, Pokemon, AiFlagList
from tkinter import ttk
from tkinter import filedialog

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

PROJECT_FILES = {
    "battle_ai":       "/include/constants/battle_ai.h",
    "items":           "/include/constants/items.h",
    "moves":           "/include/constants/moves.h",
    "opponents":       "/include/constants/opponents.h",
    "natures":         "/include/constants/pokemon.h",
    "species":         "/include/constants/species.h",
    "trainer_data":    "/src/data/trainers.h",
    "trainer_info":    "/include/constants/trainers.h",
    "trainer_parties": "/src/data/trainer_parties.h",
    "trainer_pics":    "/graphics/trainers/front_pics"
}

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
        self.title("Decomp Trainer Editor")
        self.geometry("1366x768")
        self.project_path = None
        self.project_data = ProjectData()
        self.showdown_type_output = False

        ############
        # MENU BAR #
        ############

        # Defining the top menu bar container
        self.menubar = tk.Menu(self)

        # File menu: It allows to open/save projects and exit the app.
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu_open = file_menu.add_command(label="Open project", command=self.open_project)
        file_menu_save = file_menu.add_command(label="Save project")
        file_menu.add_separator()
        file_menu_exit = file_menu.add_command(label="Exit", command=self.quit)

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
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menubar.add_cascade(label="Edit", menu=edit_menu, state=tk.DISABLED)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=self.menubar)

        # The main windows layout is divided in 3 columns. One will permit to select the trainer to edit,
        # the second will show trainer general info and the third will show the selected Pokémon info from the party.
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ##############################
        # COLUMN 1 - Trainer ID List #
        ##############################

        # Trainer list container. It will have a fixed width and scrollbars as the ID don't use to be too long.
        col1_kwargs = {"width": 340,"bd": 2, "relief": tk.GROOVE}
        col1 = tk.Frame(main_frame, **col1_kwargs)
        col1.pack(side=tk.LEFT, fill=tk.Y)
        col1.pack_propagate(False)
        # Trainer list container set up.
        listbox_frame = tk.Frame(col1)
        listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Internal frame to hold the listbox and the horizontal scrollbar below it
        listbox_pack_frame = tk.Frame(listbox_frame)
        listbox_pack_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_trainers_id = tk.Listbox(listbox_pack_frame, selectmode=tk.SINGLE)
        self.listbox_trainers_id.bind("<<ListboxSelect>>", self.update_trainer_fields)
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
        col2 = tk.Frame(main_frame, **col2_kwargs)
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

        # Now this buttons may allow to move up/down the selected Pokémon in the party, add a new one or remove the selected one.
        # They must be disabled if there is no project opened.
        btns_frame = ttk.Frame(party_frame)
        btns_frame.pack(fill=tk.X, pady=(8, 0))
        self.party_button_up     = ttk.Button(btns_frame, text="Up", state=tk.DISABLED)
        self.party_button_down   = ttk.Button(btns_frame, text="Down", state=tk.DISABLED)
        self.party_button_add    = ttk.Button(btns_frame, text="Add", state=tk.DISABLED)
        self.party_button_remove = ttk.Button(btns_frame, text="Remove", state=tk.DISABLED)

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
        ttk.Label(place_tab, text="Places where the trainer was found").pack(anchor="w", pady=(10, 5), padx=10)
        self.places_listbox = tk.Listbox(place_tab, height=8)
        self.places_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        row += 1

        ####################################
        # COLUMN 3 - Pokemon configuration #
        ####################################
        col3_kwargs = {"bd": 2, "relief": tk.GROOVE}
        col3 = tk.Frame(main_frame, **col3_kwargs)
        col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Show mon picture at the top. If the image can't be loaded, show a blank canvas instead.
        try:
            self.mon_img = tk.PhotoImage(file=MON_PIC_PLACEHOLDER)
            mon_img_label = ttk.Label(col3, image=self.mon_img)
            mon_img_label.pack(pady=(20, 10))
        except Exception:
            mon_canvas = tk.Canvas(col3, width=64, height=64, bg="#cccccc", highlightthickness=0)
            mon_canvas.pack(pady=(20, 10))

        # Data container for all Pokémon fields. Comboboxes to be populated at project load. Individual Pokémon data
        # to be loaded when selecting a Pokémon from the party listbox.
        poke_fields_frame = ttk.Frame(col3)
        poke_fields_frame.pack(pady=10, padx=20, fill=tk.X)

        # Species
        ttk.Label(poke_fields_frame, text="Species:").grid(row=0, column=0, sticky="w", pady=4)
        self.species_cb = ttk.Combobox(poke_fields_frame, values=[], state="disabled")
        self.species_cb.grid(row=0, column=1, sticky="ew", pady=4)

        # Level
        ttk.Label(poke_fields_frame, text="Level:").grid(row=1, column=0, sticky="w", pady=4)
        self.level_sb = tk.Spinbox(poke_fields_frame, from_=1, to=100, width=5, state="disabled")
        self.level_sb.grid(row=1, column=1, sticky="w", pady=4)

        # Held Item
        ttk.Label(poke_fields_frame, text="Held Item:").grid(row=2, column=0, sticky="w", pady=4)
        self.held_item_cb = ttk.Combobox(poke_fields_frame, values=[], state="disabled")
        self.held_item_cb.grid(row=2, column=1, sticky="ew", pady=4)

        # Ability
        ttk.Label(poke_fields_frame, text="Ability:").grid(row=3, column=0, sticky="w", pady=4)
        self.ability_cb = ttk.Combobox(poke_fields_frame, values=["RANDOM", "FIRST", "SECOND", "HIDDEN"], state="disabled")
        self.ability_cb.grid(row=3, column=1, sticky="ew", pady=4)

        # Nature
        ttk.Label(poke_fields_frame, text="Nature:").grid(row=4, column=0, sticky="w", pady=4)
        self.nature_cb = ttk.Combobox(poke_fields_frame, values=[], state="disabled")
        self.nature_cb.grid(row=4, column=1, sticky="ew", pady=4)

        # Moves
        ttk.Label(poke_fields_frame, text="Moves:").grid(row=5, column=0, sticky="w", pady=(12, 4))
        # Moves label and "Default moves" checkbox side by side in a frame
        moves_label_frame = ttk.Frame(poke_fields_frame)
        moves_label_frame.grid(row=5, column=0, columnspan=2, sticky="w", pady=(12, 4))
        ttk.Label(moves_label_frame, text="Moves:").pack(side=tk.LEFT)
        self.default_moves_var = tk.BooleanVar(value=False)
        self.default_moves_check = ttk.Checkbutton(moves_label_frame, text="Default moves", variable=self.default_moves_var, state="disabled")
        self.default_moves_check.pack(side=tk.LEFT, padx=10)
        self.move_cbs = []
        for i in range(4):
            cb = ttk.Combobox(poke_fields_frame, values=[], state="disabled", width=16)
            cb.grid(row=6 + i, column=0, sticky="ew", pady=2, columnspan=2)
            self.move_cbs.append(cb)

        # IVs
        ttk.Label(poke_fields_frame, text="IVs:").grid(row=20, column=0, sticky="w", pady=(12, 4), columnspan=4)
        ivs_frame = ttk.Frame(poke_fields_frame)
        ivs_frame.grid(row=21, column=0, columnspan=4, sticky="w")
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
        ttk.Label(poke_fields_frame, text="EVs:").grid(row=30, column=0, sticky="w", pady=(12, 4), columnspan=4)
        evs_frame = ttk.Frame(poke_fields_frame)
        evs_frame.grid(row=31, column=0, columnspan=4, sticky="w")
        self.evs_spinboxes = {}
        for idx, stat in enumerate(iv_stats):
            col = 0 if idx < 3 else 1
            row = idx % 3
            ttk.Label(evs_frame, text=stat+":").grid(row=row, column=col*2, sticky="e", padx=(6,1))
            sb = tk.Spinbox(evs_frame, from_=0, to=255, width=5, state="disabled")
            sb.grid(row=row, column=col*2+1, sticky="w", pady=2)
            self.evs_spinboxes[stat] = sb

        poke_fields_frame.columnconfigure(1, weight=1)

        # Status bar at the bottom of the window to show messages to the user.
        self.status = tk.Label(self, text="Project not opened.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def open_project(self):
        ''' Open a folder dialog to select the project path and load its data. WIP.'''
        path = filedialog.askdirectory(title="Select project folder", initialdir=get_last_opened_project())
        if path:
            set_last_opened_project(path)
            self.project_path = path
            self.status.config(text=f"Project opened: {path}")
            self.check_expansion()
            self.enable_trainer_editing()
            self.enable_partymon_editing()
            self.data_adquisition()
    
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
            self.party_button_remove
        ]

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
        # Only if the project is based on pokeemerald expansion
        if self.project_data.expansion:
            self.populate_nature_list()
        
        self.get_trainer_data()

    def populate_trainer_list(self):
        ''' Populate the trainer ID listbox from constants/opponents.h file. '''
        trainer_id_list = []

        with open(os.path.join(self.project_path, PROJECT_FILES["opponents"].lstrip("/")), "r") as f:
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

        with open(os.path.join(self.project_path, PROJECT_FILES["trainer_info"].lstrip("/")), "r") as f:
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

        with open(os.path.join(self.project_path, PROJECT_FILES["items"].lstrip("/")), "r") as f:
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
        with open(os.path.join(self.project_path, PROJECT_FILES["battle_ai"].lstrip("/")), "r") as f:
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

        with open(os.path.join(self.project_path, PROJECT_FILES["species"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define SPECIES_"):
                species_id = line.split()[1]
                species_id_list.append(species_id)
        
        self.species_cb['values'] = species_id_list[1:] # Remove SPECIES_NONE
    
    def populate_moves_list(self):
        ''' Populate the trainer info comboboxes from constants/moves.h file. '''
        move_id_list = []

        with open(os.path.join(self.project_path, PROJECT_FILES["moves"].lstrip("/")), "r") as f:
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

        with open(os.path.join(self.project_path, PROJECT_FILES["natures"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define NATURE_"):
                nature_id = line.split()[1]
                natures_id_list.append(nature_id)
        
        self.nature_cb['values'] = natures_id_list

    def get_trainer_data(self):
        ''' Get the trainer info from data/trainers.h file and process it to self.project_data. '''

        with open(os.path.join(self.project_path, PROJECT_FILES["trainer_data"].lstrip("/")), "r") as f:
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
                new_trainer.name = data[2].strip('",_()')
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
            elif field == '},':
                self.project_data.trainers.append(new_trainer)
                new_trainer = None
        

        for trainer in self.project_data.trainers[80:90]:
            print(trainer.id + ', ' + trainer.trainer_class)
            print('  Items: ' + ', '.join(trainer.items))
            ai_desc = [flag for flag in trainer.ai_flags]
            print('  AI flags: ' + str([(flag) for flag in ai_desc]))

    def update_trainer_fields(self, event):
        ''' Update the trainer fields in the UI with the data from self.current_trainer.'''
        selected_idx = self.listbox_trainers_id.curselection()
        if selected_idx:
            current_trainer = self.project_data.trainers[selected_idx[0] + 1] # +1 to skip TRAINER_NONE
            # Insert the ID
            self.id_entry.config(state="normal")
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, current_trainer.id)
            self.id_entry.config(state="readonly")
            # Insert the name
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, current_trainer.name)
            # Set the gender
            self.current_trainer_gender_var.set(current_trainer.gender)
            for i, opt in enumerate(self.gender_options):
                self.radio_gender[i].config(variable=self.current_trainer_gender_var, value=opt)
            # Set the trainer pic
            self.trainer_pic_cb.set(current_trainer.trainer_pic)
            # Set the trainer class
            self.trainer_class_cb.set(current_trainer.trainer_class)
            # Set the encounter music
            self.encounter_music_cb.set(current_trainer.encounter_music)
            # Set the double battle
            self.double_battle_var.set(current_trainer.double_battle)
            # Set the items
            for i in range(4):
                if i < len(current_trainer.items):
                    self.item_cbs[i].set(current_trainer.items[i])
            
            # Set the AI flags
            for flag, var in self.ai_flag_vars:
                flag_exists = False
                for trainer_flag in current_trainer.ai_flags:
                    if flag == trainer_flag:
                        flag_exists = True
                    else:
                        flag_exists = flag_exists or False

                var.set(flag_exists)

if __name__ == "__main__":
    app = App()
    app.mainloop()

