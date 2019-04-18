import os
import sys
import mmap
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log
import extract
import download
import proc
import elf
import genesis

def execute_op(gen_obj, op):
    name = op.get('op')
    if not name:
        sys.exit("Error: genesis object op is missing the 'op' property: {}".format(json.dumps(op)))
    if name == 'makeFile':
        makeFile(op)
    elif name == 'mkdir':
        mkdir(op)
    elif name == 'mkdirs':
        mkdirs(op)
    elif name == 'symlink':
        symlinkOp(op)
    elif name == 'fixSymlink':
        fixSymlinkOp(op)
    elif name == 'move':
        move(op)
    elif name == 'moveToDir':
        moveToDir(op)
    elif name == 'copyToDir':
        copyToDir(op)
    elif name == 'moveDirEntries':
        moveDirEntries(op)
    elif name == 'unwrapDir':
        unwrapDir(op)
    elif name == 'fetchArchive':
        fetchArchive(op)
    elif name == 'depend':
        depend(op, gen_obj.get_tmpout_path())
    elif name == 'addPackageLinks':
        addPackageLinks(op, gen_obj.get_tmpout_path())
    elif name == 'fixElf':
        fixElf(op)
    elif name == 'run':
        runOp(op)
    else:
        sys.exit("Error: unknown op '{}'".format(name))

def makeFile(op):
    path = op['path']
    content = op['content']
    makeDirs = op['makeDirs']
    if makeDirs:
        os.makedirs(os.path.dirname(path))
    with open(path, "w") as file:
        file.write(content)

def mkdir(op):
    path = op['path']
    log.mkdir(path)
def mkdirs(op):
    path = op['path']
    log.mkdirs(path)

def symlinkOp(op):
    path = op['path']
    to = op['to']
    log.symlink(to, path)

def fixSymlinkOp(op):
    path = op['path']
    to = op['to']
    # read the link to verify it is an existing symlink
    old_to = os.readlink(path)
    if old_to != to:
        log.unlink(path)
        log.symlink(to, path)

def move(op):
    src = op['src']
    dst = op['dst']
    log.rename(src, dst)
def moveToDir(op):
    src = op['src']
    dst = op['dst']
    log.rename(src, os.path.join(dst, os.path.basename(src)))
def copyToDir(op):
    src = op['src']
    dst = op['dst']
    dst_path = os.path.join(dst, os.path.basename(os.path.abspath(src)))
    if os.path.isdir(src):
        log.copytree(src, dst_path)
    else:
        log.copyfile(src, dst_path)
def moveDirEntries(op):
    src = op['src']
    dst = op['dst']
    log.merge_move_dir(src, dst)

# move the entries of a directory into the parent directory and remove that directory
def unwrapDir(op):
    path = op['path']
    log.unwrap_dir(path)

def get_unknown_hash():
    # TODO: this should probably have random/timestamp to avoid conflicts
    return 'unknownhashooooooooooooooooooooo'

def fetch_archive_to_ca(url, basename, in_hash):
    if len(in_hash) == 0:
        download_hash = get_unknown_hash()
    else:
        download_hash = in_hash
        ca_in_path = genesis.make_ca_path(in_hash, basename)
        if os.path.exists(ca_in_path):
            log.verbose("archive '{}' already fetched to '{}'".format(url, ca_in_path))
            return ca_in_path

    # TODO: need a lock file
    download_path = genesis.make_ca_stage_path(download_hash, basename)
    if os.path.exists(download_path):
        sys.exit("Error: cannot download '{}' because download path '{}' already exists".format(url, download_path))
    download.download(url, download_path)
    file_type, actual_in_hash = genesis.hash_path(download_path)
    if len(in_hash) == 0:
        new_path = genesis.make_ca_path(actual_in_hash, basename)
        log.rename(download_path, new_path)
        log.log("Please update inHash for '{}' to this:".format(url))
        log.log(actual_in_hash)
        sys.exit(1)
    if in_hash != actual_in_hash:
        log.log("inHash Mismatch for '{}', expected then actual:".format(url))
        log.log(in_hash)
        log.log(actual_in_hash)
        sys.exit(1)
    log.rename(download_path, ca_in_path)
    return ca_in_path

def fetch_extract_archive_to_ca(url, basename, in_hash, keep_basename, out_hash):
    extract_basename = extract.get_extracted_path(basename)

    if len(out_hash) == 0:
        extract_hash = get_unknown_hash()
    else:
        extract_hash = out_hash
        ca_out_path = genesis.make_ca_path(out_hash, extract_basename)
        if os.path.exists(ca_out_path):
            log.verbose("archive '{}' already fetched and extracted to '{}'".format(url, ca_out_path))
            return ca_out_path

    ca_in_path = fetch_archive_to_ca(url, basename, in_hash)
    extract_path = genesis.make_ca_stage_path(extract_hash, extract_basename)
    if os.path.exists(extract_path):
        sys.exit("Error: cannot extract '{}' because extract path '{}' already exists".format(ca_in_path, extract_path))

    actual_extract_basename = extract.extract(ca_in_path, extract_path, keep_basename=keep_basename)
    if not actual_extract_basename.endswith(extract_basename):
        sys.exit("Error(code bug) extract basename mismatch, expected '{}' got '{}'".format(
            extract_basename, actual_extract_basename))
    file_type, actual_out_hash = genesis.hash_path(extract_path)
    if len(out_hash) == 0:
        new_path = genesis.make_ca_path(actual_out_hash, extract_basename)
        log.rename(extract_path, new_path)
        log.log("Please update outHash for '{}' to this:".format(url))
        log.log(actual_out_hash)
        sys.exit(1)
    if out_hash != actual_out_hash:
        log.log("outHash Mismatch for '{}', expected then actual:".format(url))
        log.log(out_hash)
        log.log(actual_out_hash)
        sys.exit(1)
    log.rename(extract_path, ca_out_path)
    return ca_out_path

