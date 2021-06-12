import os
import json
from tkinter import *
from tkinter.messagebox import *
import style
import popupwindows
import settings


class MainMenu:
    def __init__(self, master, update, username=''):
        self.master = master
        self.update = update
        self.username = username
        self.popup_win = None

        if not os.path.isfile(settings.THEMES_PATH):
            os.mknod(settings.THEMES_PATH)

        if self.username and (theme := self.read_user_theme(self.username)): self.default_theme = theme
        else: self.default_theme = 'dark'
        self.read_themes()
        self.draw_menu()


    def draw_menu(self):
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)

        self.file_menu = Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.file_menu)

        self.users_menu = Menu(self.file_menu)
        self.file_menu.add_cascade(label='Change User', menu=self.users_menu)
        self.fill_user_menu(self.users_menu, settings.DB_PATH)
        self.file_menu.add_command(label='About', command=lambda: self.open_window(popupwindows.AboutWindow))
        self.file_menu.add_command(label='Exit', command=lambda: self.master.destroy())

        self.view_menu = Menu(self.menu)
        self.menu.add_cascade(label='View', menu=self.view_menu)
        self.view_menu.add_command(label='Light Theme', command=lambda: self.change_theme('light'))
        self.view_menu.add_command(label='Dark Theme', command=lambda: self.change_theme('dark'))


    def update_view(self, style):
        widgets = self.menu.winfo_children()
        widgets.append(self.menu)
        if self.popup_win and not self.popup_win.is_destroyed(): self.popup_win.update_view()

        for item in widgets:
            if children := item.winfo_children(): widgets.extend(children)
        
        for widget in widgets:
            widget.config(**style.menu)


    def read_themes(self, path='themes/'):
        self.themes = {}
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            with open(file_path) as f:
                data = json.load(f)
                self.themes[data['name']] = data['body']


    def set_theme(self, st):
        self.master.theme = style.Style(st)


    def change_theme(self, theme_name=None):
        if theme_name:
            self.set_theme(self.themes[self.default_theme] if theme_name == 'default' else self.themes[theme_name])
            if self.username: self.save_user_theme(self.username, theme_name)
        else:
            if self.username and theme_name: self.save_user_theme(self.username, theme_name)
            self.set_theme(self.themes[self.default_theme])

        self.update(self.master.theme)
        self.update_view(self.master.theme)
        

    def save_user_theme(self, username, theme):
        with open(settings.THEMES_PATH) as f:
            users = [i.replace('\n', '').rsplit(' ', 1) for i in f.readlines()]
        
        for user in users:
            if user[0] == username:
                user[1] = theme
                break
        else:
            users.append([username, theme])


        with open(settings.THEMES_PATH, 'w') as f:
            for name, theme in users:
                f.write(f'{name} {theme}\n')


    def read_user_theme(self, username):
        with open(settings.THEMES_PATH) as f:
            users = [i.replace('\n', '').rpartition(' ') for i in f.readlines()]

        for user in users:
            if user[0] == username:
                return user[2]


    def fill_user_menu(self, menu, db_path):
        if not os.path.isfile(db_path):
            os.mknod(db_path)

        with open(db_path) as f:
            users = f.readlines()
        
        for data in users:
            name, *_ = data.rpartition(' ')
            self.add_user(menu, name)


    def add_user(self, menu, name):
        menu.add_command(label=name, command=lambda: self.open_login(name))


    def open_login(self, *args):
        self.open_window(popupwindows.LoginWindow, *args)


    def open_registration(self, *args):
        self.open_window(popupwindows.RegWindow, *args)


    def open_window(self, window, *args):
        if self.popup_win: self.popup_win.destroy()
        self.popup_win = window(self.master, *args)
