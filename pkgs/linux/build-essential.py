deb_mirror = obj_set.get_alias("deb_mirror")
libc6 = obj_set.get_alias('libc6')
interp = '@'+libc6+'/lib/ld-2.27.so'

obj_set.add(name="libstdc++6-prebuilt-linux64", in_names=[], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gcc-8/libstdc++6_8-20180414-1ubuntu2_amd64.deb',
     'inHash':'sj255p54sv6tnjasg6ufy2j2qssrtzdk',
     'outHash':'3fyly6hx3beiqcsnvycemx4p6tpeflsd',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'move','src':'data/usr/lib/x86_64-linux-gnu','dst':'@tmpout/lib'},
    # NOTE: there is also a share directory, not sure what to do with it though
])
obj_set.add(name="clang-8.0.0-prebuilt-linux64", in_names=['libstdc++6-prebuilt-linux64'], ops=[
    {'op':'fetchArchive',
     'url':'http://releases.llvm.org/8.0.0/clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz',
     'inHash':'n4lrict6qoagmzv7kugdxd3usdkzksmp',
     'outHash':'zryar25fmj4guvxlqfqaven2d5izrwiv',
     'to':'@tmpout'},
    {'op':'unwrapDir','path':'@tmpout/clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04'},
    {'op':'depend','in':'@libstdc++6-prebuilt-linux64'},
])
obj_set.add(name="clang-env", in_names=[
    'libstdc++6-prebuilt-linux64',
    'clang-8.0.0-prebuilt-linux64'], ops=[
    {'op':'addPackageLinks','path':'@libstdc++6-prebuilt-linux64'},
    {'op':'addPackageLinks','path':'@clang-8.0.0-prebuilt-linux64'},
])

'''
# This seems to only contain empty directories and docs, not necessary
obj_set.add(name="gcc7base-prebuilt-linux64", in_names=[], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gcc-7/gcc-7-base_7.3.0-16ubuntu3_amd64.deb',
     'inHash':'ftrug3qpxijztqjqqeklsofjbf4p4uwz',
     'outHash':'b4xarij42sbygtjphwaqmowfr7iknl4k',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/lib','dst':'@tmpout'},
    #{'op':'fixElf','interp':None,'rpath':make_rpath(libc6),'files':[
    #    '@tmpout/lib/libz.so.1.2.11',
    #]},
])
'''


zlib1g = 'zlib1g-prebuilt-linux64'
obj_set.add(name=zlib1g, in_names=[libc6], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/z/zlib/zlib1g_1.2.11.dfsg-0ubuntu2_amd64.deb',
     'inHash':'x6scgfner2lu3t7lfwtcjvziibuflozr',
     'outHash':'5egnqjfc5eifgn76rwmbqq56azvquh3d',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(libc6),'files':[
        '@tmpout/lib/libz.so.1.2.11',
    ]},
    {'op':'depend','in':'@'+libc6},
])
libgmp10 = 'libgmp10-prebuilt-linux64'
obj_set.add(name=libgmp10, in_names=[libc6], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gmp/libgmp10_6.1.2+dfsg-2_amd64.deb',
     'inHash':'7tvlkfjgyzz6ru4memkzpvzsee75w3uw',
     'outHash':'4ave2ibk4ml7o67lwkqmumrbisfi7wrs',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/usr/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(libc6),'files':[
        '@tmpout/lib/libgmp.so.10.3.2',
    ]},
    {'op':'depend','in':'@'+libc6},
])
libisl19 = 'libisl19-prebuilt-linux64'
obj_set.add(name=libisl19, in_names=[libc6, libgmp10], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/i/isl/libisl19_0.19-1_amd64.deb',
     'inHash':'fejghirdu254qh3mqcxju36tpmbpajoc',
     'outHash':'7jqonp6g6s3hxyiceiwjuaiqut4nzmho',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/usr/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(libc6, libgmp10),'files':[
        '@tmpout/lib/libisl.so.19.0.0',
    ]},
    {'op':'depend','in':'@'+libc6},
    {'op':'depend','in':'@'+libgmp10},
])
libmpfr6 = 'libmpfr6-prebuilt-linux64'
obj_set.add(name=libmpfr6, in_names=[libc6, libgmp10], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/m/mpfr4/libmpfr6_4.0.1-1_amd64.deb',
     'inHash':'4wpcqgvqe5ug2tnpbwtpzbprgkoebjmy',
     'outHash':'2xr5jq3x7migkimx32kok2hqdyj6ut6h',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/usr/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(libc6, libgmp10),'files':[
        '@tmpout/lib/libmpfr.so.6.0.1',
    ]},
    {'op':'depend','in':'@'+libc6},
    {'op':'depend','in':'@'+libgmp10},
])
libmpc3 = 'libmpc3-prebuilt-linux64'
obj_set.add(name=libmpc3, in_names=[libc6, libgmp10, libmpfr6], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/m/mpclib3/libmpc3_1.1.0-1_amd64.deb',
     'inHash':'ggl5azl6ngl5xtaw5z7uv74u5ddz26ia',
     'outHash':'opz4tdti2ajfon3qwocj4a6m7ryclbph',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/usr/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(libc6, libgmp10, libmpfr6),'files':[
        '@tmpout/lib/libmpc.so.3.1.0',
    ]},
    {'op':'depend','in':'@'+libc6},
    {'op':'depend','in':'@'+libgmp10},
    {'op':'depend','in':'@'+libmpfr6},
])