def fetchArchive(op):
    url = op['url']
    in_hash = op['inHash']
    out_hash = op['outHash']
    to = op['to']
    #keep_basename = op['keepBasename']
    keep_basename = False

    archive_basename = os.path.basename(url)
    ca_out_path = fetch_extract_archive_to_ca(url, archive_basename, in_hash, keep_basename, out_hash)

    log.merge_copy_dir(ca_out_path, to)
    #if keep_basename:
    #    log.mkdirs_if_needed(to)
    #    log.copytree(ca_out_path, os.path.join(to, os.path.basename(ca_out_path)), symlinks=True)
    #else:
    #    log.merge_copy_dir(ca_out_path, to)

# TODO: move this to another module
def replace_dir_seps(path):
    if os.name == "nt":
        return path.replace('/','\\')

def make_exe_link(target_exe, link_file):
    if os.name == "nt":
        # TODO: maybe .bat files won't work well, maybe we want .exe files
        #       since calling .bat files work differently when you call them from .bat files
        if target_exe.endswith(".exe"):
            link_file = link_file[:-4] + ".bat"
        elif target_exe.endswith(".bat"):
            link_file = link_file[:-4] + ".bat"
        else:
            sys.exit("not implemented, making an exe link when the exe does not end with '.exe' or '.bat' {}".format(target_exe))
        with open(link_file, "w") as file:
            file.write('@"{}" %*'.format(target_exe))
    else:
        log.symlink(target_exe, link_file)

def make_env_exe_link(target_exe, link_file):
    if os.path.exists(link_file):
        sys.exit("Error: conflict with file '{}'".format(link_file))
    log.mkdirs_if_needed(os.path.dirname(link_file))
    make_exe_link(target_exe, link_file)

def depend(op, tmpout):
    in_entry = op['in']
    if not os.path.isabs(in_entry):
        sys.exit("Error: non-absolute path depends not implemented '{}'".format(in_entry))
    if not genesis.abspath_is_in_root(in_entry):
        sys.exit("Error: this depend path isn't in the root /g? '{}'".format(in_entry))
    genesis_dir = os.path.join(tmpout, "genesis")
    log.mkdirs_if_needed(genesis_dir)
    with open(os.path.join(genesis_dir, "deps"), "a") as file:
        file.write("{}\n".format(in_entry))

def addPackageLinks(op, tmpout):
    path = op['path']
    if not os.path.exists(tmpout):
        os.mkdir(tmpout)
    bin = os.path.join(path, "bin")
    tmpout_bin = os.path.join(tmpout, "bin")
    if os.path.isdir(bin):
        if not os.path.exists(tmpout_bin):
            log.mkdir(tmpout_bin)
        for entry in os.listdir(bin):
            target_exe = os.path.join(bin, entry)
            link_file = os.path.join(tmpout_bin, entry)
            make_env_exe_link(target_exe, link_file)
    extra_bin_filename = os.path.join(path, "genesis", "extra-bin")
    if os.path.exists(extra_bin_filename):
        with open(extra_bin_filename, "r") as file:
            while True:
                entry = file.readline()
                if not entry:
                    break
                entry = entry.rstrip()
                target_exe = os.path.join(path, replace_dir_seps(entry))
                link_file = os.path.join(tmpout_bin, os.path.basename(entry))
                make_env_exe_link(target_exe, link_file)
    else:
        log.verbose("extra-bin file does not exist {}".format(extra_bin_filename))


_cached_patchelf = None
def get_patchelf():
    global _cached_patchelf
    if not _cached_patchelf:
        patchelf = os.path.join(os.path.dirname(os.path.abspath(script_dir)), 'patchelf')
        if not os.path.exists(patchelf):
            log.log("patchelf tool '{}' does not exist".format(patchelf))
            sys.exit("Error: run ./bootstrap-patchelf to build the patchelf tool")
        log.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        log.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        log.log("Using '{}' even though it isn't in genesis!".format(patchelf))
        log.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        log.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        _cached_patchelf = patchelf
    return _cached_patchelf

def fixElf(op):
    import corepkgs

    files = op['files']
    interp = op['interp']
    rpath = op['rpath']
    if not interp and not rpath:
        return

    # TODO: use patchelf from corepkgs
    #if rpath:
    #    chrpath64_pkg = corepkgs.build(corepkgs.chrpath64)
    #    chrpath64 = chrpath64_pkg + "/bin/chrpath"
    for file in files:
        log.log("FIXELF  {}".format(file))
        args = [get_patchelf()]
        if interp:
            args += ['--set-interpreter', interp]
            #elf.change_interpreter(file, interp.encode("ascii"))
        if rpath:
            #log.log("[DEBUG] chrpath is in '{}'".format(chrpath64))
            #proc.run(chrpath64
            #sys.exit("not impl")
            args += ['--set-rpath', rpath]
        proc.run(args + [file])


def runOp(op):
    cmd = op['cmd']
    env = op.get('env')
    if env:
        proc_env = {**os.environ, **env}
    else:
        proc_env = os.environ
    # TODO: limit the environment variables
    proc.run(cmd, env=proc_env)
