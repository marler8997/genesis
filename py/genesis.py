import os
import sys
import enum
import json
import hashlib
import shutil
import mmap

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log
import ops

global_keep_stage = False

def on_windows():
    return os.name == "nt"

def get_root_path():
    if on_windows():
        store = "C:\g"
    else:
        store = "/g"
    return store
def get_ca_path():
    return os.path.join(get_root_path(), "ca")
def get_ca_stage_path():
    return os.path.join(get_root_path(), "ca", "stage")
def get_obj_path():
    return os.path.join(get_root_path(), "o")
def get_obj_stage_path():
    return os.path.join(get_root_path(), "o", "stage")
def get_stage_path():
    return os.path.join(get_root_path(), "stage")
def get_proxy_path():
    return os.path.join(get_root_path(), "proxy")

def make_hash_name(hash, name):
    return hash + "-" + name
def split_hash_name(name):
    # TODO: check the hash?
    return name[0:GEN_OBJ_HASH_CHAR_COUNT], name[GEN_OBJ_HASH_CHAR_COUNT + 1:]

def make_package_path(hash, name):
    return os.path.join(get_root_path(), make_hash_name(hash, name))
def make_obj_path(hash, name):
    return os.path.join(get_obj_path(), make_hash_name(hash,name))
def make_obj_stage_path(hash, name):
    return os.path.join(get_obj_stage_path(), make_hash_name(hash,name))
def make_stage_path(hash, name):
    return os.path.join(get_stage_path(), make_hash_name(hash, name))
def make_ca_path(hash, name):
    return os.path.join(get_ca_path(), make_hash_name(hash,name))
def make_ca_stage_path(hash, name):
    return os.path.join(get_ca_stage_path(), make_hash_name(hash,name))

def paths_equal(a,b):
    if on_windows():
        return a.lower() == b.lower()
    else:
        return a == b

def path_is_in_root(path):
    return abspath_is_in_root(path)
def abspath_is_in_root(abspath):
    return paths_equal(os.path.dirname(abspath), get_root_path())

def path_is_in_obj(path):
    return abspath_is_in_obj(path)
def abspath_is_in_obj(abspath):
    return paths_equal(os.path.dirname(abspath), get_obj_path())

def path_is_in_ca(path):
    return abspath_is_in_ca(path)
def abspath_is_in_ca(abspath):
    return paths_equal(os.path.dirname(abspath), get_ca_path())



def build(file):
    if not path_is_in_obj(file):
        sys.exit("Error: refusing to build genesis file '{}' that is not installed in the store '{}'".format(file, get_obj_path()))
    gen_obj = GenesisObject.from_file(file)
    return gen_obj.build()


'''
sha256 is 256 bits or or 32 bytes

base32 is 5 bits per character
we don't need that many bits so we just take the first 160

that comes out to 20 bytes or 32 characters

we also use lowercase instead of uppercase because it's easer to type
'''
GEN_OBJ_HASH_CHAR_COUNT = 32
def encode_genesis_hash(s):
    import base64
    return base64.b32encode(s).lower()

def hash_file(file):
    hasher = GenesisHasher()
    hasher.hash_file(file)
    return hasher.finish()
def hash_path(path):
    hasher = GenesisHasher()
    path_type = hasher.hash_path(path)
    return path_type, hasher.finish()

class PathType(enum.Enum):
    DIR = 0
    LINK = 1
    FILE = 2

