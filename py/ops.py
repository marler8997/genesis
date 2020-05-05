import os
import sys
import struct
import time
import multiprocessing
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

_disable_op_fail_message = False

class OpExecutor:
    def __init__(self):
        self.extra_env = {}
        self.prepended_path_envs = None
        self.appended_path_envs = None
    def execute(self, gen_obj, op):
        try:
            self.execute2(gen_obj, op)
        except:
            if not _disable_op_fail_message:
                log.log("Error: failed to execute op '{}'".format(op))
            raise
    def execute2(self, gen_obj, op):
        name = op.get('op')
        if not name:
            sys.exit("Error: genesis object op is missing the 'op' property: {}".format(json.dumps(op)))
        if name == 'cd':
            cdOp(op)
        elif name == 'setEnv':
            setEnv(self, op)
        elif name == 'prependPathEnv':
            prependPathEnv(self, op)
        elif name == 'makeFile':
            makeFile(op)
        elif name == 'mkdir':
            mkdir(op)
        elif name == 'mkdirs':
            mkdirs(op)
        elif name == 'symlink':
            symlinkOp(op)
        elif name == 'exelink':
            exelinkOp(op)
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
        elif name == 'copyDirEntries':
            copyDirEntries(op)
        elif name == 'linkDirEntries':
            linkDirEntries(op)
        elif name == 'unwrapDir':
            unwrapDir(op)
        elif name == 'fileReplace':
            fileReplaceOp(op)
        elif name == 'fetchFile':
            fetchFile(op)
        elif name == 'fetchArchive':
            fetchArchive(op)
        elif name == 'depend':
            depend(op, gen_obj.get_tmpout_path())
        elif name == 'addPackageLinks':
            addPackageLinks(op, gen_obj.get_tmpout_path())
        elif name == 'fixElf':
            fixElf(op)
        elif name == 'run':
            runOp(self, op, gen_obj.bootstrap)
        elif name == 'runMake':
            runMakeOp(self, op, gen_obj.bootstrap)
        else:
            sys.exit("Error: unknown op '{}'".format(name))

def normalizePath(path):
    if os.name == 'nt':
        return path.replace('/','\\')
    return path

def cdOp(op):
    path = op['path']
    log.chdir(path)

def setEnv(executor, op):
    name = op['name']
    value = op['value']
    executor.extra_env[name] = value

def prepend_path_env(path_env, new):
    if not new:
        return path_env
    if not path_env:
        return new
    return "{}{}{}".format(new, os.pathsep, path_env)
def append_path_env(path_env, new):
    if not new:
        return path_env
    if not path_env:
        return new
    return "{}{}{}".format(path_env, os.pathsep, new)

def prependPathEnv(executor, op):
    path = op['path']
    executor.prepended_path_envs = prepend_path_env(
        executor.prepended_path_envs, replace_dir_seps(path))

def makeFile(op):
    path = op['path']
    content = op['content']
    makeDirs = op.get('makeDirs')
    mode = op.get('mode')
    if makeDirs:
        os.makedirs(os.path.dirname(path))
    with open(path, "w") as file:
        file.write(content)
    if mode != None:
        if not mode.startswith('0'):
            raise Exception("Error: mode should be an octal string starting with '0' but is '{}'".format(mode))
        os.chmod(path, int(mode, 8))

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

def exelinkOp(op):
    path = normalizePath(op['path'])
    to = normalizePath(op['to'])
    if os.name == 'nt':
        # NOTE: for now just use bat files, but might need to support exes
        with open(path + ".bat", "w") as file:
            if not os.path.isabs(to):
                tostring = "%~dp0" + to
            else:
                tostring = to
            file.write("@" + tostring + " %*")
    else:
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
def copyDirEntries(op):
    src = op['src']
    dst = op['dst']
    log.merge_copy_dir(src, dst)
def linkDirEntries(op):
    src = op['src']
    dst = op['dst']
    log.merge_link_dir(src, dst)

# move the entries of a directory into the parent directory and remove that directory
def unwrapDir(op):
    path = op['path']
    log.unwrap_dir(path)

def fileReplaceOp(op):
    replace = op['replace'].encode('ascii')
    with_ = op['with'].encode('ascii')
    files = op['files']
    for filename in files:
        with open(filename, 'rb') as file:
            content = file.read()
        if replace in content:
            with open(filename, 'wb') as file:
                file.write(content.replace(replace, with_))

def get_unknown_hash():
    # using a timestamp to avoid conflicts
    #timestamp = time.time()
    #bytes = struct.pack('f',timestamp)
    #to_size = 10
    #if len(bytes) < to_size:
    #    bytes = (b'\0'*(to_size-len(bytes))) + bytes
    #elif len(bytes) > to_size:
    #    bytes = bytes[-to_size:]
    #return 'unknownhashooooo' + genesis.encode_genesis_hash(bytes).decode('ascii')
    return 'unknownhashooooooooooooooooooooo'

