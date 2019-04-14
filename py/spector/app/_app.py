import tkinter as tk
from tkinter import ttk

from spector.app.main import MainController
from . import spectrum
from .. import core


class Application:
    def __init__(self, process: core.main.Process = None):
        self.process = process if isinstance(process, core.main.Process) else core.main.Process()
        self.process.try_process()
        
        self.window = tk.Tk()
        self.window.title("PositronSpector")
        
        self.menu = None
        self.init_menu()

        self.tree = None
        self.init_tree()
    
        self.container = tk.Frame(self.window, width=500, height=500)
        self.container.pack(side='left', fill='both', padx='4p', pady='4p')
        self.controller = None
        self.init_frame()
        
        self.window.mainloop()
    
    def init_menu(self):
        self.menu = tk.Menu(self.window)

        menu_file = tk.Menu(self.menu, tearoff=0)
        menu_file.add_command(label='New')
        menu_file.add_command(label='Open')
        self.menu.add_cascade(label="File", menu=menu_file)

        menu_help = tk.Menu(self.menu, tearoff=0)
        menu_help.add_command(label='About')
        self.menu.add_cascade(label='Help', menu=menu_help)
        
        self.window.config(menu=self.menu)
        self.update_menu()
    
    def update_menu(self):
        pass
    
    def init_tree(self):
        self.tree: ttk.Treeview = ttk.Treeview(self.window, show="tree")
        self.tree.pack(side='left', fill='y')
        self.tree.bind('<ButtonRelease-1>', self.on_tree_clicked)
        self.update_tree()
    
    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        main_node = self.tree.insert('', 'end', text='Main', value=['main'], open=True)
        
        for i, spectrum_process in enumerate(self.process.spectrum_process_list):
            spectrum_node = self.tree.insert(main_node, 'end', text='Spectrum_' + str(i), value=['spectrum', i])
            self.tree.insert(spectrum_node, 'end', text='raw data', value=['spectrum', i, 'raw'])
            self.tree.insert(spectrum_node, 'end', text='resolution', value=['spectrum', i, 'res'])
            self.tree.insert(spectrum_node, 'end', text='peak', value=['spectrum', i, 'peak'])
            self.tree.insert(spectrum_node, 'end', text='background', value=['spectrum', i, 'bg'])
        
        for i, artifact_process in enumerate(self.process.artifact_process_list):
            self.tree.insert(main_node, 'end', text='Artifact_' + str(i), value=['artifact', i])
    
    def on_tree_clicked(self, _):
        item = self.tree.item(self.tree.focus())
        values = item['values']
        if len(values) > 0:
            self.update_frame(values)
    
    def init_frame(self):
        self.update_frame(['main'])
    
    def update_frame(self, key=None):
        self.controller = None
        for child in self.container.winfo_children():
            child.destroy()
        
        if key is None or len(key) == 0:
            return

        if key[0] == 'main':
            self.controller = MainController(self)
        elif key[0] == 'spectrum':
            spectrum_index = key[1]
            spectrum_process = self.process.spectrum_process_list[spectrum_index]
            if isinstance(spectrum_process, core.spectrum.dbs.Process):
                if len(key) == 2:
                    self.controller = spectrum.Controller(self, spectrum_index)
                elif key[2] == 'raw':
                    self.controller = spectrum.dbs.raw.Controller(self, spectrum_index)
                elif key[2] == 'res':
                    pass
                elif key[2] == 'peak':
                    pass
                elif key[2] == 'bg':
                    pass  # todo sub items of spectrum
            pass
        elif key[0] == 'artifact':
            #  todo artifact frame
            pass

        if self.controller is not None:
            self.controller.frame.pack(side='left', fill='both')