class GenesisHasher:
    def __init__(self):
        self.hash = hashlib.sha256()
    def update(self, data):
        self.hash.update(data)
    def finish(self):
        return encode_genesis_hash(self.hash.digest()[0:20]).decode("ascii")

    def start_dir_hash(self):
        self.update(b"d")
    def start_link_hash(self):
        self.update(b"l")
    def start_file_content_hash(self):
        self.update(b"f")

    def hash_file_content_string(self, file_content_str):
        self.hash_file_content_bytes(file_content_str.encode("ascii"))
    def hash_file_content_bytes(self, file_content_bytes):
        self.start_file_content_hash()
        self.update(file_content_bytes)
    def hash_file(self, file):
        with open(file, "rb") as fd:
            try:
                data = mmap.mmap(fd.fileno(), 0, access = mmap.ACCESS_READ)
            except ValueError as e:
                if str(e) == "cannot mmap an empty file":
                    data = b''
                else:
                    raise
            self.hash_file_content_bytes(data)
    def hash_link(self, link):
        self.start_link_hash()
        self.update(os.readlink(link).encode("ascii"))
    def hash_dir(self, dir):
        self.start_dir_hash()
        # Need to sort so the hash is alwasy the same
        entries = os.listdir(dir)
        entries.sort()
        for entry_basename in entries:
            self.update(entry_basename.encode("ascii"))
            entry = os.path.join(dir, entry_basename)
            self.hash_path(entry)
    def hash_path(self, path):
        # TODO: just call fstat instead
        if os.path.isdir(path):
            self.hash_dir(path)
            return PathType.DIR
        elif os.path.islink(path):
            self.hash_link(path)
            return PathType.LINK
        else:
            self.hash_file(path)
            return PathType.FILE

def is_valid_at_var_char(c):
    if c >= 'a':
        return c <= 'z'
    if c >= 'A':
        return c <= 'Z' or c == "_"
    if c >= '0':
        return c <= '9'
    return c == "-" or c == "." or c == "+"

def get_at_var_name(str, at_index):
    assert(str[at_index] == '@')
    index = at_index + 1
    if index >= len(str):
        sys.exit("Error: string '{}' cannot end with '@'".format(str))
    while True:
        c = str[index]
        if not is_valid_at_var_char(c):
            break;
        index += 1
        if index == len(str):
            break;
    return str[at_index + 1 : index]

class ProcessState(enum.Enum):
    # processing the data so it can be hashed
    #   @out is not resolved
    HASHING = 0
    # processing the data for the purpose of building it
    #   @out is resolved to the 'tmpout' path
    BUILDING = 1

def get_unknown_props(dict, known_props):
    unknown_props = []
    for key,value in dict.items():
        if not key in known_props:
            unknown_props.append(key)
    return unknown_props

class ProcessErrorContext:
    LIST = 0
    def __init__(self):
        self.stack = []
    def push_list_item(self, list, index):
        self.stack.append((ProcessErrorContext.LIST, list, index))
    def pop_list_item(self, list, index):
        assert(self.stack.pop() == (ProcessErrorContext.LIST, list, index))
    def dump(self):
        for type,arg1,arg2 in self.stack:
            if type == ProcessErrorContext.LIST:
                print("CONTEXT: {}".format(arg1[arg2]))
            else:
                sys.exit("error context not impl")

