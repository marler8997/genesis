import sys
import os

if sys.version_info.major < 3 or sys.version_info.minor < 7:
    sys.exit("Error: requires python at least version 3.7, but running '{}.{}' (needed for subprocess.run capture_output)".
             format(sys.version_info.major, sys.version_info.minor))

import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log

def fix_args(args, **kwargs):
    if os.name == "nt":
        new_args = []
        for arg in args:
            new_args.append(arg.replace('/', '\\'))
        args = new_args
    return args

def check(obj, print_out_on_error):
    if obj.returncode != 0:
        if print_out_on_error:
            print(obj.stdout.decode('ascii'))
            print(obj.stderr.decode('ascii'), file=sys.stderr)
        obj.check_returncode()
    return obj

def run_impl(check_return_code, args, **kwargs):
    args = fix_args(args, **kwargs)
    cwd = kwargs.get("cwd")
    capture_output = kwargs.get("capture_output")
    log.verbose("[RUN{}] {}{}".format(
        "-CAPTURE-OUT" if capture_output else "",
        "CWD={} ".format(cwd) if cwd else "",
        " ".join(args)))
    result = subprocess.run(args, **kwargs)
    if check_return_code:
        check(result, False)
    if capture_output:
        return result.stdout.decode("ascii")
    return result

def run(args, **kwargs):
    return run_impl(True, args, **kwargs)

def run_no_check(args, **kwargs):
    return run_impl(False, args, **kwargs)

def run_output(args, **kwargs):
    kwargs['capture_output'] = True
    return run(args, **kwargs)

def sudo_args():
    if os.name == "nt":
        return []
    else:
        return ["sudo","PATH="+os.environ["PATH"]]

_cached_nt_python_args = None
def python_args():
    global _cached_nt_python_args
    if os.name == "nt":
        if not _cached_nt_python_args:
            python = subprocess.check_output(["where","python3"])
            if not python:
                sys.exit("Error: cannot find python3 in PATH")
            _cached_nt_python_args = [python.decode('ascii').rstrip()]
        return _cached_nt_python_args
    else:
        return []


def py(args, **kwargs):
    run(python_args() + args, **kwargs)
def py_output(args, **kwargs):
    return run_output(python_args() + args, **kwargs)

_cached_programs = {}

def get_program(name, to):
    cached = _cached_programs.get(name)
    if cached:
        return cached

    import distutils.spawn
    log.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    log.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    log.log("Using the '{}' tool to {} without declaring a dependency on it!".format(name, to))
    log.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    log.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    prog = distutils.spawn.find_executable(name)
    if not prog:
        sys.exit("Cannot {} because '{}' is not installed".format(to, name))
    _cached_programs[name] = prog
    return prog
