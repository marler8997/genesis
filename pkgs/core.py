#
# packages that are included by genesis directly to help
# build it's dependencies
#
# these objects shouldn't sepend on anython outside of this file
# because genesis directly includes it
#
gnu_mirror = config.get('gnu_mirror')

obj_set.add('tar-bootstrap', {'in':[],'ops':[
    # Don't use fetchArchive because it requires tar to be installed but genesis
    # doesn't have tar installed yet.  genesis uses this object to install tar so
    # it will fail because it try to build tar recursively. So instead we use fetchFile
    # and use the host tar tool to extract it.
    {'op':'fetchFile',
     'url':gnu_mirror + '/tar/tar-1.32.tar.bz2',
     'hash':'ajrv34idegpimg3ovmpka4obd2aluhcr',
     'toDir':'@stage'},
    {'op':'run','cmd':['tar','-xjf','@stage/tar-1.32.tar.bz2']},
    {'op':'unwrapDir','path':'@stage/tar-1.32'},
    {'op':'run','cmd':['./configure','--prefix=@tmpout']},
    {'op':'runMake','args':[]},
    {'op':'runMake','args':['install']},
]})

obj_set.add('patchelf-bootstrap', {'in':[],'ops':[
    {'op':'fetchArchive',
     'url':'https://github.com/NixOS/patchelf/archive/0.10.tar.gz',
     'inHash':'4asajumnh6noejmhngrwiy5ewurv77bz',
     'outHash':'zmxlxdjmjbpr6yznhhwqaza2wamfseg2',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/patchelf-0.10'},
    {'op':'run','cmd':['./bootstrap.sh']},
    {'op':'run','cmd':['./configure','--prefix=@tmpout']},
    {'op':'runMake','args':[]},
    {'op':'runMake','args':['install']},
]})