class GenesisObject:
    def from_data(name, data):
        return GenesisObject(name, data.get('config',{}), data["in"], data["ops"])
    def from_file(filename):
        abspath = os.path.abspath(filename)
        basename = os.path.basename(abspath)
        hash, name = split_hash_name(basename)
        with open(filename, "r") as file:
            data = json.load(file)
        obj = GenesisObject(name, data.get('config',{}), data["in"], data["ops"])

        # verify hash is correct
        if hash != obj.get_hash():
            log.log("Error: genesis object file '{}' has the wrong, actual hash is:".format(basename))
            log.log(hash)
            sys.exit(1)
        return obj
    def __init__(self, name, config, in_list, raw_ops):
        self.name = name
        self.bootstrap = name.endswith('-bootstrap')
        self.bootstrap2 = name.endswith('-bootstrap2')
        unknown_config_props = get_unknown_props(config, ['notmpout', 'ifaces'])
        if len(unknown_config_props) > 0:
            log.log("Error: genesis object '{}' config has {} unknown property(s) '{}'".format(
                name, len(unknown_config_props), ",".join(unknown_props)))
            sys.exit(1)
        self.config = config
        self.notmpout = config.get('notmpout')
        self.ifaces = config.get('ifaces')

        self.in_list = in_list
        self.in_map = {}
        self.in_hash_name_map = {}
        for in_entry in in_list:
            if (not self.bootstrap) and (not self.bootstrap2):
                in_is_bootstrap = in_entry.endswith('-bootstrap') or in_entry.endswith('-bootstrap2')
                if in_is_bootstrap:
                    log.log("Error: package '{}' is NOT a bootstrap package but 'in' dependency '{}' is".format(
                        self.name, in_entry))
                    sys.exit(1)
            hash,name = split_hash_name(in_entry)
            in_finalout = os.path.join(get_root_path(), in_entry)
            self.in_map[name] = in_finalout
            self.in_hash_name_map[in_entry] = in_finalout

        self.raw_ops = raw_ops
        self.hashdata_ops = None
        self.processed_ops = None
        self.hashdata = None
        self.hash = None
        self.hash_name = None
        self.out_store_path = None
        self.obj_path = None
        self.obj_stage_path = None
        self.stage_path = None
        self.tmpout_path = None


    def raise_error(self, msg):
        raise Exception(msg)
    def raise_error_with_context(self, context, msg):
        context.dump()
        raise Exception(msg)

    def try_resolve_var(self, name, state):
        if name.startswith("in."):
            field = name[3:]
            if len(field) == 0:
                self.raise_error("'@in.' requires a name after it")
            return self.in_map.get(field)
        if name == "tmpout":
            if state == ProcessState.HASHING:
                return "@tmpout"
            elif state == ProcessState.BUILDING:
                return self.get_tmpout_path()
            else:
                sys.exit("Error(codebug): unknown process state '{}'".format(state))
        if name == "stage":
            if state == ProcessState.HASHING:
                return "@stage"
            elif state == ProcessState.BUILDING:
                return self.get_stage_path()
            else:
                sys.exit("Error(codebug): unknown process state '{}'".format(state))
        if name == "finalout":
            if state == ProcessState.HASHING:
                return "@finalout"
            elif state == ProcessState.BUILDING:
                return self.get_finalout_path()
            else:
                sys.exit("Error(codebug): unknown process state '{}'".format(state))

        result = self.in_hash_name_map.get(name)
        if result:
            return result
        # use to support @<in-name> but now it requires @in.<in-name>
        #if name in self.in_map:
        #    return self.in_map[name]
        return None
    def resolve_var(self, name, state, error_context):
        result = self.try_resolve_var(name, state)
        if not result:
            if self.in_map.get(name):
                self.raise_error_with_context(error_context, "in genesis object '{}': '@{}' variable reference is missing 'in.', it should be '@in.{}'".format(self.name, name, name))
            self.raise_error_with_context(error_context, "in genesis object '{}': '@{}' is not defined".format(self.name, name))
        return result

    def get_hashdata_ops(self):
        if not self.hashdata_ops:
            self.hashdata_ops = self.process_list(self.raw_ops, ProcessState.HASHING, ProcessErrorContext())
        return self.hashdata_ops

    def process_string(self, str, state, error_context):
        at_index = str.find('@')
        if at_index == -1:
            return str
        if (at_index + 1 < len(str)) and (str[at_index + 1] == '@'):
            keep = 2 if state == ProcessState.HASHING else 1
            return str[0:at_index+keep] + self.process_string(str[at_index + 2:], state, error_context)
        var_name = get_at_var_name(str, at_index)
        resolved = self.resolve_var(var_name, state, error_context)
        return str[:at_index] + resolved + self.process_string(str[at_index + 1 + len(var_name):], state, error_context)
    def process_dict(self, dict, state, error_context):
            newDict = {}
            for key,value in dict.items():
                newDict[key] = self.process_something(value, state, error_context)
            return newDict
    def process_list(self, list, state, error_context):
        # todo: optimization, newList has a fixed size
        newList = []
        for i in range(0, len(list)):
            error_context.push_list_item(list, i)
            result = self.process_something(list[i], state, error_context)
            error_context.pop_list_item(list, i)
            newList.append(result)
        return newList
    def process_something(self, obj, state, error_context):
        if isinstance(obj, str):
            return self.process_string(obj, state, error_context)
        if type(obj) is dict:
            return self.process_dict(obj, state, error_context)
        if type(obj) is list:
            return self.process_list(obj, state, error_context)
        if type(obj) is bool:
            return obj
        if obj == None:
            return obj
        sys.exit("process python type not implemented. type(obj) = {}".format(type(obj)))


    def get_hash_dict(self):
        return {'config':self.config,'in':self.in_list,'ops':self.get_hashdata_ops()}
    def make_pretty_hashdata(self):
        return json.dumps(self.get_hash_dict(), indent=4)
    # dump the data used for the hash of the genesis object
    def get_hashdata(self):
        if not self.hashdata:
            # need to sort keys so the same object always gets the same hash
            self.hashdata = json.dumps(self.get_hash_dict(), sort_keys=True)
        return self.hashdata
    def get_hash(self):
        if not self.hash:
            hasher = GenesisHasher()
            hasher.hash_file_content_string(self.get_hashdata())
            self.hash = hasher.finish()
        return self.hash
    def get_hash_name(self):
        if not self.hash_name:
            self.hash_name = make_hash_name(self.get_hash(), self.name)
        return self.hash_name

    def get_finalout_path(self):
        if not self.out_store_path:
            self.out_store_path = make_package_path(self.get_hash(), self.name)
        return self.out_store_path
    def get_obj_path(self):
        if not self.obj_path:
            self.obj_path = make_obj_path(self.get_hash(), self.name)
        return self.obj_path
    def get_obj_stage_path(self):
        if not self.obj_stage_path:
            self.obj_stage_path = make_obj_stage_path(self.get_hash(), self.name)
        return self.obj_stage_path
    def get_stage_path(self):
        if not self.stage_path:
            self.stage_path = make_stage_path(self.get_hash(), self.name)
        return self.stage_path
    def get_tmpout_path(self):
        if not self.tmpout_path:
            if self.notmpout:
                self.tmpout_path = self.get_finalout_path()
            else:
                self.tmpout_path = make_stage_path(self.get_hash(), self.name + ".tmpout")
        return self.tmpout_path

    def build_ins(self):
        for in_entry in self.in_list:
            gens_path = os.path.join(get_obj_path(), in_entry)
            if not os.path.exists(gens_path):
                sys.exit("Error: in '{}' is not in the store ({})".format(in_entry, gens_path))
            build(gens_path)
    def build(self):
        finalout = self.get_finalout_path()
        if os.path.exists(finalout):
            log.verbose("package '{}' is already built".format(self.name))
        else:
            self.build_ins()

            log.log("--------------------------------------------------------------------------------")
            log.log("BUILD   {}".format(finalout))
            # stage dir is where the files live during the build process
            stage_dir = self.get_stage_path()
            # tmpout dir is where the files are written to temporarily
            tmpout = self.get_tmpout_path()
            if os.path.exists(stage_dir):
                sys.exit("Error: stage directory '{}' already exists (TODO: handle this)".format(stage_dir))
            if os.path.exists(tmpout):
                sys.exit("Error: temporary output path '{}' already exists (TODO: handle this)".format(tmpout))
            log.verbose("mkdir '{}'".format(stage_dir))
            os.mkdir(stage_dir)

            save_cwd = os.getcwd()
            os.chdir(stage_dir)
            log.verbose("executing '{}' ops...".format(len(self.raw_ops)))
            executor = ops.OpExecutor()
            for op in self.raw_ops:
                if not type(op) is dict:
                    sys.exit("Error: in {}, got an op that is not an object but is {}".format(
                        self.name, type(op)))
                executor.execute(self, self.process_dict(op, ProcessState.BUILDING, ProcessErrorContext()))
            os.chdir(save_cwd)

            if not os.path.exists(tmpout):
                sys.exit("Error: operations did not generate anything in '@tmpout' ({})".format(tmpout))
            if self.ifaces:
                for iface in self.ifaces:
                    iface_path = os.path.join(tmpout, "genesis", "i", iface)
                    if not os.path.exists(iface_path):
                        raise Exception("genesis object '{}' implements interface '{}' but did not create file '{}'".format(
                            self.name, iface, iface_path))

            log.verbose("moving tmpout to final out")
            os.rename(tmpout, finalout)

            if not global_keep_stage:
                log.rmtree(stage_dir)
            log.log("--------------------------------------------------------------------------------")
        return finalout


