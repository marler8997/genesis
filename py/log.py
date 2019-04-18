import sys
import os
import shutil

verbose_enabled = False

def log(msg):
    print(msg, file=sys.stderr, flush=True)
def verbose(msg):
    if verbose_enabled:
        print(msg, file=sys.stderr, flush=True)
def flush():
    sys.stderr.flush()

def unlink(path):
    verbose("unlink '{}'".format(path))
    os.unlink(path)
def symlink(target, link_src):
    verbose("symlink '{}' > '{}'".format(link_src, target))
    os.symlink(target, link_src)
def copyfile(src, dst):
    verbose("copy '{}' to '{}'".format(src, dst))
    shutil.copyfile(src, dst)
def copytree(src, dst, **kwargs):
    symlinks = kwargs.get('symlinks')
    verbose("copytree {}'{}' to '{}'".format("symlinks=True " if symlinks else "", src, dst))
    shutil.copytree(src, dst, **kwargs)
def mkdir(path):
    verbose("mkdir '{}'".format(path))
    os.mkdir(path)
def mkdirs(path):
    verbose("mkdirs '{}'".format(path))
    os.makedirs(path)
def mkdirs_if_needed(path):
    if not os.path.exists(path):
        mkdirs(path)
def rename(src,dst):
    verbose("move '{}' to '{}'".format(src, dst))
    os.rename(src, dst)
def rmtree(path):
    verbose("rmtree '{}'".format(path))
    shutil.rmtree(path)
def rmdir(path):
    verbose("rmdir '{}'".format(path))
    os.rmdir(path)
def rmfile(file):
    verbose("rmfile '{}'".format(file))
    os.remove(file)

# merge the contents of src into dst
def merge_move_dir(src, dst):
    if not os.path.exists(dst):
        mkdirs_if_needed(os.path.dirname(dst))
        rename(src, dst)
    else:
        for entry in os.listdir(src):
            rename(os.path.join(src, entry), os.path.join(dst, entry))
        rmdir(src)

def merge_copy_dir(src, dst):
    if not os.path.exists(dst):
        mkdirs_if_needed(os.path.dirname(dst))
        shutil.copytree(src, dst, symlinks=True)
    else:
        for entry_base in os.listdir(src):
            entry_src = os.path.join(src, entry_base)
            entry_dst = os.path.join(dst, entry_base)
            if os.path.isdir(entry_src):
                shutil.copytree(entry_src, entry_dst, symlinks=True)
            else:
                shutil.copy(entry_src, entry_dst)

def unwrap_dir(path):
    dst_dir = os.path.dirname(path)
    for entry in os.listdir(path):
        src = os.path.join(path, entry)
        dst = os.path.join(dst_dir, entry)
        rename(src, dst)
    rmdir(path)
