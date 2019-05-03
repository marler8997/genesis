import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log
import util
import genesis
import genobjset
import genesispkgslib

_core_pkg_set = None
def get_core_pkg_set():
    global _core_pkg_set
    if not _core_pkg_set:
        shared_globals = {
            'obj_set':genobjset.GenObjSet(),
            'config':genesispkgslib.Config(),
        }
        util.execfile(os.path.join(os.path.dirname(script_dir), "pkgs", "config.py"), shared_globals, {})
        util.execfile(os.path.join(os.path.dirname(script_dir), "pkgs", "core.py"), shared_globals, {})
        _core_pkg_set = shared_globals['obj_set']
        _core_pkg_set.add_all_to_global_genesis_obj_dir()
    return _core_pkg_set

_tar_bootstrap = None
def get_tar_bootstrap():
    global _tar_bootstrap
    if _tar_bootstrap == None:
        set = get_core_pkg_set()
        tar_pkg = genesis.build(set.get('tar-bootstrap').get_obj_path())
        _tar_bootstrap = os.path.join(tar_pkg,'bin','tar')
    return _tar_bootstrap

_patchelf_bootstrap = None
def get_patchelf_bootstrap():
    global _patchelf_bootstrap
    if _patchelf_bootstrap == None:
        set = get_core_pkg_set()
        patchelf_pkg = genesis.build(set.get('patchelf-bootstrap').get_obj_path())
        _patchelf_bootstrap = os.path.join(patchelf_pkg,'bin','patchelf')
    return _patchelf_bootstrap