cpp7 = 'cpp7-prebuilt-linux64'
obj_set.add(name=cpp7, in_names=[libc6, libgmp10, libisl19, libmpc3, libmpfr6, zlib1g], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gcc-7/cpp-7_7.3.0-16ubuntu3_amd64.deb',
     'inHash':'4m6ycx4dtzhvvgzgciwk6iafvguc57rv',
     'outHash':'to6ov5v3mjnm467j7eaqcmsxwtbrqvwf',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(libc6),'files':[
        '@tmpout/bin/x86_64-linux-gnu-cpp-7',
    ]},

    # cpp-7 looks for cc1 relative to it's own directory so we just put it there
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':interp,
     'rpath':make_rpath(libc6, libgmp10, libisl19, libmpc3, libmpfr6, zlib1g),'files':[
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/cc1',
    ]},
    {'op':'depend','in':'@'+libc6},
    {'op':'depend','in':'@'+libgmp10},
    {'op':'depend','in':'@'+libisl19},
    {'op':'depend','in':'@'+libmpc3},
    {'op':'depend','in':'@'+libmpfr6},
    {'op':'depend','in':'@'+zlib1g},
])


# other depends
# binutils-aarch64-linux-gnu
# binutils-arm-linux-gnueabihf
# binutils-i686-linux-gnu
# binutils-powerpc64le-linux-gnu
# binutils-s390x-linux-gnu

