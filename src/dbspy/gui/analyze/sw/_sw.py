import tkinter as tk
import tkinter.ttk as ttk

import matplotlib.pyplot as plt
import numpy as np

from dbspy.gui.utils.figure import FigureResultController
from dbspy.gui import base
from dbspy.core.analyze.sw import Conf


class Controller(FigureResultController, base.ElementProcessController):
    def __init__(self, app, index):
        from dbspy.gui import Application
        self.app: Application = app
        self.index = index
        self.conf_rs = tk.StringVar()
        self.conf_rw = tk.StringVar()
        self.conf_ra = tk.StringVar()
        self.conf_w_mode = tk.StringVar()
        super().__init__(
            app.container,
            app.process.analyze_processes[index],
            plt.figure(figsize=(7, 5)))
    
    def on_create_info_frame(self, info_frame):
        tk.Label(info_frame, text=f'#{self.index} SW Analyze').pack()
        tk.Button(info_frame, text='Remove', foreground='red', command=self.remove).pack()
    
    def on_create_conf_frame(self, conf_frame):
        tk.Label(conf_frame, text='rs=').pack(side='left')
        tk.Entry(conf_frame, width=6, textvariable=self.conf_rs).pack(side='left')
        tk.Label(conf_frame, text='eV').pack(side='left')
        
        tk.Label(conf_frame, text='rw=').pack(side='left', padx=(10, 0))
        tk.Entry(conf_frame, width=6, textvariable=self.conf_rw).pack(side='left')
        tk.Label(conf_frame, text='eV').pack(side='left')
        
        tk.Label(conf_frame, text='ra=').pack(side='left', padx=(10, 0))
        tk.Entry(conf_frame, width=6, textvariable=self.conf_ra).pack(side='left')
        tk.Label(conf_frame, text='eV').pack(side='left')
        
        tk.Label(conf_frame, text="w_mode=").pack(side='left', padx=(10, 0))
        ttk.OptionMenu(conf_frame, self.conf_w_mode, 'all', *Conf.w_modes).pack(side='left')
    
    def on_reset(self, conf: Conf):
        self.conf_rs.set(str(conf.s_radius))
        self.conf_rw.set(str(conf.w_radius))
        self.conf_ra.set(str(conf.a_radius))
        self.conf_w_mode.set(str(conf.w_mode))
    
    def on_apply(self) -> Conf:
        return Conf(
            s_radius=float(self.conf_rs.get()),
            w_radius=float(self.conf_rw.get()),
            a_radius=float(self.conf_ra.get()),
            w_mode=self.conf_w_mode.get())
    
    def on_update_draw(self, figure, result, exception):
        if result is not None:
            tag_list = tuple(process.tag for process in self.app.process.spectrum_processes)
            s_list, s_var_list, w_list, w_var_list = zip(*(
                (s, s_var, w, w_var) for (s, s_var, _), (w, w_var, _) in result))
            
            sp_index = 0
            (x, y, _), _ = self.app.process.spectrum_processes[sp_index].value
            (_, _, s_range_i), (_, _, w_range_i) = result[sp_index]
            peak_i = np.argmax(y)
            
            axe_sp = figure.add_subplot(2, 1, 1)
            axe_s = figure.add_subplot(2, 2, 3)
            axe_w = figure.add_subplot(2, 2, 4)
            
            axe_sp.fill_between(x[slice(*s_range_i)], y[slice(*s_range_i)], color='#0088ff')
            if isinstance(w_range_i[0], tuple):
                w1_range_i, w2_range_i = w_range_i
                axe_sp.fill_between(x[slice(*w1_range_i)], y[slice(*w1_range_i)], color='#ff8800')
                axe_sp.fill_between(x[slice(*w2_range_i)], y[slice(*w2_range_i)], color='#ff8800')
            else:
                axe_sp.fill_between(x[slice(*w_range_i)], y[slice(*w_range_i)], color='#ff8800')
            
            axe_sp.plot(x, y, color='black')
            axe_sp.plot([x[peak_i], x[peak_i]], [0, y[peak_i]], '--', color='black')
            
            axe_s.set_title("S")
            axe_s.errorbar(tag_list, s_list, np.sqrt(s_var_list), capsize=3, fmt='.-', color='#0088ff')
            axe_w.set_title("W")
            axe_w.errorbar(tag_list, w_list, np.sqrt(w_var_list), capsize=3, fmt='.-', color='#ff8800')
        else:
            figure.gca().set_title("Error!")
            # todo show info
    
    def remove(self):
        self.app.process.remove_analyze_process(self.process)
        self.app.update_frame(['main'])
        self.app.update_tree()
