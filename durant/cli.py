import os

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