def fetch_archive_to_ca(url, basename, in_hash, hash_name):
    global _disable_op_fail_message
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
        correct_path = genesis.make_ca_path(actual_in_hash, basename)
        if os.path.exists(correct_path):
            log.rmtree_or_file(download_path)
        else:
            log.rename(download_path, correct_path)
        log.log("Please update {} for '{}' to this:".format(hash_name, url))
        log.log(actual_in_hash)
        _disable_op_fail_message = True
        sys.exit(1)
    if in_hash != actual_in_hash:
        log.log("{} Mismatch for '{}', expected then actual:".format(hash_name, url))
        log.log(in_hash)
        log.log(actual_in_hash)
        _disable_op_fail_message = True
        sys.exit(1)
    log.rename(download_path, ca_in_path)
    return ca_in_path

def fetchFile(op):
    url = op['url']
    hash = op['hash']
    to_dir = op['toDir']
    if not os.path.exists(to_dir):
        log.log("Error: cannot fetchFile '{}' toDir '{}' because that dir does not exist".format(url,to_dir))
        sys.exit(1)

    basename = os.path.basename(url)
    ca_path = fetch_archive_to_ca(url, basename, hash, 'hash')
    log.copyfile(ca_path, os.path.join(to_dir, basename))

def fetch_extract_archive_to_ca(url, basename, in_hash, keep_basename, out_hash):
    global _disable_op_fail_message
    extract_basename = extract.get_extracted_path(basename)

    if len(out_hash) == 0:
        extract_hash = get_unknown_hash()
    else:
        extract_hash = out_hash
        ca_out_path = genesis.make_ca_path(out_hash, extract_basename)
        if os.path.exists(ca_out_path):
            log.verbose("archive '{}' already fetched and extracted to '{}'".format(url, ca_out_path))
            return ca_out_path

    ca_in_path = fetch_archive_to_ca(url, basename, in_hash, 'inHash')
    extract_path = genesis.make_ca_stage_path(extract_hash, extract_basename)
    if os.path.exists(extract_path):
        sys.exit("Error: cannot extract '{}' because extract path '{}' already exists".format(ca_in_path, extract_path))

    actual_extract_basename = extract.extract(ca_in_path, extract_path, keep_basename=keep_basename)
    if not actual_extract_basename.endswith(extract_basename):
        sys.exit("Error(code bug) extract basename mismatch, expected '{}' got '{}'".format(
            extract_basename, actual_extract_basename))
    file_type, actual_out_hash = genesis.hash_path(extract_path)
    if len(out_hash) == 0:
        correct_path = genesis.make_ca_path(actual_out_hash, extract_basename)
        if os.path.exists(correct_path):
            log.rmtree(extract_path)
        else:
            log.rename(extract_path, correct_path)
        log.log("Please update outHash for '{}' to this:".format(url))
        log.log(actual_out_hash)
        _disable_op_fail_message = True
        sys.exit(1)
    if out_hash != actual_out_hash:
        log.log("outHash Mismatch for '{}', expected then actual:".format(url))
        log.log(out_hash)
        log.log(actual_out_hash)
        _disable_op_fail_message = True
        sys.exit(1)
    log.rename(extract_path, ca_out_path)
    return ca_out_path

def fetchArchive(op):
    url = op['url']
    in_hash = op['inHash']
    out_hash = op['outHash']
    # TODO: rename this to 'copyTo' and make it optional
    copy_to = op.get('to')
    #keep_basename = op['keepBasename']
    keep_basename = False

    archive_basename = os.path.basename(url)
    ca_out_path = fetch_extract_archive_to_ca(url, archive_basename, in_hash, keep_basename, out_hash)

    if copy_to:
        log.merge_copy_dir(ca_out_path, copy_to)
    #if keep_basename:
    #    log.mkdirs_if_needed(to)
    #    log.copytree(ca_out_path, os.path.join(to, os.path.basename(ca_out_path)), symlinks=True)
    #else:
    #    log.merge_copy_dir(ca_out_path, to)

# TODO: move this to another module
def replace_dir_seps(path):
    if os.name == "nt":
        return path.replace('/','\\')
    return path

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

# Returns: True if added, False if it was already added
def add_depend_if_not_added(dep_file, dep):
    if not os.path.exists(dep_file):
        with open(dep_file, "wb") as file:
            file.write(dep + b'\n')
        return True
    with open(dep_file, "r+b") as file:
        with mmap.mmap(file.fileno(), 0, mmap.ACCESS_READ) as mem:
            file_length = len(mem)
            if mem.find(dep) >= 0:
                #log.log("[DEBUG] depend '{}' already added".format(dep))
                return False # not added
        #log.log("[DEBUG] depend '{}' NOT added".format(dep))
        file.seek(file_length)
        file.write(dep + b'\n')
    return True

def addPackageLinks(op, tmpout):
    path = op['path']
    add_package_links(path, tmpout)