libbinutils = 'libbinutils-prebuilt-linux64'
obj_set.add(name=libbinutils, in_names=[libc6, zlib1g], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/b/binutils/libbinutils_2.30-20ubuntu2~18.04_amd64.deb',
     'inHash':'mzgm6j3gf5azlznl5r4oxcne5656un5x',
     'outHash':'d7kqklaebt7vbfsqot4amrzxb6s73sca',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/usr/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(libc6),'files':[
        '@tmpout/lib/libopcodes-2.30-system.so',
    ]},
    {'op':'fixElf','interp':None,'rpath':make_rpath(libc6, zlib1g),'files':[
        '@tmpout/lib/libbfd-2.30-system.so',
    ]},
    {'op':'depend','in':'@'+libc6},
    {'op':'depend','in':'@'+zlib1g},
])
binutils_linux64 = 'binutils-prebuilt-linux64'
obj_set.add(name=binutils_linux64, in_names=[libc6, zlib1g, libbinutils], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/b/binutils/binutils-x86-64-linux-gnu_2.30-20ubuntu2~18.04_amd64.deb',
     'inHash':'doiqfhkggtmgeblwkmjyoo7mw4buqwft',
     'outHash':'puwi5iyxyd46q52zosncm6aokwhyw6tv',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    # I think that the binutils binaries looks for these lib files relative to where they are stored
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(libc6),'files':[
        '@tmpout/bin/x86_64-linux-gnu-elfedit',
    ]},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(libc6, zlib1g),'files':[
        '@tmpout/bin/x86_64-linux-gnu-readelf',
    ]},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(libc6, libbinutils),'files':[
        '@tmpout/bin/x86_64-linux-gnu-addr2line',
        '@tmpout/bin/x86_64-linux-gnu-ar',
        '@tmpout/bin/x86_64-linux-gnu-c++filt',
        '@tmpout/bin/x86_64-linux-gnu-gprof',
        '@tmpout/bin/x86_64-linux-gnu-ld',
        '@tmpout/bin/x86_64-linux-gnu-ld.bfd',
        '@tmpout/bin/x86_64-linux-gnu-nm',
        '@tmpout/bin/x86_64-linux-gnu-objcopy',
        '@tmpout/bin/x86_64-linux-gnu-objdump',
        '@tmpout/bin/x86_64-linux-gnu-ranlib',
        '@tmpout/bin/x86_64-linux-gnu-size',
        '@tmpout/bin/x86_64-linux-gnu-strings',
        '@tmpout/bin/x86_64-linux-gnu-strip',
    ]},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(libc6, libbinutils, zlib1g),'files':[
        '@tmpout/bin/x86_64-linux-gnu-as',
        '@tmpout/bin/x86_64-linux-gnu-dwp',
        '@tmpout/bin/x86_64-linux-gnu-gold',
        '@tmpout/bin/x86_64-linux-gnu-ld.gold',
    ]},
    {'op':'depend','in':'@'+libc6},
    {'op':'depend','in':'@'+libbinutils},
])

gcc7_linux64 = 'gcc7-prebuilt-linux64'
obj_set.add(name=gcc7_linux64, in_names=[libc6, libgmp10, libisl19, libmpc3, libmpfr6, zlib1g, cpp7], ops=[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gcc-7/gcc-7_7.3.0-16ubuntu3_amd64.deb',
     'inHash':'muy2fd2y5agwv57sccmfar5xtcroa6ky',
     'outHash':'2zqzdgxuzccslnd2j274bp3qndhn5unl',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    # I think that gcc looks for these lib files relative to where the binaries are stored
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    # TODO: change symbolic link libcc1.so, it's target does exist
    {'op':'fixElf','interp':None,'rpath':make_rpath(libc6),'files':[
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/liblto_plugin.so.0.0.0',
    ]},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(libc6),'files':[
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/collect2',
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/lto-wrapper',
    ]},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(libc6, libgmp10, libisl19, libmpc3, libmpfr6, zlib1g),'files':[
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/lto1',
    ]},
    {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(libc6),'files':[
        '@tmpout/bin/x86_64-linux-gnu-gcc-7',
        '@tmpout/bin/x86_64-linux-gnu-gcc-ar-7',
        '@tmpout/bin/x86_64-linux-gnu-gcc-nm-7',
        '@tmpout/bin/x86_64-linux-gnu-gcc-ranlib-7',
        '@tmpout/bin/x86_64-linux-gnu-gcov-7',
        '@tmpout/bin/x86_64-linux-gnu-gcov-dump-7',
        '@tmpout/bin/x86_64-linux-gnu-gcov-tool-7',
    ]},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/cc1','to':'@'+cpp7+'/lib/gcc/x86_64-linux-gnu/7/cc1'},
    {'op':'depend','in':'@'+libc6},
    {'op':'depend','in':'@'+libgmp10},
    {'op':'depend','in':'@'+libisl19},
    {'op':'depend','in':'@'+libmpc3},
    {'op':'depend','in':'@'+libmpfr6},
    {'op':'depend','in':'@'+zlib1g},
    {'op':'depend','in':'@'+cpp7},
])
