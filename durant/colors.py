ESC = '\033'
CSI = ESC + '['
OSC = ESC + ']'

ansi = {
    'Reset':      '0',
    'Black':      '0;30',
    'Red':        '0;31',
    'Green':      '0;32',
    'Yellow':     '0;33',
    'Blue':       '0;34',
    'Purple':     '0;35',
    'Cyan':       '0;36',
    'LightGray':  '0;37',
    'DarkGray':   '1;30', 
    'BoldRed':    '1;31',
    'BoldGreen':  '1;32',
    'BoldYellow': '1;33',
    'BoldBlue':   '1;34',
    'BoldPurple': '1;35',
    'BoldCyan':   '1;36',
    'White':      '1;37'
}

class Codes(object):
    def __init__(self):
        for name in ansi:
            setattr(self, name.upper(), CSI + ansi[name] + 'm')                                        

colors = Codes()
