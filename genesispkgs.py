include_file("pkgs/config.py")
include_file("pkgs/core.py")

include_file("pkgs/nix.py")

obj_set.add('hello',{'in':[],'ops':[
    {'op':'makeFile', 'path':'@tmpout/Hello.txt', 'content':'Hello Genesis!', 'makeDirs':True}
]})
obj_set.add('need-hello',{'in':['hello'],'ops':[
    {'op':'makeFile', 'path':'@tmpout/NeedHello.txt', 'content':'This package was built with "hello" as an in.', 'makeDirs':True}
]})

include_file("pkgs/python.py")
include_file("pkgs/genesis.py")
include_file("pkgs/musl-libc.py")
include_file("pkgs/glibc.py")
include_file("pkgs/gnumake.py")
include_file("pkgs/gcc.py")
include_file("pkgs/dmc.py")

include_file("pkgs/busybox.py")
include_file("pkgs/tcc.py")

if os.name == "nt":
    obj_set.add("clang-8.0.0-win64-prebuilt",{'in':[],'ops':[
        {'op':'fetchArchive',
         'url':'http://releases.llvm.org/8.0.0/LLVM-8.0.0-win64.exe',
         'hash':'',
         'to':'@stage'},
    ]})
else:
    include_file("pkgs/linux/coreutils.py")
    include_file("pkgs/linux/build-essential.py")

include_file("pkgs/lcc.py")
include_file("pkgs/dmd.py")
