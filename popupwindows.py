import os
import textwrap
import bcrypt
from tkinter import *
from PIL import ImageTk, Image
import game
import settings


class PopupWindow:
    def __init__(self, master, title, geometry='280x180'):
        self.master = master
        self.win = Toplevel(self.master)
        self.win.geometry(geometry)
        self.win.bind('<Control-q>', lambda _: self.win.destroy())

        self.win.title(title)
        self.win.resizable(0, 0)


    def update_view(self):
        widgets = self.master.winfo_children()

        for item in widgets:
            if children := item.winfo_children(): widgets.extend(children)
            
        self.win.configure(**self.master.theme.space)
        for widget in widgets:
            class_name = widget.winfo_class()
            if class_name == 'Frame': widget.config(**self.master.theme.space)
            elif class_name == 'Label': widget.config(**self.master.theme.text)
            elif class_name == 'Entry': widget.config(**self.master.theme.entry)
            elif class_name == 'Button': widget.config(**self.master.theme.button)

        if 'errors_label' in vars(self): 
            self.errors_label.config(fg=self.master.theme.style['error'])


    def pack_errors(self, error_obj, errors):
        if len(errors):
            error_obj['text'] = '\n'.join(errors.values())
            error_obj.pack()
        else:
            error_obj.pack_forget()

    
    def is_destroyed(self):
        return not self.win.winfo_exists()


    def destroy(self):
        self.win.destroy()


class AboutWindow(PopupWindow):
    def __init__(self, master, username=''):
        super().__init__(master, 'About', '600x220')
        self.draw_window()


    def draw_window(self):
        self.main = Frame(self.win, bd=30)
        self.main.pack()

        img = Image.open(settings.IMG_PATH)
        img_resized = img.resize((150, 150), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img_resized)
        self.img = Label(self.main, image=img)
        self.img.image = img
        self.img.grid(row=0, column=0)

        Frame(self.main, width=30).grid(row=0, column=1)

        text = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Pulvinar sapien et ligula ullamcorper malesuada proin libero. Tortor vitae purus faucibus ornare suspendisse sed nisi lacus.'''
        wrapped = '\n'.join(textwrap.wrap(text, width = 50))
        self.label = Label(self.main, text=wrapped, justify=LEFT, font='ubuntu 12')
        self.label.grid(row=0, column=2)

        self.update_view()


class LoginWindow(PopupWindow):
    def __init__(self, master, username=''):
        super().__init__(master, 'Log In')
        self.draw_window(username)
        if not os.path.isfile(settings.DB_PATH):
            os.mknod(settings.DB_PATH)


    def draw_window(self, username):
        Frame(self.win, height=7).pack()
        Label(self.win, text='Log in', font='ubuntu 14 bold').pack()

        self.form = Frame(self.win, bd=10)
        self.form.pack()
        
        Label(self.form, text='username:   ', font='ubuntu 12').grid(row=0, column=0)
        self.username_entry = Entry(self.form)
        self.username_entry.insert(END, username)
        self.username_entry.bind('<Return>', lambda _: self.apply())
        Label(self.form, text='password:   ', font='ubuntu 12').grid(row=1, column=0)
        self.password_entry = Entry(self.form, show="*")
        self.password_entry.bind('<Return>', lambda _: self.apply())
        self.errors_label = Label(self.win, font='ubuntu 10')
        
        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)
        
        self.btns = Frame(self.win, bd=15)
        self.btns.pack(side=BOTTOM)

        self.log_btn = Button(self.btns, text='Log in', command=self.apply)
        self.cancel_btn = Button(self.btns, text='Cancel', command=self.win.destroy)

        self.log_btn.pack(side=LEFT)
        Label(self.btns, width=3).pack(side=LEFT)
        self.cancel_btn.pack(side=LEFT)

        self.update_view()
        

    def apply(self):
        errors = {}
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            errors['empty_fields'] = 'Enter your username and password'
        
        if len(errors): 
            self.pack_errors(self.errors_label, errors)
            return

        with open(settings.DB_PATH) as f:
            users = f.readlines()

        userdata = ('', '')
        for user in users:
            name, _, passwd = user.rpartition(' ')
            passwd = passwd.replace('\n', '')
            if name == username:
                userdata = (name, passwd)
                break

        if bcrypt.checkpw(password.encode(), userdata[1].encode()):
            self.win.destroy()
            game.Game(self.master, name)
        else:
            errors['wrong_input'] = 'Wrong username or password'
            self.pack_errors(self.errors_label, errors)


class RegWindow(PopupWindow):
    def __init__(self, master):
        super().__init__(master, 'Registration')
        self.draw_window()
        if not os.path.isfile(settings.DB_PATH):
            os.mknod(settings.DB_PATH)


    def draw_window(self):
        Frame(self.win, height=7).pack()
        Label(self.win, text='Registration', font='ubuntu 14 bold').pack()

        self.form = Frame(self.win, bd=10)
        self.form.pack()

        Label(self.form, text='username:   ', font='ubuntu 12').grid(row=0, column=0)
        self.username_entry = Entry(self.form)
        self.username_entry.bind('<Return>', lambda _: self.register())
        Label(self.form, text='password:   ', font='ubuntu 12').grid(row=1, column=0)
        self.password_entry = Entry(self.form, show="*")
        self.password_entry.bind('<Return>', lambda _: self.register())
        self.errors_label = Label(self.win, font='ubuntu 10')
        
        self.username_entry.grid(row=0, column=1)
        self.password_entry.grid(row=1, column=1)

        self.btns = Frame(self.win, bd=15)
        self.btns.pack(side=BOTTOM)

        self.log_btn = Button(self.btns, text='Create Account', command=self.register)
        self.cancel_btn = Button(self.btns, text='Cancel', command=self.win.destroy)

        self.log_btn.pack(side=LEFT)
        Label(self.btns, width=3).pack(side=LEFT)
        self.cancel_btn.pack(side=LEFT)

        self.update_view()


    def register(self):
        errors = {}
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            errors['empty_fields'] = 'Enter your username and password'

        self.pack_errors(self.errors_label, errors)
        if len(errors): return

        with open(settings.DB_PATH) as f:
            users = f.readlines()

        for user in users:
            name, *_ = user.rpartition(' ')
            if name == username:
                errors['wrong_input'] = 'This username is not available'

        if len(errors): 
            self.pack_errors(self.errors_label, errors)
            return
        
        with open(settings.DB_PATH, 'a') as f:
            f.write(f'{username} {bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()}\n')

        self.win.destroy()
        LoginWindow(self.master)
