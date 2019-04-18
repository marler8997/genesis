import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log
import genesis

deb_mirror = 'http://mirrors.kernel.org/ubuntu'
libc64 = genesis.GenesisObject.from_data('prebuilt-libc64', {'in':[], 'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/glibc/libc6_2.27-3ubuntu1_amd64.deb',
     'inHash':'xaanohc3qbsu62l5tuve4ogecz7oqwr5',
     'outHash':'czl3zqdayqw55ltk73xahu4mifk5o4r4',
     'to':'@stage'},
    {'op':'moveDirEntries','src':'@stage/data/lib/x86_64-linux-gnu','dst':'@tmpout/lib'},
]})
'''
chrpath64_broken = genesis.GenesisObject.from_data('prebuilt-chrpath64-broken', {'in':[libc64.get_hash_name()], 'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/universe/c/chrpath/chrpath_0.16-2_amd64.deb',
     'inHash':'xm5y7oihd56qzlkbir3hi7kyxsm5jqcy',
     'outHash':'gsonknulo2th3tka5pdzbphyki5xqux5',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
    {'op':'fixElf','interp':'@' + libc64.name + '/lib/ld-2.27.so','rpath':None,'files':[
        '@tmpout/bin/chrpath',
    ]},
]})
chrpath64 = genesis.GenesisObject.from_data('prebuilt-chrpath64', {'in':[
    libc64.get_hash_name(),
    chrpath64_broken.get_hash_name(),
], 'ops':[
    {'op':'mkdir','path':'@tmpout'},
    {'op':'copyToDir','src':'@' + chrpath64_broken.name + '/bin','dst':'@tmpout'},
    # Now we need to fix rpath of chrpath
    {'op':'run','env':{
        'LD_LIBRARY_PATH':'@' + libc64.name + '/lib',
    }, 'cmd':[
        '@'+chrpath64_broken.name+'/bin/chrpath',
        '-r', '@' + libc64.name + '/lib',
        '@tmpout/bin/chrpath'
    ]},
]})
'''

all = [libc64]

_add_checked = False
def build(obj_to_build):
    global _add_checked
    if not _add_checked:
        # add all the core pkg object files
        for obj in all:
            if not os.path.exists(obj.get_obj_path()):
                log.verbose("adding genesis object '{}'".format(obj.name))
                genesis.write_gen_obj(obj)
        _add_checked = True
    return genesis.build(obj_to_build.get_obj_path())
