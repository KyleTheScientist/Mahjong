import os
import inspect

from colorama import Fore, Style, init

init()

def src_directory():
    return os.path.dirname(os.path.realpath(__file__))

def repository_path():
    return os.path.join(src_directory(), os.pardir)

def static():
    return os.path.join(repository_path(), 'web/static')

def templates():
    return os.path.join(repository_path(), 'web/templates')

def color(string, color):
    fore = getattr(Fore, color.upper())
    return f'{fore}{string}{Style.RESET_ALL}'

def cprint(string, color):
    fore = getattr(Fore, color.upper())
    print(f'{fore}{string}{Style.RESET_ALL}')

def log(message):
    _class = inspect.stack()[1][0].f_locals["self"].__class__.__name__
    if _class == 'Game':
        clr = 'cyan'
    else:
        clr = 'green'
    print(color(_class, clr), message)

def string_list(tiles):
    return ''.join([str(t) for t in tiles])

