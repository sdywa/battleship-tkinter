#!/bin/python3
import os
import random
from tkinter import *
import menu
import settings

import game

 
class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title('Main Page')
        self.master.resizable(0, 0)
        self.master.geometry(f'{settings.WIN_WIDTH}x{settings.WIN_HEIGHT}')
        self.master.bind('<Control-q>', lambda _: self.master.destroy())

        self.logo = self.get_logo('logos')

        self.draw_main_page()
        self.draw_meme()
        self.menu = menu.MainMenu(self.master, self.update_view)
        self.menu.change_theme()


    def draw_main_page(self):
        self.main = Frame(self.master)
        self.main.place(relx=0.5, rely=0.65, anchor=CENTER)

        self.title = Label(self.master, text=self.logo, font='monospace 6')
        self.login_btn = Button(self.main, text='log in',
                                command=lambda: self.menu.open_login())
        self.reg_btn = Button(self.main, text='create account',
                              command=lambda: self.menu.open_registration())
        self.title.place(relx=0.5, rely=0.35, anchor=CENTER)
        self.login_btn.pack(side=LEFT)
        Label(self.main, width=5).pack(side=LEFT)
        self.reg_btn.pack(side=LEFT)


    def draw_meme(self):
        Frame(self.master, height=15).pack(side=BOTTOM)
        self.name = Canvas(self.master, width=120, height=70, highlightthickness=0)
        self.name.pack(side=BOTTOM)

        self.name.create_line(40, 13, 45, 19, width=2)
        self.name.create_line(25, 15, 40, 15, width=2)
        self.name.create_line(25, 10, 15, 30, width=2)
        self.name.create_line(15, 27, 15, 45, width=2)
        self.name.create_line(15, 40, 25, 55, width=2)
        self.name.create_line(22, 53, 40, 53, width=2)
        self.name.create_line(40, 55, 45, 50, width=2)

        self.name.create_oval(55, 58, 57, 60, fill='black')

        self.name.create_line(70, 55, 83, 13, width=2)
        self.name.create_line(86, 13, 92, 53, width=2)
        self.name.create_line(80, 17, 90, 17, width=2)
        self.name.create_line(80, 35, 97, 35, width=2)

        self.name.create_oval(98, 55, 100, 57, fill='black')
        

    def update_view(self, style):
        widgets = self.master.winfo_children()
        for item in widgets:
            if children := item.winfo_children(): widgets.extend(children)
        
        self.master.configure(**style.space)
        for widget in widgets:
            class_name = widget.winfo_class()
            if class_name in {'Frame', 'Canvas'}: widget.config(**style.space)
            elif class_name == 'Label': widget.config(**style.text)
            elif class_name == 'Entry': widget.config(**style.entry)
            elif class_name == 'Button': widget.config(**style.button)


    def get_logo(self, path):
        titles = os.listdir(path)
        text = ''
        with open(os.path.join(path, random.choice(titles))) as f:
            text = f.read()

        return text
            

if __name__ == '__main__':
    root = Tk()
    window = MainWindow(root)
    root.mainloop()