'''
A genesis object may only be added if all it's dependencies are also added
'''
def add_gen_obj(name, search_paths):
    global_gen_filename = os.path.join(get_obj_path(), name)
    if os.path.exists(global_gen_filename):
        return
    for search_path in search_paths:
        filename = os.path.join(search_path, name)
        if os.path.exists(filename):
            add_gen_obj_from_file_not_already_added(GenesisObject.from_file(filename), filename, search_paths)
            return
    log.log("Error: failed to find genesis object '{}', searched in:".format(name))
    log.log("  - {}".format(get_obj_path()))
    for search_path in search_paths:
        log.log("  - {}".format(search_path))
    sys.exit(1)

# assumption: the genesis object is not added yet
def add_gen_obj_from_file_not_already_added(gen_obj, filename, search_paths):
    for in_entry in gen_obj.in_list:
        add_gen_obj(in_entry, search_paths)
    log.copyfile(filename, gen_obj.get_obj_path())
    return gen_obj.get_obj_path()

def add_gen_obj_from_file(filename):
    gen_obj = GenesisObject.from_file(filename)
    gens_path = gen_obj.get_obj_path()
    if os.path.exists(gens_path):
        log.verbose("genesis object '{}' is already added".format(gen_obj.name))
        return gens_path
    return add_gen_obj_from_file_not_already_added(gen_obj, filename, [os.path.dirname(filename)])

