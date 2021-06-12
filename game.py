import os
import time
import socket
import threading
from tkinter import *
import menu
import ship
import settings


class Game():
    def __init__(self, master, username):
        self.master = master
        self.master.title('Battleship')
        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.username = username
        self.connection = threading.Thread(target=self.connect)

        self.clear()
        self.initialize()
        self.menu = menu.MainMenu(self.master, self.update_view, username)
        self.menu.change_theme()


    def initialize(self):
        self.temp_text = None
        self.tiles = []
        self.enemy_tiles = []
        self.shoots = []
        self.SIZE_X, self.SIZE_Y = 10, 10
        
        self.canvas = Canvas(self.master, highlightthickness=0,
                             width=settings.WIN_WIDTH, height=settings.WIN_HEIGHT)
        self.canvas.bind('<Button-1>', self.update_start_btn)
        self.canvas.bind('<Button-3>', self.update_start_btn)
        self.canvas.bind('<ButtonRelease-1>', self.update_start_btn)
        self.canvas.pack()

        self.username_text = self.canvas.create_text(15, 10, text=self.username, anchor='nw',
                                                     font='ubuntu 14 bold')
        self.enemy_text = self.canvas.create_text(settings.WIN_WIDTH - 15, 10, anchor='ne',
                                                  font='ubuntu 14 bold')
        self.draw_ships()
        self.draw_tiles(self.tiles)


    def connect(self):
        data = (settings.HOST, settings.PORT)
        with socket.socket() as s:
            try:
                s.bind(data)
            except OSError:
                s.connect(data)
                self.client = s
                self.is_my_turn = False
            else:
                text = 'please wait for another player'
                self.temp_text = self.canvas.create_text(settings.WIN_WIDTH // 1.8, settings.WIN_HEIGHT // 2, 
                                        text=text, anchor='w', fill=self.master.theme.style['text_color'],
                                        font='ubuntu 14 bold')
                s.listen(5)
                conn, addr = s.accept()
                self.client = conn
                self.canvas.delete(self.temp_text)
                self.is_my_turn = True
            self.client.send(self.username.encode('utf-8'))
            username = self.client.recv(1024).decode('utf-8')

            field = '\\'.join([','.join(map(str, row)) for row in self.get_parsed_field()])
            self.client.send(field.encode('utf-8'))
            enemy_field = self.client.recv(1024).decode('utf-8')
            self.prepare_enemy(username, enemy_field)
            self.get_data()


    def get_data(self):
        while True:
            user_input = self.client.recv(1024).decode('utf-8')
            com, _, text = user_input.partition(' ')
            coords = map(int, text.split())
            if com == 'enemy': 
                self.is_my_turn = True
                self.shoot_from_enemy(coords)
            elif com == 'user': 
                self.shoot(self.get_tile(list(coords), self.enemy_tiles))


    def draw_tiles(self, tiles_list, shift=0, tag=''):
        OFFSET_X, OFFSET_Y = 70, 50

        for y in range(self.SIZE_Y):
            row = []
            for x in range(self.SIZE_X):
                pos = (OFFSET_X + settings.TILE_SIZE * x + shift,
                       OFFSET_Y + settings.TILE_SIZE * y)
                shifted_pos = (pos[0] + settings.TILE_SIZE, pos[1] + settings.TILE_SIZE)
                tile = self.canvas.create_rectangle(pos, shifted_pos, tag='tile')
                if tag: self.canvas.addtag(tag, 'withtag', tile)
                row.append(tile)
            tiles_list.append(row)


    def draw_ships(self):
        OFFSET_X, OFFSET_Y = 70, 60
        SHIFT = settings.WIN_WIDTH // 2
        self.ships = []
        self.enemy_ships = []

        # rewrite this pls
        for i in range(4):
            for j in range(0, 4 - i):
                if j: y = OFFSET_Y + settings.TILE_SIZE * ((i + 1) * j + j)
                else: y = OFFSET_Y + settings.TILE_SIZE * j * 2

                if i == 1 and j == 2:
                    y -= settings.TILE_SIZE
                    x = SHIFT + OFFSET_X + settings.TILE_SIZE * 6
                else:
                    x = SHIFT + OFFSET_X + settings.TILE_SIZE * i * 2
                self.ships.append(ship.Ship(self.canvas, (x, y), i + 1))

        self.start_btn = Button(self.canvas, text='Start', font='ubuntu', state='disabled')
        self.start_btn_id = self.canvas.create_window(SHIFT + OFFSET_X + settings.TILE_SIZE * 3.5,
                                                      OFFSET_Y + settings.TILE_SIZE * 8.5,
                                                      window=self.start_btn)
        self.start_btn.bind('<Button-1>', self.start_game)


    def update_view(self, style):
        self.canvas.config(**style.space)
        self.canvas.itemconfig(self.username_text, fill=style.style['text_color'])
        self.canvas.itemconfig(self.enemy_text, fill=style.style['text_color'])
        self.canvas.itemconfig(self.temp_text, fill=style.style['text_color'])

        for row in self.tiles:
            for tile in row:
                self.canvas.itemconfig(tile, **style.tile)

        for row in self.enemy_tiles:
            for tile in row:
                self.canvas.itemconfig(tile, **style.tile)

        for shoot in self.shoots:
            self.canvas.itemconfig(shoot, fill=style.style['shoot_color'])

        for ship in self.ships:
            ship.update_view(style.ship)

        for ship in self.enemy_ships:
            self.canvas.config(ship, **style.ship)

        self.start_btn.configure(**style.button)


    def update_start_btn(self, _):
        if self.is_fixed():
            self.start_btn['state'] = 'normal'
            self.start_btn.bind('<Button-1>', self.start_game)
        else:
            self.start_btn['state'] = 'disabled'
            self.start_btn.unbind('<Button-1>')
        self.start_btn.bind('<Button-1>', self.start_game)


    def clear(self):
        widgets = self.master.winfo_children()
        for widget in widgets:
            widget.destroy()


    def start_game(self, event):
        for ship in self.ships:
            ship.fix_ship()

        self.canvas.delete(self.start_btn_id)
        
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<Button-3>')
        self.canvas.unbind('<ButtonRelease-1>')

        self.canvas.bind('<Button-1>', self.mouse_shoot)
        self.connection.start()


    def prepare_enemy(self, username, field):
        self.canvas.itemconfig(self.enemy_text, text=username)
        self.draw_tiles(self.enemy_tiles, settings.WIN_WIDTH // 2, 'enemy')
        field = [item.split(',') for item in field.split('\\')]
        for field_row, tiles_row in zip(field, self.enemy_tiles):
            for item, tile in zip(field_row, tiles_row):
                if item == '1': self.canvas.addtag('ship', 'withtag', tile)
        self.update_view(self.master.theme)


    def shoot(self, obj):
        shoot_color = self.master.theme.style['shoot_color']
        coords = self.canvas.coords(obj)

        tags = self.canvas.gettags(obj)
        if 'ship' in tags:
            self.is_my_turn = not self.is_my_turn
            major = coords
            minor = [coords[0], coords[3], coords[2], coords[1]]
            shoot = self.canvas.create_line(*major, width=2, fill=shoot_color)
            self.shoots.append(shoot)
            self.canvas.create_line(*minor, width=2, fill=shoot_color)
            self.shoots.append(shoot)
        elif 'tile' in tags:
            shift = settings.TILE_SIZE * 0.35
            shoot_coords = (coords[0] + shift, coords[1] + shift,
                            coords[2] - shift, coords[3] - shift)
            shoot = self.canvas.create_oval(*shoot_coords, fill=shoot_color, width=0)
            self.shoots.append(shoot)

        self.canvas.addtag('shooted', 'withtag', obj)


    def mouse_shoot(self, event):
        if self.is_my_turn: self.shoot_enemy((event.x, event.y))


    def shoot_from_enemy(self, coords):
        x, y = coords
        shift = settings.TILE_SIZE / 2
        x0, y0, x1, y1 = self.canvas.coords(self.tiles[x][y])
        box_coords = [x0 + shift, y0 + shift, x1 - shift, y1 - shift]

        obj = self.canvas.find_overlapping(*box_coords)[-1]
        self.shoot(obj)
        for ship in self.ships:
            if ship.is_section_in_ship(obj): 
                ship.kill_section(obj)
                if not ship.is_killed(): return

                shift = settings.TILE_SIZE / 2
                x0, y0 = self.canvas.coords(ship.sections[0])[:2]
                x1, y1 = self.canvas.coords(ship.sections[-1])[2:]
                box_coords = [x0 + shift, y0 + shift, x1 - shift, y1 - shift]
                ship_tiles = {i for i in self.canvas.find_overlapping(*box_coords) 
                              if 'tile' in self.canvas.gettags(i)}
                box_coords = [x0 - shift, y0 - shift, x1 + shift, y1 + shift]
                overlaps = {i for i in self.canvas.find_overlapping(*box_coords) 
                            if 'tile' in self.canvas.gettags(i)}

                diff = overlaps - ship_tiles
                for item in diff:
                    tile = self.get_shoot_index(item, self.tiles)
                    self.shoot(item)
                    self.send_shoot(tile, 'user')
                    time.sleep(.001)

                if self.is_finished(): print('end')
                break


    def shoot_enemy(self, coords):        
        obj = self.canvas.find_closest(*coords)[0]
        tags = self.canvas.gettags(obj)

        if 'shooted' in tags: return
        if not 'enemy' in tags: return
        if 'ship' in tags:
            # TODO: fix coords for creating ships
            section = self.canvas.create_rectangle(self.canvas.coords(obj), tag='ship',
                                                   **self.master.theme.ship)
            self.enemy_ships.append(section)
            

        self.send_shoot(self.get_shoot_index(obj, self.enemy_tiles))
        self.shoot(obj)


    def send_shoot(self, coords, com='enemy'):
        text = ' '.join(map(str, coords))
        self.is_my_turn = False
        self.client.send(f'{com} {text}'.encode('utf-8'))


    def get_parsed_field(self):
        field = []
        shift = settings.TILE_SIZE / 2

        for row in self.tiles:
            field_row = []
            for tile in row:
                x0, y0, x1, y1 = self.canvas.coords(tile)
                box_coords = [x0 + shift, y0 + shift, x1 - shift, y1 - shift]
                upper_item = self.canvas.find_overlapping(*box_coords)[-1]
                field_row.append(int('ship' in self.canvas.gettags(upper_item)))
            field.append(field_row)
        return field


    def get_shoot_index(self, target, tiles):
        for i, row in enumerate(tiles):
            if target in row:
                return (i, row.index(target))
        else:
            raise ValueError('There is no such target in the array')


    def get_tile(self, coords, tiles):
        return tiles[coords[0]][coords[1]]


    def is_fixed(self):
        for ship in self.ships:
            if not ship.is_fixed: return False
            
        return True


    def is_finished(self):
        for ship in self.ships:
            if not ship.is_killed(): return False

        return True


    def on_closing(self):
        self.master.destroy()
        os._exit(0)
