#! /usr/bin/env python3

import tkinter as tk
from tkinter import ttk

PROJECT_TYPES = [
    "pokeemerald",
    "pokeruby",
    "pokefirered",
    "pokeemerald-expansion"
]

class ProjectSelectionDialog:
    '''Dialog modal para seleccionar el tipo de proyecto.

    Se puede invocar desde otro módulo usando la función `ask_project(parent)` que
    devuelve el string seleccionado o None si el usuario cancela.
    '''

    def __init__(self, parent=None):
        self.parent = parent
        self.owns_parent = False

        self.window = tk.Toplevel(self.parent)
        self.window.title("Decomp Trainer Editor")
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        self.window.transient(self.parent)
        self.window.grab_set()

        frame_main = tk.Frame(self.window)
        frame_main.pack(fill=tk.BOTH, expand=True)

        frame_dialog = tk.Frame(frame_main, bd=2)
        frame_dialog.pack(side=tk.TOP, fill=tk.X)

        label_icon = tk.Label(frame_dialog, bitmap='question')
        label_icon.grid(row=0, column=0, padx=6, pady=6)
        ttk.Label(frame_dialog, text="Choose project type:").grid(row=0, column=1, padx=5, pady=2)

        frame_control = tk.Frame(frame_main, bd=2)
        frame_control.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.project_combobox = ttk.Combobox(frame_control, values=PROJECT_TYPES, state='readonly')
        self.project_combobox.pack(padx=2, pady=10, anchor='n')
        self.project_combobox.set(PROJECT_TYPES[0])

        btn_frame = tk.Frame(frame_control)
        btn_frame.pack(padx=5, pady=5)
        self.button_next = ttk.Button(btn_frame, text="Continue", command=self.on_continue)
        self.button_next.pack(side=tk.LEFT, padx=4)
        self.button_cancel = ttk.Button(btn_frame, text="Cancel", command=self.on_close)
        self.button_cancel.pack(side=tk.LEFT, padx=4)

        self.result = None
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_continue(self):
        self.result = self.project_combobox.get()
        self.window.destroy()

    def on_close(self):
        self.result = None
        self.window.destroy()


def ask_project(parent=None):
    '''Show project type modal dialog.'''
    dialog = ProjectSelectionDialog(parent)
    dialog.window.wait_window()
    result = dialog.result
    if dialog.owns_parent:
        dialog.parent.destroy()
    return result


if __name__ == "__main__":
    sel = ask_project()
    print("Selected:", sel)