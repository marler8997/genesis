import sys
import os
import tarfile
import zipfile

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log
import proc
import genesis

def un_tar_gzip(src, dst):
    with tarfile.open(src, "r:gz") as file:
        file.extractall(path=dst)
def un_tar_lzma(src, dst):
    # NOTE: the python lzma extractor is not working righ
    #with tarfile.open(src, "r:xz") as file:
    #    file.extractall(path=dst)
    tar = proc.get_program("tar", "extract .tar.xz files")
    log.mkdirs_if_needed(dst)
    proc.run([tar, "-xf", src, "-C", dst])
def un_gzip(src, dst):
    sys.exit("un_gzip not impl")
def un_tar(src, dst):
    sys.exit("un not impl")
def un_zip(src, dst):
    with zipfile.ZipFile(src, "r") as zip:
        zip.extractall(dst)
def un_7z(src, dst):
    _7z = proc.get_program("7z", "extract .7z files")
    log.mkdirs_if_needed(dst)
    proc.run([_7z, "x", src, "-o" + dst])
def un_deb(src, dst):
    ar = proc.get_program("ar", "extract .deb files")
    log.mkdirs_if_needed(dst)
    proc.run([ar, 'x', os.path.abspath(src)], cwd=dst)
    for entry_base in os.listdir(dst):
        entry = os.path.join(dst, entry_base)
        result = extract_if_needed(entry, os.path.dirname(entry), keep_basename=True)
        if result:
            log.rmfile(entry)

extract_ops = (
    (".tar.xz", un_tar_lzma),
    (".tar.gz", un_tar_gzip),
    (".gz", un_gzip),
    (".tar", un_tar),
    (".zip", un_zip),
    (".7z", un_7z),
    (".deb", un_deb),
)

def get_extract_func(filename):
    for ext,func in extract_ops:
        if filename.endswith(ext):
            return filename[:-(len(ext))], func
    return None, None
'''
class ExtractOp:
    def __init__(self, name, func):
        self.name = name
        self.func = func

def get_extract_ops(filename):
    extract_ops = []
    while True:
        next_filename, func = get_extract_func(filename)
        if not next_filename:
            return extract_ops
        extract_ops.append(ExtractOp(next_filename, func))
        filename = next_filename
'''
def get_extracted_path(path):
    while True:
        next_path, func = get_extract_func(path)
        if not next_path:
            return path
        path = next_path

# Options: remove transitionary forms?
def extract(path, dst_path, **kwargs):
    result = extract_if_needed(path, dst_path, **kwargs)
    if not result:
        sys.exit("don't know how to extract '{}'".format(path))
    return result

# Options: remove transitionary forms?
def extract_if_needed(path, dst_path, **kwargs):
    keep_basename = kwargs['keep_basename']
    original_path = path

    # get first extract func
    extract_path, func = get_extract_func(path)
    if not extract_path:
        return None # don't know how to extract

    # TODO: create lock file for extracting_dir
    extracting_dir = dst_path + ".extracting"
    if os.path.exists(extracting_dir):
        sys.exit("Error: cannot extract '{}' because '{}' already exists".format(
            path, extracting_dir))
    log.mkdirs(extracting_dir)
    while True:
        next_dst_path = os.path.join(extracting_dir, os.path.basename(extract_path))
        log.log("EXTRACT {}".format(path))
        func(path, next_dst_path)
        if not os.path.exists(next_dst_path):
            sys.exit("Error(code bug) extract function did not create '{}' from '{}'".format(
                next_dst_path, path))
        path = next_dst_path
        next_extract_path, func = get_extract_func(path)
        if not next_extract_path:
            break
        extract_path = next_extract_path

    if not keep_basename:
        log.unwrap_dir(next_dst_path)
    log.merge_move_dir(extracting_dir, dst_path)
    return extract_path