def add_package_links(path, tmpout):
    genesis_dir = os.path.join(tmpout, "genesis")
    log.mkdirs_if_needed(genesis_dir)

    #log.log("[DEBUG] add_package_links '{}'".format(path))
    env_dep_file = os.path.join(tmpout, "genesis", "deps")
    if not add_depend_if_not_added(env_dep_file, path.encode('ascii')):
        return

    # add deps deps
    deps_filename = os.path.join(path, "genesis", "deps")
    if not os.path.exists(deps_filename):
        log.verbose("deps file does not exist {}".format(deps_filename))
    else:
        with open(deps_filename, "r") as file:
            while True:
                entry = file.readline()
                if not entry:
                    break
                entry = entry.rstrip()
                add_package_links(entry, tmpout)


    bin = os.path.join(path, "bin")
    tmpout_bin = os.path.join(tmpout, "bin")
    if os.path.isdir(bin):
        if not os.path.exists(tmpout_bin):
            log.mkdir(tmpout_bin)
        for entry in os.listdir(bin):
            target_exe = os.path.join(bin, entry)
            link_file = os.path.join(tmpout_bin, entry)
            #log.log("[DEBUG] linking {}".format(link_file))
            make_env_exe_link(target_exe, link_file)
    extra_bin_filename = os.path.join(path, "genesis", "extra-bin")
    if not os.path.exists(extra_bin_filename):
        log.verbose("extra-bin file does not exist {}".format(extra_bin_filename))
    else:
        with open(extra_bin_filename, "r") as file:
            while True:
                entry = file.readline()
                if not entry:
                    break
                entry = entry.rstrip()
                target_exe = os.path.join(path, replace_dir_seps(entry))
                link_file = os.path.join(tmpout_bin, os.path.basename(entry))
                make_env_exe_link(target_exe, link_file)

def fixElf(op):
    import corepkgs

    files = op['files']
    interp = op.get('interp')
    rpath = op.get('rpath')
    if not interp and not rpath:
        log.log("Error: the 'fixElf' operation requires either 'interp' or 'rpath'")
        sys.exit()

    for file in files:
        log.log("FIXELF  {}".format(file))
        args = [corepkgs.get_patchelf_bootstrap()]
        if interp:
            args += ['--set-interpreter', interp]
            #elf.change_interpreter(file, interp.encode("ascii"))
        if rpath:
            #log.log("[DEBUG] chrpath is in '{}'".format(chrpath64))
            #proc.run(chrpath64
            #sys.exit("not impl")
            args += ['--set-rpath', rpath]
        proc.run(args + [file])




def update_path(executor, env):
    if executor.prepended_path_envs or executor.appended_path_envs:
        env['PATH'] = append_path_env(
            prepend_path_env(env.get('PATH'), executor.prepended_path_envs),
            executor.appended_path_envs)
        #log.log("[DEBUG] path is '{}'".format(env['PATH']))

# If we update the PATH to be able to run different programs
# then we need to do it in os.environ becuase python looks
# for the binary in the same process.
class ScopedEnv:
    def __init__(self, executor):
        self.save_path = None
        self.executor = executor
    def __enter__(self):
        #log.log("[DEBUG] ENTER env: '{}'".format(os.environ))
        self.save_path = os.environ.get('PATH')
        update_path(self.executor, os.environ)
    def __exit__(self, type, value ,traceback):
        if self.save_path == None:
            os.environ.pop('PATH', None)
        else:
            os.environ['PATH'] = self.save_path
        #log.log("[DEBUG] EXIT env: '{}'".format(os.environ))

def make_env(executor, bootstrap, extra_env):
    env = {}
    if executor.extra_env:
        env = {**env,**executor.extra_env}
    if extra_env:
        env = {**env,**extra_env}
    if os.name == 'nt':
        # for now I'm just always including c:\windows\system32 in the path for windows
        env['PATH'] = append_path_env(env.get('PATH'), r'C:\Windows\System32')
        #    env['PATHEXT'] = '.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC'
    if bootstrap:
        # no need to call update_path(executor, env) because it's assumed
        # that PATH will have already been updated in os.environ with a ScopedEnv
        env = {**env, **os.environ}
    else:
        update_path(executor, env)
    return env

def runOp(executor, op, bootstrap):
    cmd = op['cmd']
    # TODO: keep the same environment accross all ops
    # TODO: pull in the environment from all the inputs?
    #       maybe some inputs we want to pull in the environment and some we don't?
    #       if so, I could just select which ones I want to pull in with an op.
    #       it would be similar to addPackageLinks but it would't be adding them to
    #       the @tmpout directory but instead the stage directory.
    env = op.get('env')
    with ScopedEnv(executor) as env:
        proc_env = make_env(executor, bootstrap, env)
        #log.log("[DEBUG] proc_env:")
        #import pprint
        #pprint(proc_env)
        proc.run(cmd, env=proc_env)

def runMakeOp(executor, op, bootstrap):
    args = op['args']
    env = op.get('env')
    with ScopedEnv(executor) as env:
        proc.run(['make','-j'+str(multiprocessing.cpu_count())] + args,
                 env=make_env(executor, bootstrap, env))