def write_gen_obj(gen_obj):
    # TODO: lock the stage path
    stage_file = gen_obj.get_obj_stage_path()
    if os.path.exists(stage_file):
        sys.exit("stage path for genesis object file '{}' already exists, not impl".format(stage_file))
    with open(stage_file, "wb") as file:
        file.write(gen_obj.get_hashdata().encode('ascii'))
    # verify the hash
    actual_hash = hash_file(stage_file)
    if actual_hash != gen_obj.get_hash():
        os.remove(stage_file)
        sys.exit("Error: code bug, hashes didn't match {} and {}".format(actual_hash, gen_obj.get_hash()))
    obj_path = gen_obj.get_obj_path()
    log.rename(stage_file, obj_path)
    return obj_path

def add_gen_obj_from_data(gen_obj):
    gens_path = gen_obj.get_obj_path()
    if os.path.exists(gens_path):
        log.verbose("genesis object '{}' is already added".format(gen_obj.name))
        return gens_path
    for in_entry in gen_obj.in_list:
        add_gen_obj(in_entry, [])
    return write_gen_obj(gen_obj)

def make_env(pkgs):
    in_list = []
    ops = []
    for pkg in pkgs:
        pkg = pkg.rstrip(os.path.sep)
        if not path_is_in_root(pkg):
            log.log("Error: make-env, genesis file '{}' is not in the store '{}'".format(pkg, get_root_path()))
            sys.exit(1)
        basename = os.path.basename(pkg)
        hash, name = split_hash_name(basename)
        in_list.append(basename)
        ops.append({'op':'addPackageLinks','path':'@in.'+name})
    gen_obj = GenesisObject.from_data("env", {'in':in_list, 'ops':ops})
    gen_path = add_gen_obj_from_data(gen_obj)
    return build(gen_path)
