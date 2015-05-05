from __future__ import print_function

import os
import time

from colors import colors


def output(text, color=None, reset=True):
    output = (color if color else '') + text
    if reset:
        output += colors.RESET

    return output


def output_dots(text, char='.', end=None, size=None, color=None, reset=True):
    if not size:
        size = int(get_console_size()[-1])

    chars = char * (size - len(text))
    if end:
        chars = chars[len(end):]

    return output(text + chars, color, reset)


def get_console_size():
    rows, columns = os.popen('stty size', 'r').read().split()
    return (rows, columns)


class Console(object):
    def log(self, text, color=None, prefix=True, end='\n'):
        if prefix:
            date = output('[' + time.strftime('%X') + '] ',
                          color=colors.YELLOW)
            text = date + text
            
        print(output(text, color), end=end)

    def done(self, text='DONE', end='\n'):
        return self.log(text, color=colors.GREEN, prefix=False, end=end)

    def fail(self, text='FAIL', end='\n'):
        return self.log(text, color=colors.RED, prefix=False, end=end)

    def error(self, text, prefix='ERROR: ', end='\n'):
        err = output(prefix, color=colors.RED)
        return self.log(err + text)

    def nl(self):
        return self.log('', prefix=False)


console = Console()
