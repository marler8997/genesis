import os

def fix_path_sep(path):
    if os.path.sep != '/':
        path = path.replace('/', os.path.sep)
    return path

def execfile(filename, *args):
    with open(filename, "r") as file:
        code = compile(file.read(), filename, 'exec')
        exec(code, *args)
