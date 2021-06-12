from tkinter import *
import settings


class Ship():
    def __init__(self, canvas, init_pos, count=1):
        self.ROTATE_BTN = '<Button-3>'
        self.sections = []
        self.killed_sections = []
        self.canvas = canvas
        self.count = count
        self.init_pos = init_pos
        self.is_rotated = False
        self.is_fixed = False
        self.draw_ship()


    def draw_ship(self):
        for i in range(self.count):
            pos = (self.init_pos[0], self.init_pos[1] + i * settings.TILE_SIZE)
            shifted_pos = (pos[0] + settings.TILE_SIZE, pos[1] + settings.TILE_SIZE)
            section = self.canvas.create_rectangle(pos, shifted_pos, tag='ship')
            self.canvas.tag_bind(section, self.ROTATE_BTN, self.rotate)
            self.canvas.tag_bind(section, '<ButtonPress-1>', self.on_begin_drag)
            self.canvas.tag_bind(section, '<B1-Motion>', self.on_drag)
            self.canvas.tag_bind(section, '<ButtonRelease-1>', self.on_end_drag)
            self.sections.append(section)


    def update_view(self, style):
        for section in self.sections:
            self.canvas.itemconfig(section, style)


    def kill_section(self, _id):
        if _id in self.sections: self.killed_sections.append(_id)


    def rotate(self, event):
        x, y, *_ = self.canvas.coords(self.sections[0])
        for section in self.sections[1:]:
            coords = self.canvas.coords(section)
            if self.is_rotated: diff = x - coords[0]
            else: diff = -(y - coords[1])
            self.canvas.move(section, diff, -diff)

        self.is_rotated = not self.is_rotated

        if not self.is_placeable():
            self.is_fixed = False
            self.move_to_start()


    def move_to_start(self):
        speed = 2

        x, *_ = self.canvas.coords(self.sections[0])
        if (x > self.init_pos[0]): speed = -speed
        count = (self.init_pos[0] - x) / speed
        count = abs(int(count))
        for i in range(0, count):
            self.canvas.after(i, lambda: self.lerp_move(speed))

        self.canvas.after(count, lambda: self.move_ship(*self.init_pos))


    def move_ship(self, x, y):
        for i in range(self.count):
            if self.is_rotated:
                pos = (x + i * settings.TILE_SIZE, y)
            else:
                pos = (x, y + i * settings.TILE_SIZE)
            shifted_pos = (pos[0] + settings.TILE_SIZE, pos[1] + settings.TILE_SIZE)

            self.canvas.moveto(self.sections[i], *pos)


    def lerp_move(self, speed):
        pos = self.canvas.coords(self.sections[0])[:2]
        x, y = self.lerp(pos, self.init_pos, speed)
        self.move_ship(x - 1, y - 1)


    def lerp(self, start, end, t):
        x0, y0 = start
        x1, y1 = end
        x = x0 + t

        a = (y1 - y0) / (x1 - x0)
        b = y0 - a * x0
        y = a * x + b

        return x, y


    def fix_ship(self):
        for section in self.sections:
            self.canvas.tag_unbind(section, self.ROTATE_BTN)
            self.canvas.tag_unbind(section, '<ButtonPress-1>')
            self.canvas.tag_unbind(section, '<B1-Motion>')
            self.canvas.tag_unbind(section, '<ButtonRelease-1>')


    def is_placeable(self):
        tiles = []
        shift = settings.TILE_SIZE / 2
        x0, y0 = self.canvas.coords(self.sections[0])[:2]
        x1, y1 = self.canvas.coords(self.sections[-1])[2:]
        box_coords = [x0 - shift, y0 - shift, x1 + shift, y1 + shift]
        overlaps = self.canvas.find_overlapping(*box_coords)
        if sum(['ship' in self.canvas.gettags(i) for i in overlaps]) > self.count:
            return False
        
        for section in self.sections:
            x0, y0, x1, y1 = self.canvas.coords(section)
            shift = settings.TILE_SIZE / 2
            
            box_coords = [x0 + shift, y0 + shift, x1 - shift, y1 - shift]
            lowest_tile = self.canvas.find_overlapping(*box_coords)[0]
            tags = self.canvas.gettags(lowest_tile)
            if lowest_tile == section or 'tile' not in tags:
                return False
            tiles.append(lowest_tile)
            
        return tiles


    def is_section_in_ship(self, _id):
        return _id in self.sections


    def is_killed(self):
        return len(self.killed_sections) == self.count


    def on_begin_drag(self, event):
        self.is_fixed = False
        self.mouse_pos = (event.x, event.y)
        for section in self.sections:
            self.canvas.tag_raise(section)


    def on_drag(self, event):
        for section in self.sections:
            self.canvas.move(section, event.x - self.mouse_pos[0], event.y - self.mouse_pos[1])

        self.mouse_pos = (event.x, event.y)


    def on_end_drag(self, event):
        tiles = self.is_placeable()
        if not tiles:
            self.move_to_start()
            return

        for tile, section in zip(tiles, self.sections):
            tile_coords = [i - 1 for i in self.canvas.coords(tile)[:2]]
            self.canvas.moveto(section, *tile_coords)

        self.is_fixed = True
