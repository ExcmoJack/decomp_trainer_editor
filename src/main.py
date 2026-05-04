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

# IMG resources paths - Think about moving this to another file
TRAINER_PIC_PLACEHOLDER = os.path.join(get_current_directory(), "assets", "trainer_placeholder.png")
MON_PIC_PLACEHOLDER = os.path.join(get_current_directory(), "assets", "pokemon_placeholder.png")
STAR_ICON = os.path.join(get_current_directory(), "assets", "star.png")
DYNAMAX_ICON = os.path.join(get_current_directory(), "assets", "dynamax.png")

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

    ##########################################################
    #               SETTING THE WINDOW FORMAT                #
    ##########################################################

    def init_window_data(self):
        '''
        Initializes window-related data and prepares the main interface components.
        This method sets up variables, widgets, and any necessary state for the main window.

        ```
        ╔═════════════════════════════════════════════════════════════════════════╗
        ║                                Menu bar                                 ║
        ╠═══════════════════════╦══════════════════════╦══════════════════════════╣
        ║                       ║                      ║                          ║
        ║ col_trainer_selection ║ col_trainer_settings ║ col_trainer_mon_settings ║
        ║                       ║                      ║                          ║
        ║  - width: 340px       ║  - width:  auto      ║  - width:  auto          ║
        ║  - border:  2px       ║  - border:  2px      ║  - border:  2px          ║
        ║  - relief: Groove     ║  - relief: Groove    ║  - relief: Groove        ║
        ║                       ║                      ║                          ║
        ║                       ║                      ║                          ║
        ║                       ║                      ║                          ║
        ║                       ║                      ║                          ║
        ╠═══════════════════════╩══════════════════════╩══════════════════════════╣
        ║                               Status bar                                ║
        ╚═════════════════════════════════════════════════════════════════════════╝
        ```
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

        self.list_gender_options = ["MALE", "FEMALE"]

        self.create_menubar()
        self.create_column_layout()
        self.create_status_bar()

    ##########################################################
    #               SETTING THE MENU BAR                     #
    ##########################################################

    def create_menubar(self):
        '''
        Creates and configures the application's menu bar.
        This method sets up the main menu options and attaches them to the window.

        **Workflow:**
        1. Creates self.menu_bar calling tk.Menu(self)
        2. Calls the functions to populate the several options.
        3. Sets the root window to use the configured menu bar.
        '''
        # Defining the top menu bar container
        self.menu_bar = tk.Menu(self)

        self.create_menu_bar_file_menu()
        self.create_menu_bar_edit_menu()
        self.create_menu_bar_help_menu()

        # Set the root window to use this menu bar
        self.config(menu=self.menu_bar)


    def create_menu_bar_file_menu(self):
        '''
        It builds a set of commands to open/save projects and exit the app into the Menu Bar (`self.menu_bar`)
        through the File button.

        **Workflow:**
        1. Creates the container into self.menu_bar with `tearoff = false` to avoid undocking from the menu.
        2. Creates four widgets inside the File Menu with the `add_command` method:
            * `file_menu_open`: labeled as "Open project", sets the command to the function `self.open_project`.
              It will be enabled from the begining (`state=tk.NORMAL`)
            * `file_menu_save`: labeled as "Save project", sets the command to the function `self.save_project`.
              It will be disabled from the begining (`state='disabled'`) and set to `tk.NORMAL` when the project
              is loaded.
            * A separator using the `add_separator` method.
            * `file_menu_exit`: labeled as "Exit", sets the command to the builtin function `self.quit`.
              It will be enabled from the begining (`state=tk.NORMAL`).
        3. Adds the container to the button labeled as "File" through the method `add_cascade`.
           It will be enabled from the begining (`state=tk.NORMAL`)
        '''
        # Create the container inside the menu bar
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)

        # Set the widgets. Every of them have names in case it is needed an action for them.
        file_menu_open = self.file_menu.add_command(label="Open project", command=self.open_project, state=tk.NORMAL)
        file_menu_save = self.file_menu.add_command(label="Save project", command=self.save_project, state='disabled')
        self.file_menu.add_separator() # This is a separator. Just decoration.
        file_menu_exit = self.file_menu.add_command(label="Exit", command=self.quit, state=tk.NORMAL)

        # Add the container to the menu bar
        self.menu_bar.add_cascade(label="File", menu=self.file_menu, state=tk.NORMAL)


    def create_menu_bar_edit_menu(self):
        '''
        It builds a set of commands to copy/paste trainer settings or just Pokémon data into the Menu Bar (`self.menu_bar`)
        through the Edit button. It will be disabled by default until a project is opened. *(Currently disabled - WIP)*

        **Workflow:**
        1. Creates the container into self.menu_bar with `tearoff = false` to avoid undocking from the menu.
        2. Creates five widgets inside the Edit Menu with the `add_command` method:
            * `edit_menu_copy_trainer`: labeled as "Copy trainer", sets the command to the function `TBD`.
              It will be enabled from the begining (`state=tk.NORMAL`)
            * `edit_menu_paste_trainer`: labeled as "Paste trainer", sets the command to the function `TBD`.
              It will be disabled from the begining (`state='disabled'`) and set to `tk.NORMAL` when data is copied.
            * A separator using the `add_separator` method.
            * `edit_menu_copy_mon`: labeled as "Copy Pokémon", sets the command to the function `TBD`.
              It will be enabled from the begining (`state=tk.NORMAL`)
            * `edit_menu_paste_mon`: labeled as "Paste Pokémon", sets the command to the function `TBD`.
              It will be disabled from the begining (`state='disabled'`) and set to `tk.NORMAL` when data is copied.
        3. Adds the container to the button labeled as "Edit" through the method `add_cascade`.
           It will be disabled from the begining (`state=tk.NORMAL`) and set to `tk.NORMAL` when the project is loaded.
        '''
        # Create the container inside the menu bar
        edit_menu = tk.Menu(self.menu_bar, tearoff=False)
        
        # Set the widgets. Every of them have names in case it is needed an action for them.
        edit_menu_copy_trainer  = edit_menu.add_command(label="Copy trainer", state=tk.NORMAL)
        edit_menu_paste_trainer = edit_menu.add_command(label="Paste trainer", state='disabled')
        edit_menu.add_separator() # This is a separator. Just decoration.
        edit_menu_copy_mon      = edit_menu.add_command(label="Copy Pokémon", state=tk.NORMAL)
        edit_menu_paste_mon     = edit_menu.add_command(label="Paste Pokémon", state='disabled')

        # Add the container to the menu bar
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu, state='disabled')


    def create_menu_bar_help_menu(self):
        '''
        It builds a set of commands to access documentation and see info about the app into the Menu Bar (`self.menu_bar`)
        through the Help button.

        **Workflow:**
        1. Creates the container into self.menu_bar with `tearoff = false` to avoid undocking from the menu.
        2. Creates two widgets inside the Help Menu with the `add_command` method:
            * `help_menu_docs`: labeled as "Documentation", sets the command to the function `self.launch_documentation`.
              It will be enabled from the begining (`state=tk.NORMAL`)
            * `help_menu_about`: labeled as "About", sets the command to the function `self.show_about_dialog`.
              It will be enabled from the begining (`state=tk.NORMAL`)
        3. Adds the container to the button labeled as "Help" through the method `add_cascade`.
           It will be enabled from the begining (`state=tk.NORMAL`)
        '''
        # Create the container inside the menu bar
        help_menu = tk.Menu(self.menu_bar, tearoff=False)

        # Set the widgets. Every of them have names in case it is needed an action for them.
        help_menu_docs  = help_menu.add_command(label="Documentation", command=self.launch_documentation, state=tk.NORMAL)
        help_menu_about = help_menu.add_command(label="About", command=self.show_about_dialog, state=tk.NORMAL)

        # Add the container to the menu bar
        self.menu_bar.add_cascade(label="Help", menu=help_menu, state=tk.NORMAL)
        
    ##########################################################
    #            SETTING THE WINDOW ARRANGEMENT              #
    ##########################################################

    def create_column_layout(self):
        '''
        The main_frame layout is divided in 3 columns. One will permit to select the trainer to edit,
        the second will show trainer general info and the third will show the selected Pokémon info from the party.

        **Workflow:**
        1. Creates and arranges the `main_frame` layout. It is packed to fill the whole of the window with `fill='both'` and `expand=True`
           (apart from the menu bar and the status bar).
        2. Sets up the three main columns: trainer selection, trainer info, and Pokémon info.
        3. Initializes all widgets and containers for user interaction.
        '''
        # Create the main_frame and attach to the app window.
        self.main_frame = tk.Frame(self)
        # Pack the main_frame to fill the screen.
        self.main_frame.pack(fill='both', expand=True)

        self.create_col_trainer_selection()
        self.create_col_trainer_settings()
        self.create_col_trainer_mon_settings()


    def create_col_trainer_selection(self):
        '''
        Trainer list container. It will have a fixed width and scrollbars as the ID don't use to be too long.
        
        **Workflow:**
        1.  Create the `col_trainer_selection` frame and pack it into `main_frame` to the left side (`side='left'`) and filling in vertical (`fill='y'`).
            We set `pack_propagate` to `False` so the column will mantain its width when the Listbox is added.
        2.  Create the `frame_listbox` inside the `col_trainer_selection` frame.
            It is packed to fill the whole of the `col_trainer_selection` frame with `fill='both'` and `expand=True`.
        3.  Create the `frame_listbox_scrollbar_x` inside the `frame_listbox` frame.
            This is an auxiliar frame to hold the listbox and the horizontal scrollbar below it.
            It is packed to fill the whole of the left side (`side='left'`) of the `frame_listbox` to make space to the `scrollbar_listbox_trainers_id_y`
            at its right and it is filled with `fill='both'` and `expand=True`.
        4.  Create the `listbox_trainers_id` inside `frame_listbox_scrollbar_x`. `selectmode` set to `'single'` to avoid multiple trainers selected.
        5.  Add an event listener with `bind("<<ListboxSelect>>", self.update_trainer_fields_trigger)` the update of the trainer data
            in the col_trainer_settings when switching the item selected.
        6.  Pack `listbox_trainers_id` inside `frame_listbox_scrollbar_x`. We pack it on `side='top'` to make space to the `scrollbar_listbox_trainers_id_x`
            on its bottom and it is filled horizontally.
        7.  Create the `scrollbar_listbox_trainers_id_x` and link it to the `listbox_trainers_id` X movement with `command=self.listbox_trainers_id.xview`
            and configurate the `listbox_trainers_id` with `config(xscrollcommand=scrollbar_listbox_trainers_id_x.set)`.
        8.  Pack `scrollbar_listbox_trainers_id_x` inside `frame_listbox_scrollbar_x`. We pack it on `side='bottom'` right down `listbox_trainers_id`
            and it is filled horizontally.
        9.  Create the `scrollbar_listbox_trainers_id_y` and link it to the `listbox_trainers_id` Y movement with `command=self.listbox_trainers_id.yview`
            and configurate the `listbox_trainers_id` with `config(xscrollcommand=scrollbar_listbox_trainers_id_y.set)`.
        10. Pack `scrollbar_listbox_trainers_id_x` inside `listbox_scrollbar`. We pack it on `side='right'` besides `frame_listbox_scrollbar_x`
            and it is filled vertically.

        ```
        ╔═════════════════════════════════════════════════════════════════════════╗
        ║ col_trainer_selection                                                   ║
        ║╔═══════════════════════════════════════════════════════════════════════╗║
        ║║ frame_listbox                                                         ║║
        ║║╔═══════════════════════════════════╦═════════════════════════════════╗║║
        ║║║ frame_listbox_scrollbar_x         ║                                 ║║║
        ║║║╔═════════════════════════════════╗║                                 ║║║
        ║║║║ listbox_trainers_id             ║║                                 ║║║
        ║║║╠═════════════════════════════════╣║ scrollbar_listbox_trainers_id_y ║║║
        ║║║║ scrollbar_listbox_trainers_id_x ║║                                 ║║║
        ║║║╚═════════════════════════════════╝║                                 ║║║
        ║║╚═══════════════════════════════════╩═════════════════════════════════╝║║
        ║╚═══════════════════════════════════════════════════════════════════════╝║
        ╚═════════════════════════════════════════════════════════════════════════╝
        ```
        '''
        # Create the column frame inside the main_frame
        col_trainer_selection = tk.Frame(self.main_frame, width=340, bd=2, relief='groove')
        col_trainer_selection.pack(side='left', fill='y')
        # Fix the width even containing smaller or bigger widgets.
        col_trainer_selection.pack_propagate(False)
        
        # Create the frame_listbox inside the col_trainer_selection frame.
        frame_listbox = tk.Frame(col_trainer_selection)
        frame_listbox.pack(padx=10, pady=10, fill='both', expand=True)

        # Create the frame_listbox_scrollbar_x inside the frame_listbox frame.
        # This is an auxiliar frame to hold the listbox and the horizontal scrollbar below it.
        frame_listbox_scrollbar_x = tk.Frame(frame_listbox)
        frame_listbox_scrollbar_x.pack(side='left', fill='both', expand=True)

        # Create the listbox_trainers_id inside frame_listbox_scrollbar_x.
        self.listbox_trainers_id = tk.Listbox(frame_listbox_scrollbar_x, selectmode='single')
        # Triggers the update of the trainer data on the col_trainer_settings on switch the item selected.
        self.listbox_trainers_id.bind("<<ListboxSelect>>", self.update_trainer_fields_trigger)
        # Pack listbox_trainers_id inside frame_listbox_scrollbar_x.
        self.listbox_trainers_id.pack(side='top', fill='both', expand=True)

        # Create the scrollbar_listbox_trainers_id_x and link it to the listbox_trainers_id movement.
        scrollbar_listbox_trainers_id_x = tk.Scrollbar(frame_listbox_scrollbar_x, orient=tk.HORIZONTAL, command=self.listbox_trainers_id.xview)
        self.listbox_trainers_id.config(xscrollcommand=scrollbar_listbox_trainers_id_x.set)
        # Pack scrollbar_listbox_trainers_id_x inside frame_listbox_scrollbar_x.
        scrollbar_listbox_trainers_id_x.pack(side='bottom', fill='x')

        # Create the scrollbar_listbox_trainers_id_y and link it to the listbox_trainers_id movement.
        scrollbar_listbox_trainers_id_y = tk.Scrollbar(frame_listbox, orient=tk.VERTICAL, command=self.listbox_trainers_id.yview)
        self.listbox_trainers_id.config(yscrollcommand=scrollbar_listbox_trainers_id_y.set)
        # Pack scrollbar_listbox_trainers_id_y inside frame_listbox.
        scrollbar_listbox_trainers_id_y.pack(side='right', fill='y')


    def create_col_trainer_settings(self):
        '''
        Trainer info container. Info is supposed to be updated when selecting a trainer from the listbox
        
        **Workflow:**
        1.  Create the column frame inside the `main_frame`
        2.  Create the form frame inside the `col_trainer_settings` frame
        3.  Force the middle column to be wider than the other two. Without any `columnconfigure`, the first and the last will have the minimum width.
        4.  Show trainer picture at the top left
            - Add a `PhotoImage` widget with `TRAINER_PIC_PLACEHOLDER`
            - In case the image is not found or can't be loaded, show a blank canvas instead
        5.  Add radio buttons for gender. This will be saved in `self.current_trainer_gender_var`.
        6.  Iterate through the options (`self.list_gender_options`) and set each radio in a row at the right of the `self.photoimage_trainer_pic`.
        7.  Add Trainer ID entry widget and its label. Read only.
        8.  Add a button to replace the `TRAINER_ID` in all directories. WIP. It will use a different dialog windows for this purpose.
        9.  Add Trainer Pic and its label combobox widget to `frame_col_trainer_settings_form`. Empty values by default before loading a project.
        10. Add Trainer Class combobox widget and its label to `frame_col_trainer_settings_form`. Empty values by default before loading a project.
        11. Add Trainer Encounter Music combobox widget and its label to `frame_col_trainer_settings_form`. Empty values by default before loading a project.
        12. Add Double Battle checkbox widget to `frame_col_trainer_settings_form`. Unchecked by default before loading a project.
        13. Create the tabs frame inside the `col_trainer_settings` frame
        14. This will force the notebook container to be full width.
        15. Create the notebook frame inside the `frame_col_trainer_settings_tabs`
        16. Add a button to save all the trainer data.
        
        ```
        ╔═══════════════════════════════════════════════════════════════════════════════════════════════════════╗
        ║ col_trainer_settings                                                                                  ║
        ║╔═════════════════════════════════════════════════════════════════════════════════════════════════════╗║
        ║║ frame_col_trainer_settings_form                                                                     ║║
        ║║╔═════════════════════════════╤═══════════════════════════════════════╤═════════════════════════════╗║║
        ║║║                             │ self.radio_gender[MALE]               │                             ║║║
        ║║║ self.photoimage_trainer_pic ├───────────────────────────────────────┼─────────────────────────────╢║║
        ║║║                             │ self.radio_gender[FEMALE]             │                             ║║║
        ║║╟─────────────────────────────┼───────────────────────────────────────┼─────────────────────────────╢║║
        ║║║ "Trainer ID:" (Label)       │ self.text_entry_trainer_id            │ self.button_edit_trainer_id ║║║
        ║║╟─────────────────────────────┼───────────────────────────────────────┼─────────────────────────────╢║║
        ║║║ "Trainer Name:" (Label)     │ self.text_entry_trainer_name          │                             ║║║
        ║║╟─────────────────────────────┼───────────────────────────────────────┼─────────────────────────────╢║║
        ║║║ "Trainer Pic:" (Label)      │ self.combobox_trainer_pic             │                             ║║║
        ║║╟─────────────────────────────┼───────────────────────────────────────┼─────────────────────────────╢║║
        ║║║ "Trainer Class:" (Label)    │ self.combobox_trainer_class           │                             ║║║
        ║║╟─────────────────────────────┼───────────────────────────────────────┼─────────────────────────────╢║║
        ║║║ "Encounter Music:" (Label)  │ self.combobox_trainer_encounter_music │                             ║║║
        ║║╟─────────────────────────────┼───────────────────────────────────────┼─────────────────────────────╢║║
        ║║║                             │ self.checkbox_double_battle           │                             ║║║
        ║║╚═════════════════════════════╧═══════════════════════════════════════╧═════════════════════════════╝║║
        ║╠═════════════════════════════════════════════════════════════════════════════════════════════════════╣║
        ║║ frame_col_trainer_settings_tabs                                                                     ║║
        ║║╔═══════════════════════════════════════════════════════════════════════════════════════════════════╗║║
        ║║║ notebook_trainer_battle_settings                                                                  ║║║
        ║║╚═══════════════════════════════════════════════════════════════════════════════════════════════════╝║║
        ║╠═════════════════════════════════════════════════════════════════════════════════════════════════════╣║
        ║║ self.button_save_trainer                                                                            ║║
        ║╚═════════════════════════════════════════════════════════════════════════════════════════════════════╝║
        ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════╝
        ```
        '''
        # Create the column frame inside the main_frame
        col_trainer_settings = tk.Frame(self.main_frame, bd=2, relief='groove')
        col_trainer_settings.pack(side='left', fill='both', expand=True)

        # Create the form frame inside the col_trainer_settings frame
        frame_col_trainer_settings_form = tk.Frame(col_trainer_settings)
        frame_col_trainer_settings_form.pack(side='top', fill='both', expand=True, padx=10, pady=10)

        # This will force the middle column to be wider than the other two.
        # Without any columnconfigure, the first and the last will have the minimum width.
        frame_col_trainer_settings_form.columnconfigure(index=1, weight=1)

        # Show trainer picture at the top left
        try:
            # Add a PhotoImage widget with TRAINER_PIC_PLACEHOLDER
            self.photoimage_trainer_pic = tk.PhotoImage(file=(TRAINER_PIC_PLACEHOLDER))
            img_label = ttk.Label(frame_col_trainer_settings_form, image=self.photoimage_trainer_pic)
            img_label.grid(row=0, column=0, rowspan=2)
        except Exception:
            # In case the image is not found or can't be loaded, show a blank canvas instead
            self.canvas_trainer_pic_when_file_missing = tk.Canvas(frame_col_trainer_settings_form, width=64, height=64, bg="#cccccc", highlightthickness=0)
            self.canvas_trainer_pic_when_file_missing.grid(row=0, column=0, rowspan=2)

        # Add radio buttons for gender. This will be saved in self.current_trainer_gender_var.
        self.current_trainer_gender_var = tk.StringVar(value=self.list_gender_options[0])
        self.radio_gender = []
        for i, opt in enumerate(self.list_gender_options):
            # Iterate through the options (self.list_gender_options) and set each radio in a row at the right of the self.photoimage_trainer_pic.
            rb = ttk.Radiobutton(frame_col_trainer_settings_form, text=opt, variable=self.current_trainer_gender_var, value=opt, state='disabled')
            self.radio_gender.append(rb)
            rb.grid(row=i, column=1, sticky='w')

        # Add Trainer ID entry widget and its label. Read only.
        ttk.Label(frame_col_trainer_settings_form, text="Trainer ID:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.text_entry_trainer_id = ttk.Entry(frame_col_trainer_settings_form)
        self.text_entry_trainer_id.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        self.text_entry_trainer_id.config(state='readonly')

        # Add a button to replace the TRAINER_ID in all directories. WIP. It will use a different dialog windows for this purpose.
        self.button_edit_trainer_id = ttk.Button(frame_col_trainer_settings_form, text="Edit Trainer ID", state='disabled')
        self.button_edit_trainer_id.grid(row=2, column=2, sticky="ew")

        # Add Trainer Name entry widget and its label to frame_col_trainer_settings_form. Read only until the project is loaded.
        ttk.Label(frame_col_trainer_settings_form, text="Trainer Name:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.text_entry_trainer_name = ttk.Entry(frame_col_trainer_settings_form)
        self.text_entry_trainer_name.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        self.text_entry_trainer_name.config(state='readonly')

        # Add Trainer Pic and its label combobox widget to frame_col_trainer_settings_form. Empty values by default before loading a project.
        ttk.Label(frame_col_trainer_settings_form, text="Trainer Pic:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.combobox_trainer_pic = ttk.Combobox(frame_col_trainer_settings_form, values=[], state='disabled')
        self.combobox_trainer_pic.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        self.combobox_trainer_pic.bind("<<ComboboxSelected>>", self.set_trainer_pic_trigger)

        # Add Trainer Class combobox widget and its label to frame_col_trainer_settings_form. Empty values by default before loading a project.
        ttk.Label(frame_col_trainer_settings_form, text="Trainer Class:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.combobox_trainer_class = ttk.Combobox(frame_col_trainer_settings_form, values=[], state='disabled')
        self.combobox_trainer_class.grid(row=5, column=1, sticky="ew", padx=10, pady=5)

        # Add Trainer Encounter Music combobox widget and its label to frame_col_trainer_settings_form. Empty values by default before loading a project.
        ttk.Label(frame_col_trainer_settings_form, text="Encounter Music:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.combobox_trainer_encounter_music = ttk.Combobox(frame_col_trainer_settings_form, values=[], state='disabled')
        self.combobox_trainer_encounter_music.grid(row=6, column=1, sticky="ew", padx=10, pady=5)

        # Add Double Battle checkbox widget to frame_col_trainer_settings_form. Unchecked by default before loading a project.
        self.bool_double_battle = tk.BooleanVar(value=False)
        self.checkbox_double_battle = ttk.Checkbutton(frame_col_trainer_settings_form, text="Double Battle", variable=self.bool_double_battle, state='disabled')
        self.checkbox_double_battle.grid(row=7, column=1, sticky="w", padx=10, pady=8)

        # Create the tabs frame inside the col_trainer_settings frame
        frame_col_trainer_settings_tabs = tk.Frame(col_trainer_settings)
        frame_col_trainer_settings_tabs.pack(side='top', fill='both', expand=True)
        # This will force the notebook container to be full width.
        frame_col_trainer_settings_tabs.columnconfigure(index=0, weight=1)

        # Create the notebook frame inside the frame_col_trainer_settings_tabs
        self.create_notebook_trainer_battle_settings(frame_col_trainer_settings_tabs)

        # Add a button to save all the trainer data.
        self.button_save_trainer = ttk.Button(col_trainer_settings, text="Save Trainer", state='disabled', command=self.save_trainer_object)
        self.button_save_trainer.pack(side='bottom', expand=False, pady=20)


    def create_col_trainer_mon_settings(self):
        column3_format = {"bd": 2, "relief": 'groove'}
        column3 = tk.Frame(self.main_frame, **column3_format)
        column3.pack(side='left', fill='both', expand=True)

        # Data container for all Pokémon fields. Comboboxes to be populated at project load. Individual Pokémon data
        # to be loaded when selecting a Pokémon from the party listbox.
        frame_selected_mon_data = ttk.Frame(column3)
        frame_selected_mon_data.pack(pady=10, padx=20, fill='x')
        
        # Show mon picture at the top. If the image can't be loaded, show a blank canvas instead.
        # Create a two-column table (frame) for mon picture and toggle buttons
        frame_mon_pic_and_toggles = ttk.Frame(frame_selected_mon_data)
        frame_mon_pic_and_toggles.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        # First column: Pokémon picture
        try:
            self.photoimage_mon_pic = tk.PhotoImage(file=MON_PIC_PLACEHOLDER)
            label_mon_pic = ttk.Label(frame_mon_pic_and_toggles, image=self.photoimage_mon_pic)
            label_mon_pic.grid(row=0, column=0, rowspan=2, padx=(0, 10))
        except Exception:
            canvas_mon_pic_when_files_missing = tk.Canvas(frame_mon_pic_and_toggles, width=64, height=64, bg="#cccccc", highlightthickness=0)
            canvas_mon_pic_when_files_missing.grid(row=0, column=0, rowspan=2, padx=(0, 10))

        # Second column: Two rows, each with a toggle button
        self.current_mon_gender_var = tk.StringVar(value=self.list_gender_options[0])
        self.radio_mon_gender = []
        for i, opt in enumerate(self.list_gender_options):
            rb = ttk.Radiobutton(frame_mon_pic_and_toggles, text=opt, variable=self.current_mon_gender_var, value=opt, state='disabled')
            self.radio_mon_gender.append(rb)
            rb.grid(row=i, column=1, sticky="w", padx=5)

        # Species
        ttk.Label(frame_selected_mon_data, text="Species:").grid(row=1, column=0, sticky="w", pady=4)
        self.combobox_mon_species = ttk.Combobox(frame_selected_mon_data, values=[], state='disabled')
        self.combobox_mon_species.grid(row=1, column=1, sticky="ew", pady=4)
        self.combobox_mon_species.bind("<<ComboboxSelected>>", self.set_mon_pic_trigger)

        # Level
        ttk.Label(frame_selected_mon_data, text="Level:").grid(row=2, column=0, sticky="w", pady=4)
        self.spinbox_mon_level = tk.Spinbox(frame_selected_mon_data, from_=1, to=100, width=5, state='disabled')
        self.spinbox_mon_level.grid(row=2, column=1, sticky="w", pady=4)

        # Held Item
        ttk.Label(frame_selected_mon_data, text="Held Item:").grid(row=3, column=0, sticky="w", pady=4)
        self.combobox_mon_held_item = ttk.Combobox(frame_selected_mon_data, values=[], state='disabled')
        self.combobox_mon_held_item.grid(row=3, column=1, sticky="ew", pady=4)

        # Ability
        ttk.Label(frame_selected_mon_data, text="Ability:").grid(row=4, column=0, sticky="w", pady=4)
        self.combobox_mon_ability = ttk.Combobox(frame_selected_mon_data, values=["RANDOM", "FIRST", "SECOND", "HIDDEN"], state='disabled')
        self.combobox_mon_ability.grid(row=4, column=1, sticky="ew", pady=4)

        # Nature
        ttk.Label(frame_selected_mon_data, text="Nature:").grid(row=5, column=0, sticky="w", pady=4)
        self.combobox_mon_nature = ttk.Combobox(frame_selected_mon_data, values=[], state='disabled')
        self.combobox_mon_nature.grid(row=5, column=1, sticky="ew", pady=4)

        # Moves
        ttk.Label(frame_selected_mon_data, text="Moves:").grid(row=6, column=0, sticky="w", pady=(12, 4))
        # Moves label and "Default moves" checkbox side by side in a frame
        frame_mon_moves_label = ttk.Frame(frame_selected_mon_data)
        frame_mon_moves_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(12, 4))
        ttk.Label(frame_mon_moves_label, text="Moves:").pack(side='left')
        self.bool_mon_default_moves = tk.BooleanVar(value=False)
        self.checkbox_mon_default_moves = ttk.Checkbutton(frame_mon_moves_label, text="Default moves", variable=self.bool_mon_default_moves, state='disabled', command=self.set_default_moves)
        self.checkbox_mon_default_moves.pack(side='left', padx=10)
        self.combobox_mon_movements = []
        for i in range(4):
            combobox_mon_movement = ttk.Combobox(frame_selected_mon_data, values=[], state='disabled', width=16)
            combobox_mon_movement.grid(row=7 + i, column=0, sticky="ew", pady=2, columnspan=2)
            combobox_mon_movement.bind('<<ComboboxSelected>>', self.uncheck_default_moves)
            self.combobox_mon_movements.append(combobox_mon_movement)

        # IVs/EVs y pestaña de configuración extra
        notebook_mon_stats = ttk.Notebook(frame_selected_mon_data)
        notebook_mon_stats.grid(row=21, column=0, columnspan=4, sticky="ew", pady=(12, 4))

        # Tab IVs/EVs
        tab_ivs_evs = ttk.Frame(notebook_mon_stats)
        notebook_mon_stats.add(tab_ivs_evs, text="IVs/EVs")

        # IVs
        ttk.Label(tab_ivs_evs, text="IVs:").grid(row=0, column=1, sticky="w", pady=(4, 2), columnspan=3)
        frame_mon_ivs = ttk.Frame(tab_ivs_evs)
        frame_mon_ivs.grid(row=2, column=0, columnspan=4, sticky="w")
        self.dict_spinboxes_ivs = {}
        list_mon_stats = ["HP", "ATK", "DEF", "SPD", "SPATK", "SPDEF"]
        for idx, stat in enumerate(list_mon_stats):
            col = 0 if idx < 3 else 1
            row = idx % 3
            ttk.Label(frame_mon_ivs, text=stat+":").grid(row=row, column=col*2, sticky="e", padx=(6,1))
            spinbox = tk.Spinbox(frame_mon_ivs, from_=0, to=31, width=5, state='disabled')
            spinbox.grid(row=row, column=col*2+1, sticky="w", pady=2)
            self.dict_spinboxes_ivs[stat] = spinbox

        # EVs
        ttk.Label(tab_ivs_evs, text="EVs:").grid(row=2, column=0, sticky="w", pady=(12, 2), columnspan=4)
        frame_mon_evs = ttk.Frame(tab_ivs_evs)
        frame_mon_evs.grid(row=3, column=0, columnspan=4, sticky="w")
        self.dict_spinboxes_evs = {}
        for idx, stat in enumerate(list_mon_stats):
            col = 0 if idx < 3 else 1
            row = idx % 3
            ttk.Label(frame_mon_evs, text=stat+":").grid(row=row, column=col*2, sticky="e", padx=(6,1))
            spinbox = tk.Spinbox(frame_mon_evs, from_=0, to=255, width=5, state='disabled')
            spinbox.grid(row=row, column=col*2+1, sticky="w", pady=2)
            self.dict_spinboxes_evs[stat] = spinbox

        # Tab Other settings
        tab_other_settings = ttk.Frame(notebook_mon_stats)
        notebook_mon_stats.add(tab_other_settings, text="Other settings")

        self.current_mon_is_shiny  = tk.BooleanVar(value=False)
        self.current_mon_dinamaxes = tk.BooleanVar(value=False)
        
        self.button_shiny_toggle = ttk.Checkbutton(tab_other_settings, text='Shiny', state='disabled')
        self.button_shiny_toggle.grid(row=0, column=0, sticky="w", pady=4)

        self.button_toggle_dynamax = ttk.Checkbutton(tab_other_settings, text="Dynamax", state='disabled')
        self.button_toggle_dynamax.grid(row=1, column=0, sticky="w", pady=4)

        ttk.Label(tab_other_settings, text="Dynamax level: ").grid(row=2, column=0, sticky="e", padx=(6,1))
        self.spinbox_dynamax_level = tk.Spinbox(tab_other_settings, from_=0, to=255, width=5, state='disabled')

        self.button_save_mon = ttk.Button(frame_selected_mon_data, text="Save Pokémon", state='disabled', command=self.save_mon_object)
        self.button_save_mon.grid(row=33, column=0, columnspan=4)

        frame_selected_mon_data.columnconfigure(1, weight=1)


    def create_notebook_trainer_battle_settings(self, parent):
        '''
        Here we will have a tabbed notebook with 3 tabs: Pokémon & Items, AI Flags and Places where the trainer battle is found.
        It is important to pay attention to this part as it is the most complex of the UI.

        **Workflow:**
        1. Create the notebook_trainer_battle_settings frame inside the parent frame
        2. Create the tabs and insert them in notebook_trainer_battle_settings

        ```
        ╔════════════════════════════════════════════════════════════════════════════════════╗
        ║ notebook_trainer_battle_settings                                                   ║
        ║╔═════════════════════╗══════════════════════╗═══════════════════════════╗          ║
        ║║ tab_party_and_items ║ tab_trainer_ai_flags ║ self.tab_trainer_ai_flags ║          ║
        ║║                     ╚══════════════════════╩═══════════════════════════╩═════════╗║
        ║║                                                                                  ║║
        ║║ << Tab content >>                                                                ║║
        ║║                                                                                  ║║
        ║╚══════════════════════════════════════════════════════════════════════════════════╝║
        ╚════════════════════════════════════════════════════════════════════════════════════╝
        ```
        '''
        # Create the notebook_trainer_battle_settings frame inside the parent frame
        notebook_trainer_battle_settings = ttk.Notebook(parent)
        notebook_trainer_battle_settings.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=(10, 5))

        # Create the tabs and insert them in notebook_trainer_battle_settings
        self.create_party_items_tab_notebook_trainer_battle_settings(notebook_trainer_battle_settings)
        self.create_ai_flags_tab_notebook_trainer_battle_settings(notebook_trainer_battle_settings)
        self.create_trainer_locations_tab_notebook_trainer_battle_settings(notebook_trainer_battle_settings)


    def create_party_items_tab_notebook_trainer_battle_settings(self, notebook):
        '''
        Creates the content of `tab_party_and_items` in `notebook`.
        It sets two columns: frame_party on the left and frame_trainer_items on the right.
        The frame_trainer_items column has more weight than frame_party which will just adjust to content.

        **Workflow:**
        1.  Create the `tab_party_and_items` frame and add it to the `notebook` tab collection
        2.  Create the `frame_party_and_items` frame and insert it to the `tab_party_and_items` frame.
        3.  Create the `frame_party` frame and insert it to the the first column of `frame_party_and_items` frame.
        4.  Create the `self.listbox_mons_in_party` listbox.
        5.  Add a trigger to load the selected mon into `col_trainer_mon_settings` on `<<ListboxSelect>>` event.
        6.  Create the `frame_party_list_management` frame and insert it below the `self.listbox_mons_in_party` listbox. 
        7.  Create the party management buttons that may allow to move up/down the selected Pokémon in the party, add a new one or remove the selected one.
        8.  Create the buttons and insert them into `frame_party_list_management` frame side by side. 
        9.  Create the `frame_trainer_items` frame and insert it to the the second column of `frame_party_and_items` frame.
        10. Create the `list_combobox_trainer_item` and add one `combobox` for each item the trainer has using a `for` loop.

        ```
        ╔═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
        ║ tab_party_and_items                                                                                                                                             ║
        ║╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗║
        ║║ frame_party_and_items                                                                                                                                         ║║
        ║║╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╤══════════════════════════════════════╗║║
        ║║║ frame_party                                                                                                          │ frame_trainer_items                  ║║║
        ║║║╔════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗│╔════════════════════════════════════╗║║║
        ║║║║ "Party"                                                                                                            ║│║ "Items"                            ║║║║
        ║║║╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣│╠════════════════════════════════════╣║║║
        ║║║║ self.listbox_mons_in_party                                                                                         ║│║ self.list_combobox_trainer_item[0] ║║║║
        ║║║║                                                                                                                    ║│╠════════════════════════════════════╣║║║
        ║║║╠════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣│║ self.list_combobox_trainer_item[1] ║║║║
        ║║║║ frame_party_list_management                                                                                        ║│╠════════════════════════════════════╣║║║
        ║║║║╔══════════════════════════╦════════════════════════════╦═══════════════════════════╦══════════════════════════════╗║│║ self.list_combobox_trainer_item[2] ║║║║
        ║║║║║ self.button_party_mon_up ║ self.button_party_mon_down ║ self.button_party_add_mon ║ self.button_party_remove_mon ║║│╠════════════════════════════════════╣║║║
        ║║║║╚══════════════════════════╩════════════════════════════╩═══════════════════════════╩══════════════════════════════╝║│║ self.list_combobox_trainer_item[3] ║║║║
        ║║║╚════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝│╚════════════════════════════════════╝║║║
        ║║╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╧══════════════════════════════════════╝║║
        ║╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝║
        ╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
        ```
        '''
        # Create the tab_party_and_items frame and add it to the notebook tab collection
        tab_party_and_items = ttk.Frame(notebook)
        notebook.add(tab_party_and_items, text='Party and Items')

        # Create the frame_party_and_items frame and insert it to the tab_party_and_items frame.
        frame_party_and_items = ttk.Frame(tab_party_and_items)
        frame_party_and_items.pack(fill='both', expand=True, padx=10, pady=10)
        # It will have two columns: frame_party on the left and frame_trainer_items on the right.
        # The frame_trainer_items column will get more weight than frame_party that will just adjust to content.
        frame_party_and_items.columnconfigure(1, weight=1)

        # Create the frame_party frame and insert it to the the first column of frame_party_and_items frame.
        frame_party = ttk.Frame(frame_party_and_items)
        frame_party.grid(row=0, column=0, sticky='nsw', padx=(0, 20))

        # Create the self.listbox_mons_in_party listbox. It is supposed to be populated with the Pokémon species in the party.
        # Up to 6 Pokémon in the party and never less than 1.
        ttk.Label(frame_party, text='Party').pack(anchor='w', pady=(0, 5))
        self.listbox_mons_in_party = tk.Listbox(frame_party, height=6)
        self.listbox_mons_in_party.pack(fill='both', expand=True)
        # Trigger the loading of the selected mon in the party into col_trainer_mon_settings on '<<ListboxSelect>>' event.
        self.listbox_mons_in_party.bind('<<ListboxSelect>>', self.update_mon_fields_trigger)

        # Create the frame_party_list_management frame and insert it below the self.listbox_mons_in_party listbox. 
        frame_party_list_management = ttk.Frame(frame_party)
        frame_party_list_management.pack(fill='x', pady=(8, 0))

        # Create the party management buttons that may allow to move up/down the selected Pokémon in the party, add a new one or remove the selected one.
        # They must be disabled if there is no project opened.
        self.button_party_mon_up     = ttk.Button(frame_party_list_management, text='Up',     state='disabled', command=self.move_up_party_mon)
        self.button_party_mon_down   = ttk.Button(frame_party_list_management, text='Down',   state='disabled', command=self.move_down_party_mon)
        self.button_party_add_mon    = ttk.Button(frame_party_list_management, text='Add',    state='disabled', command=self.add_party_mon)
        self.button_party_remove_mon = ttk.Button(frame_party_list_management, text='Remove', state='disabled', command=self.del_party_mon)

        # Create the buttons and insert them into frame_party_list_management frame side by side. 
        self.button_party_mon_up.pack    (side='left', expand=True, fill='x', padx=2)
        self.button_party_mon_down.pack  (side='left', expand=True, fill='x', padx=2)
        self.button_party_remove_mon.pack(side='left', expand=True, fill='x', padx=2)
        self.button_party_add_mon.pack   (side='left', expand=True, fill='x', padx=2)

        # Create the frame_trainer_items frame and insert it to the the second column of frame_party_and_items frame.
        frame_trainer_items = ttk.Frame(frame_party_and_items)
        frame_trainer_items.grid(row=0, column=1, sticky='nsew')

        ttk.Label(frame_trainer_items, text='Items').pack(anchor='w', pady=(0, 5))

        # Create the list_combobox_trainer_item and add one combobox for each item the trainer has
        # using a for loop.
        # They must be disabled if there is no project opened.
        self.list_combobox_trainer_item = []
        for _ in range(4):
            combobox_trainer_item = ttk.Combobox(frame_trainer_items, values=[], state='disabled')
            combobox_trainer_item.pack(fill='x', pady=2)
            self.list_combobox_trainer_item.append(combobox_trainer_item)


    def create_ai_flags_tab_notebook_trainer_battle_settings(self, notebook):
        '''
        Creates the content for `tab_trainer_ai_flags` which consists in a group of checkboxes with an AI Flag each one.
        They will be loaded into `self.list_ai_flags` and they will be added after loading the project.

        In pokeemerald expansion there are some presets for AI flags. This function adds a combobox to select one and a button to apply them
        only if the project is based on pokeemerald expansion. Otherwise, the box will be removed after loading the project.
        
        ** Workflow:**
        1. Create the `tab_trainer_ai_flags` frame and add it to the `notebook` tab collection
        2. Initialize the list of AI flags
        3. Create the `frame_ai_flags_presets` for the presets selector
        4. Create the label with text 'Preset' and add it to the `frame_ai_flags_presets`
        5. Create `combobox_ai_flags_presets` and add it to the `frame_ai_flags_presets` with some values
        6. Create `button_apply_ai_flags_preset` and add it to the `frame_ai_flags_presets`
        7. Create the `frame_trainer_ai_tags` for the AI flags checkboxes.

        ```
        ╔═══════════════════════════════════════════════════════════════════════════════════╗
        ║ tab_trainer_ai_flags                                                              ║
        ║╔═════════════════════════════════════════════════════════════════════════════════╗║
        ║║ frame_ai_flags_presets                                                          ║║
        ║║╔══════════╤════════════════════════════════╤═══════════════════════════════════╗║║
        ║║║"Preset:" | self.combobox_ai_flags_presets | self.button_apply_ai_flags_preset ║║║
        ║║╚══════════╧════════════════════════════════╧═══════════════════════════════════╝║║
        ║╚═════════════════════════════════════════════════════════════════════════════════╝║
        ║╔═════════════════════════════════════════════════════════════════════════════════╗║
        ║║ frame_trainer_ai_tags                                                           ║║
        ║║ [X] FLAG_1   [ ] FLAG_8    [ ] FLAG_16                                          ║║
        ║║ [ ] FLAG_2   [ ] FLAG_9    [ ] FLAG_17                                          ║║
        ║║ [ ] FLAG_3   [ ] FLAG_10   [ ] FLAG_18                                          ║║
        ║║ [ ] FLAG_4   [ ] FLAG_11   [ ] FLAG_19                                          ║║
        ║║ [ ] FLAG_5   [ ] FLAG_12   [ ] FLAG_20                                          ║║
        ║║ [ ] FLAG_6   [ ] FLAG_13   [ ] FLAG_21                                          ║║
        ║║ [ ] FLAG_7   [ ] FLAG_14   [ ] FLAG_22                                          ║║
        ║╚═════════════════════════════════════════════════════════════════════════════════╝║
        ╚═══════════════════════════════════════════════════════════════════════════════════╝
        ```
        '''
        # Create the tab_trainer_ai_flags frame and add it to the notebook tab collection
        self.tab_trainer_ai_flags = ttk.Frame(notebook)
        notebook.add(self.tab_trainer_ai_flags, text='AI Flags')

        # Initialize the list of AI flags
        self.list_ai_flags = []
        
        # In pokeemerald expansion there are some presets for AI flags. We will add a combobox to select one and a button to apply them
        # only if the project is based on pokeemerald expansion. Otherwise, the box will be removed at runtime.

        # Create the frame_ai_flags_presets for the presets selector
        self.frame_ai_flags_presets = ttk.Frame(self.tab_trainer_ai_flags)
        self.frame_ai_flags_presets.pack(side='top', pady=8, padx=8, anchor='w', fill='x')

        # Create the label with text 'Preset' and add it to the frame_ai_flags_presets
        ttk.Label(self.frame_ai_flags_presets, text='Preset:').pack(side='left', padx=(0, 5))

        # Create combobox_ai_flags_presets and add it to the frame_ai_flags_presets with some values
        # TODO: Make the preset list dynamic
        self.combobox_ai_flags_presets = ttk.Combobox(self.frame_ai_flags_presets, values=['Basic Trainer', 'Smart Trainer', 'Predict'], state='disabled')
        self.combobox_ai_flags_presets.pack(side='left', padx=(0, 5))

        # Create button_apply_ai_flags_preset and add it to the frame_ai_flags_presets
        self.button_apply_ai_flags_preset = ttk.Button(self.frame_ai_flags_presets, text='Apply', state='disabled')
        self.button_apply_ai_flags_preset.pack(side='left')

        # Create the frame_trainer_ai_tags for the AI flags checkboxes. They will be added after loading the project.
        self.frame_trainer_ai_tags = ttk.Frame(self.tab_trainer_ai_flags)
        self.frame_trainer_ai_tags.pack(side='bottom', pady=8, padx=8, expand=True)
        

    def create_trainer_locations_tab_notebook_trainer_battle_settings(self, notebook):
        '''
        Creates the content of `tab_trainer_places`, which consists in a list of maps where the trainer battle is found.
        Adds the necessary commands to launch the function `self.find_trainer_in_maps`.

        **Workflow:**
        1. Create the `tab_trainer_places` frame and add it to the `notebook` tab collection
        2. Create the label with text 'Maps where the trainer was found' and add it to the `tab_trainer_places`
        3. Create `listbox_trainer_map_appereances` and add it to the `tab_trainer_places`. 
        4. Create `button_find_trainer_in_maps` and add it to the `tab_trainer_places`. Sets the command `self.find_trainer_in_maps` to get a list of locations where a `trainerbattle` is found.
        
        ```
        ╔════════════════════════════════════════╗
        ║ tab_trainer_places                     ║
        ║╔══════════════════════════════════════╗║
        ║║ self.listbox_trainer_map_appereances ║║
        ║╠══════════════════════════════════════╣║
        ║║ self.button_find_trainer_in_maps     ║║
        ║╚══════════════════════════════════════╝║
        ╚════════════════════════════════════════╝
        ```
        '''
        # Create the tab_trainer_places frame and add it to the notebook tab collection
        tab_trainer_places = ttk.Frame(notebook)
        notebook.add(tab_trainer_places, text='Found at...')

        # Create the label with text 'Maps where the trainer was found' and add it to the tab_trainer_places
        ttk.Label(tab_trainer_places, text='Maps where the trainer was found').pack(anchor='w', pady=(10, 5), padx=10)

        # Create listbox_trainer_map_appereances and add it to the tab_trainer_places. 
        self.listbox_trainer_map_appereances = tk.Listbox(tab_trainer_places, height=8)
        self.listbox_trainer_map_appereances.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Create button_find_trainer_in_maps and add it to the tab_trainer_places. Sets the command self.find_trainer_in_maps to get a list of locations where a trainerbattle is found.
        self.button_find_trainer_in_maps = ttk.Button(tab_trainer_places, text='Find trainer', state='disabled', command=self.find_trainer_in_maps)
        self.button_find_trainer_in_maps.pack(side='bottom', pady=(0, 10))


    def create_status_bar(self):
        '''
        Creates and displays the status bar at the bottom of the main window.

        The status bar is used to show messages and feedback to the user.
        '''
        # Status bar at the bottom of the window to show messages to the user.
        self.status = tk.Label(self, text='Project not opened.', bd=1, relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')


    def open_project(self):
        ''' Open a folder dialog to select the project path and load its data. WIP.'''
        path = filedialog.askdirectory(title="Select project folder", initialdir=get_last_opened_project())
        if path:
            self.menu_bar.destroy()
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
                    self.project_data.expansion = self.check_expansion()
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
        self.menu_bar.entryconfig("Edit", state="normal")
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
            partymon_ui_spinners.append(self.dict_spinboxes_ivs["ATK"])
            partymon_ui_spinners.append(self.dict_spinboxes_ivs["DEF"])
            partymon_ui_spinners.append(self.dict_spinboxes_ivs["SPD"])
            partymon_ui_spinners.append(self.dict_spinboxes_ivs["SPATK"])
            partymon_ui_spinners.append(self.dict_spinboxes_ivs["SPDEF"])
            for stat in self.dict_spinboxes_evs:
                partymon_ui_spinners.append(self.dict_spinboxes_evs[stat])
            self.button_shiny_toggle.config(state="normal")
            self.button_toggle_dynamax.config(state="normal")
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
            checkbox = ttk.Checkbutton(self.frame_trainer_ai_tags, text=flag[10:], variable=var)
            checkbox.grid(row=i//2, column=i%2, sticky="w", padx=2, pady=1)
            self.list_ai_flags.append((flag, var))
        
        if self.project_data.expansion:
            self.combobox_ai_flags_presets.config(state="readonly")
            self.button_apply_ai_flags_preset.config(state="normal")
        
        else:
            self.frame_ai_flags_presets.destroy()


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
        for flag, var in self.list_ai_flags:
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

        if self.project_data.expansion:
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

        for flag in self.list_ai_flags:
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

