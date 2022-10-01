import os
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