from renderer2 import *
from py3dUtility import *
import tkinter as tk
import time

class py3DEngine:
    delta_time = 0
    input = None

    def main(self):
        d_time = time.time() - self.last_time
        py3DEngine.delta_time = d_time
        py3DEngine.input.update_values()
        for e in Entity.entity_list:
            for m in e.get_modules('all'):
                m.update()
        
        self.main_renderer.draw_frame([e for e in Entity.entity_list if isinstance(e, EnvironmentEntity)])

        self.last_time = time.time()
        self.root.after_idle(self.main)

    def __init__(self, height, width):
        self.root = tk.Tk()
        self.main_renderer = MainRenderer(self.root, height, width)
        py3DEngine.input = Inputs()
        
    def start_game(self):
        self.root.after(1,self.main)
        self.last_time = time.time()
        self.root.mainloop()

    def __del__(self):
        self.file.close()
