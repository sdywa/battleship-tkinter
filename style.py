class Style:
    def __init__(self, style):
        self.style = style
        self.text = { 'bg': self.style['bg'],
                      'fg': self.style['text_color'] }
        self.space = { 'bg': self.style['bg'] }
        self.entry = { 'bg': self.style['entry_bg'],
                       'fg': self.style['text_color'],
                       'highlightbackground': self.style['entry_bg'],
                       'borderwidth': 0,
                       'font': 'ubuntu 10' }
        self.button = { 'bg': self.style['button_bg'],
                        'activebackground': self.style['hover_button_bg'],
                        'fg': self.style['button_text_color'],
                        'activeforeground': self.style['button_text_color'],
                        'highlightbackground': self.style['button_border_color'],
                        'font': 'ubuntu' }
        self.menu = { 'background': self.style['menu_bg'],
                      'activebackground': self.style['hover_menu_bg'],
                      'foreground': self.style['menu_text_color'],
                      'activeforeground': self.style['menu_text_color'],
                      'borderwidth': 0,
                      'font': 'ubuntu 10' }
        self.tile = { "fill": self.style['tile_color_bg'],
                      "outline": self.style['tile_outline_color'],
                      "width": 3 }
        self.ship = { "fill": self.style['ship_color'],
                      "outline": self.style['ship_outline_color'],
                      "width": 2 }
