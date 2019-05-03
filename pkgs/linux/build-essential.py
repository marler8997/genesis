deb_mirror = config.get("deb_mirror")
glibc6 = obj_set.resolve_name('glibc6')
glibc6_dev = obj_set.resolve_name('glibc6-dev')
interp = '@in.'+glibc6+'/lib/ld-2.27.so'

obj_set.add("libstdc++6-linux64-prebuilt",{'in':[],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gcc-8/libstdc++6_8-20180414-1ubuntu2_amd64.deb',
     'inHash':'sj255p54sv6tnjasg6ufy2j2qssrtzdk',
     'outHash':'r56bcap37w4pnaqeusugu7fl5phcloiu',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'move','src':'data/usr/lib/x86_64-linux-gnu','dst':'@tmpout/lib'},
    # NOTE: there is also a share directory, not sure what to do with it though
]})
obj_set.add("clang-8.0.0-linux64-prebuilt",{'in':['libstdc++6-linux64-prebuilt'],'ops':[
    {'op':'fetchArchive',
     'url':'http://releases.llvm.org/8.0.0/clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz',
     'inHash':'n4lrict6qoagmzv7kugdxd3usdkzksmp',
     'outHash':'zryar25fmj4guvxlqfqaven2d5izrwiv',
     'to':'@tmpout'},
    {'op':'unwrapDir','path':'@tmpout/clang+llvm-8.0.0-x86_64-linux-gnu-ubuntu-18.04'},
    {'op':'depend','in':'@in.libstdc++6-linux64-prebuilt'},
]})
obj_set.add("clang-env",{'in':[
    'libstdc++6-linux64-prebuilt',
    'clang-8.0.0-linux64-prebuilt'],'ops':[
    {'op':'addPackageLinks','path':'@in.libstdc++6-linux64-prebuilt'},
    {'op':'addPackageLinks','path':'@in.clang-8.0.0-linux64-prebuilt'},
]})


def binutils_template(*, name, version, platform, cross_platform, glibc6, zlib1g, libbinutils):
    deb_mirror = config.get("deb_mirror")
    debian_platform = kwselect(platform, linux64='amd64', linux32='i386')
    triple = kwselect(platform, linux64='x86_64-linux-gnu', linux32='i386-linux-gnu')
    interp = '@'+glibc6+'/lib/ld-2.27.so'
    return {'in':[glibc6, zlib1g, libbinutils],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/b/binutils/binutils-i686-linux-gnu_'+version+'-20ubuntu2~18.04_'+debian_platform+'.deb',
         'to':'@stage',
         **kwselect(debian_platform, amd64={
             'inHash':'ylhdh32roph7mfck4s47wrgkpaq7ntee',
             'outHash':'2jok2fd4xzhcm3juehlt6yatqw4cpaf2',
         },i386={
             'inHash':'',
             'outHash':'',
         })},
        {'op':'mkdir','path':'@tmpout'},
        # I think that the binutils binaries looks for these lib files relative to where they are stored
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
        {'op':'fixElf','interp':interp,'rpath':make_rpath2(glibc6),'files':[
            '@tmpout/bin/i686-linux-gnu-elfedit',
        ]},
        {'op':'fixElf','interp':interp,'rpath':make_rpath2(glibc6, zlib1g),'files':[
            '@tmpout/bin/i686-linux-gnu-readelf',
        ]},
        {'op':'fixElf','interp':interp,'rpath':make_rpath2(glibc6, libbinutils)+
         ':@finalout/lib/'+triple,'files':[
            '@tmpout/bin/i686-linux-gnu-addr2line',
            '@tmpout/bin/i686-linux-gnu-ar',
            '@tmpout/bin/i686-linux-gnu-c++filt',
            '@tmpout/bin/i686-linux-gnu-gprof',
            '@tmpout/bin/i686-linux-gnu-ld',
            '@tmpout/bin/i686-linux-gnu-ld.bfd',
            '@tmpout/bin/i686-linux-gnu-nm',
            '@tmpout/bin/i686-linux-gnu-objcopy',
            '@tmpout/bin/i686-linux-gnu-objdump',
            '@tmpout/bin/i686-linux-gnu-ranlib',
            '@tmpout/bin/i686-linux-gnu-size',
            '@tmpout/bin/i686-linux-gnu-strings',
            '@tmpout/bin/i686-linux-gnu-strip',
        ]},
        {'op':'fixElf','interp':interp,'rpath':make_rpath2(glibc6, libbinutils, zlib1g)+
         ':@finalout/lib/'+triple,'files':[
            '@tmpout/bin/i686-linux-gnu-as',
            '@tmpout/bin/i686-linux-gnu-dwp',
            '@tmpout/bin/i686-linux-gnu-ld.gold',
        ] + kwselect(debian_platform, amd64=[
            #'@tmpout/bin/i686-linux-gnu-gold',
        ],i386=[
        ])},
        {'op':'fixElf','interp':None,'rpath':make_rpath2(glibc6),'files':[
            '@tmpout/lib/x86_64-linux-gnu/libopcodes-'+version+'-i386.so',
        ]},
        {'op':'fixElf','interp':None,'rpath':make_rpath2(glibc6, zlib1g),'files':[
            '@tmpout/lib/x86_64-linux-gnu/libbfd-'+version+'-i386.so',
        ]},
        {'op':'depend','in':'@'+glibc6},
        {'op':'depend','in':'@'+libbinutils},
    ]}

def add_packages(deb_plat, glibc6, zlib1g, libgmp10, libisl19, libmpfr6,
                 libmpc3, cpp7, libbinutils, binutils_cross_linux64):
    deb_mirror = config.get("deb_mirror")

    def platform_select(**kwargs):
        value = kwargs.get(deb_plat)
        if value == None:
            raise Exception("undefined platform_select '{}'".format(deb_plat))
        return value

    genplat = platform_select(amd64='linux64', i386='linux32')
    triple = platform_select(amd64='x86_64-linux-gnu', i386='i386-linux-gnu')
    triple2 = platform_select(amd64='x86_64-linux-gnu', i386='i686-linux-gnu')
    interp = '@in.'+glibc6+'/lib/ld-2.27.so'

    obj_set.add(zlib1g,{'in':[glibc6],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/z/zlib/zlib1g_1.2.11.dfsg-0ubuntu2_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'x6scgfner2lu3t7lfwtcjvziibuflozr',
             'outHash':'5egnqjfc5eifgn76rwmbqq56azvquh3d',
         },i386={
             'inHash':'3guxe76zfoke6idoyhlto2a7r3mm4fhi',
             'outHash':'ardnejr2ecw4z6tgylgkjejpqzllfw6x',
         })},
        {'op':'unwrapDir','path':'@stage/data/lib/'+triple},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/lib','dst':'@tmpout'},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
            '@tmpout/lib/libz.so.1.2.11',
        ]},
        {'op':'depend','in':'@in.'+glibc6},
    ]})
    obj_set.add(libgmp10,{'in':[glibc6],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/g/gmp/libgmp10_6.1.2+dfsg-2_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'7tvlkfjgyzz6ru4memkzpvzsee75w3uw',
             'outHash':'4ave2ibk4ml7o67lwkqmumrbisfi7wrs',
         },i386={
             'inHash':'cwsoljdvszw7aykmkodmg7x2humfal6x',
             'outHash':'zagyv4vlaxzfwo6fbdj3piipboi43aq4',
         })},
        {'op':'unwrapDir','path':'@stage/data/usr/lib/'+triple},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
            '@tmpout/lib/libgmp.so.10.3.2',
        ]},
        {'op':'depend','in':'@in.'+glibc6},
    ]})
    obj_set.add(libisl19,{'in':[glibc6, libgmp10],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/i/isl/libisl19_0.19-1_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'fejghirdu254qh3mqcxju36tpmbpajoc',
             'outHash':'7jqonp6g6s3hxyiceiwjuaiqut4nzmho',
         },i386={
             'inHash':'nhsz7aqvgrrlnue6f7pup4n6sszpto5h',
             'outHash':'gbs7d7dtu4sw6bq2h573tn2es4mrtnfi',
         })},
        {'op':'unwrapDir','path':'@stage/data/usr/lib/'+triple},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6, libgmp10),'files':[
            '@tmpout/lib/libisl.so.19.0.0',
        ]},
        {'op':'depend','in':'@in.'+glibc6},
        {'op':'depend','in':'@in.'+libgmp10},
    ]})
    obj_set.add(libmpfr6,{'in':[glibc6, libgmp10],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/m/mpfr4/libmpfr6_4.0.1-1_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'4wpcqgvqe5ug2tnpbwtpzbprgkoebjmy',
             'outHash':'2xr5jq3x7migkimx32kok2hqdyj6ut6h',
         },i386={
             'inHash':'q5qgcopidxw6rozkbn7rnba3drcukymv',
             'outHash':'jqx3j2hf7rhi5mitnaxvzluirglmc3xm',
         })},
        {'op':'unwrapDir','path':'@stage/data/usr/lib/'+triple},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6, libgmp10),'files':[
            '@tmpout/lib/libmpfr.so.6.0.1',
        ]},
        {'op':'depend','in':'@in.'+glibc6},
        {'op':'depend','in':'@in.'+libgmp10},
    ]})
    obj_set.add(libmpc3,{'in':[glibc6, libgmp10, libmpfr6],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/m/mpclib3/libmpc3_1.1.0-1_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'ggl5azl6ngl5xtaw5z7uv74u5ddz26ia',
             'outHash':'opz4tdti2ajfon3qwocj4a6m7ryclbph',
         },i386={
             'inHash':'awqu3ak2sjzsuvope6352ebdybbigvnn',
             'outHash':'sqal7an3asfa672x7uceqxdzkloekj5h',
         })},
        {'op':'unwrapDir','path':'@stage/data/usr/lib/'+triple},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6, libgmp10, libmpfr6),'files':[
            '@tmpout/lib/libmpc.so.3.1.0',
        ]},
        {'op':'depend','in':'@in.'+glibc6},
        {'op':'depend','in':'@in.'+libgmp10},
        {'op':'depend','in':'@in.'+libmpfr6},
    ]})
    obj_set.add(cpp7,{'in':[glibc6, libgmp10, libisl19, libmpc3, libmpfr6, zlib1g],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/g/gcc-7/cpp-7_7.3.0-16ubuntu3_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'4m6ycx4dtzhvvgzgciwk6iafvguc57rv',
             'outHash':'to6ov5v3mjnm467j7eaqcmsxwtbrqvwf',
         },i386={
             'inHash':'5sikh3oz7whnmhem4qmorlko5yvui2cb',
             'outHash':'ogut5qi3j3e26xnkebr54mrubksccq3z',
         })},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6),'files':[
            '@tmpout/bin/'+triple2+'-cpp-7',
        ]},

        # cpp-7 looks for cc1 relative to it's own directory so we just put it there
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'fixElf','interp':interp,
         'rpath':make_rpath(glibc6, libgmp10, libisl19, libmpc3, libmpfr6, zlib1g),'files':[
             '@tmpout/lib/gcc/'+triple2+'/7/cc1',
         ]},
        {'op':'depend','in':'@in.'+glibc6},
        {'op':'depend','in':'@in.'+libgmp10},
        {'op':'depend','in':'@in.'+libisl19},
        {'op':'depend','in':'@in.'+libmpc3},
        {'op':'depend','in':'@in.'+libmpfr6},
        {'op':'depend','in':'@in.'+zlib1g},
    ]})
    obj_set.add(libbinutils,{'in':[glibc6, zlib1g],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/b/binutils/libbinutils_2.30-20ubuntu2~18.04_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'mzgm6j3gf5azlznl5r4oxcne5656un5x',
             'outHash':'d7kqklaebt7vbfsqot4amrzxb6s73sca',
         },i386={
             'inHash':'pm2eu3pmkqvdm2ftmr7m734uclw2zjbs',
             'outHash':'i7sgf3kp54wnb52ut4jkwdszyqvrzwzf',
         })},
        {'op':'unwrapDir','path':'@stage/data/usr/lib/'+triple},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
            '@tmpout/lib/libopcodes-2.30-system.so',
        ]},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6, zlib1g),'files':[
            '@tmpout/lib/libbfd-2.30-system.so',
        ]},
        {'op':'depend','in':'@in.'+glibc6},
        {'op':'depend','in':'@in.'+zlib1g},
    ]})
    # other depends
    # binutils-aarch64-linux-gnu
    # binutils-arm-linux-gnueabihf
    # binutils-i686-linux-gnu
    # binutils-powerpc64le-linux-gnu
    # binutils-s390x-linux-gnu
    obj_set.add(binutils_cross_linux64,{'in':[glibc6, zlib1g, libbinutils],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/b/binutils/binutils-x86-64-linux-gnu_2.30-20ubuntu2~18.04_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'doiqfhkggtmgeblwkmjyoo7mw4buqwft',
             'outHash':'puwi5iyxyd46q52zosncm6aokwhyw6tv',
         },i386={
             'inHash':'b3uroactfksj2fbrmj4o2hhv3rqx6eal',
             'outHash':'jaon2dj3tqrlj2szb3vagkp6hacqmybl',
         })},
        {'op':'mkdir','path':'@tmpout'},
        # I think that the binutils binaries looks for these lib files relative to where they are stored
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6),'files':[
            '@tmpout/bin/x86_64-linux-gnu-elfedit',
        ]},
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6, zlib1g),'files':[
            '@tmpout/bin/x86_64-linux-gnu-readelf',
        ]},
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6, libbinutils),'files':[
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
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6, libbinutils, zlib1g),'files':[
            '@tmpout/bin/x86_64-linux-gnu-as',
            '@tmpout/bin/x86_64-linux-gnu-dwp',
            '@tmpout/bin/x86_64-linux-gnu-ld.gold',
        ] + platform_select(amd64=[
            '@tmpout/bin/x86_64-linux-gnu-gold',
        ],i386=[
        ])},
        {'op':'depend','in':'@in.'+glibc6},
        {'op':'depend','in':'@in.'+libbinutils},
    ]})

    global binutils_template
    obj_set.add_or_get_variation_set('binutils-cross-linux32', binutils_template).add({
        'version':['2.30'],
        'platform':[genplat],
        'cross_platform':['linux32'],
        'glibc6':[obj_set.alias_to_hash_name(glibc6)],
        'zlib1g':[obj_set.alias_to_hash_name(zlib1g)],
        'libbinutils':[obj_set.alias_to_hash_name(libbinutils)],
    })

    '''
    binutils_cross_linux32 = 'binutils-cross-linux32-' + genplat + '-prebuilt'
    obj_set.add(binutils_cross_linux32,{'in':[glibc6, zlib1g, libbinutils],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/b/binutils/binutils-i686-linux-gnu_2.30-20ubuntu2~18.04_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'ylhdh32roph7mfck4s47wrgkpaq7ntee',
             'outHash':'2jok2fd4xzhcm3juehlt6yatqw4cpaf2',
         },i386={
             'inHash':'',
             'outHash':'',
         })},
        {'op':'mkdir','path':'@tmpout'},
        # I think that the binutils binaries looks for these lib files relative to where they are stored
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
        {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6),'files':[
            '@tmpout/bin/i686-linux-gnu-elfedit',
        ]},
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6, zlib1g),'files':[
            '@tmpout/bin/i686-linux-gnu-readelf',
        ]},
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6, libbinutils)+
         ':@finalout/lib/'+triple,'files':[
            '@tmpout/bin/i686-linux-gnu-addr2line',
            '@tmpout/bin/i686-linux-gnu-ar',
            '@tmpout/bin/i686-linux-gnu-c++filt',
            '@tmpout/bin/i686-linux-gnu-gprof',
            '@tmpout/bin/i686-linux-gnu-ld',
            '@tmpout/bin/i686-linux-gnu-ld.bfd',
            '@tmpout/bin/i686-linux-gnu-nm',
            '@tmpout/bin/i686-linux-gnu-objcopy',
            '@tmpout/bin/i686-linux-gnu-objdump',
            '@tmpout/bin/i686-linux-gnu-ranlib',
            '@tmpout/bin/i686-linux-gnu-size',
            '@tmpout/bin/i686-linux-gnu-strings',
            '@tmpout/bin/i686-linux-gnu-strip',
        ]},
        {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6, libbinutils, zlib1g)+
         ':@finalout/lib/'+triple,'files':[
            '@tmpout/bin/i686-linux-gnu-as',
            '@tmpout/bin/i686-linux-gnu-dwp',
            '@tmpout/bin/i686-linux-gnu-ld.gold',
        ] + platform_select(amd64=[
            #'@tmpout/bin/i686-linux-gnu-gold',
        ],i386=[
        ])},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
            '@tmpout/lib/x86_64-linux-gnu/libopcodes-2.30-i386.so',
        ]},
        {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6, zlib1g),'files':[
            '@tmpout/lib/x86_64-linux-gnu/libbfd-2.30-i386.so',
        ]},
        {'op':'depend','in':'@in.'+glibc6},
        {'op':'depend','in':'@in.'+libbinutils},
    ]})
    '''

zlib1g = 'zlib1g-linux64-prebuilt'
libgmp10 = 'libgmp10-linux64-prebuilt'
libisl19 = 'libisl19-linux64-prebuilt'
libmpfr6 = 'libmpfr6-linux64-prebuilt'
libmpc3 = 'libmpc3-linux64-prebuilt'
cpp7 = 'cpp7-linux64-prebuilt'
libbinutils = 'libbinutils-linux64-prebuilt'
binutils_linux64 = 'binutils-cross-linux64-linux64-prebuilt'
add_packages('amd64', glibc6, zlib1g, libgmp10, libisl19, libmpfr6,
             libmpc3, cpp7, libbinutils, binutils_linux64)
add_packages('i386',
             obj_set.resolve_name('glibc6-linux32-prebuilt'),
             'zlib1g-linux32-prebuilt',
             'libgmp10-linux32-prebuilt',
             'libisl19-linux32-prebuilt',
             'libmpfr6-linux32-prebuilt',
             'libmpc3-linux32-prebuilt',
             'cpp7-linux32-prebuilt',
             'libbinutils-linux32-prebuilt',
             'binutils-cross-linux64-linux32-prebuilt')

libgcc7_dev = 'libgcc7-dev-linux64-prebuilt'
obj_set.add(libgcc7_dev,{'in':[],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gcc-7/libgcc-7-dev_7.3.0-16ubuntu3_amd64.deb',
     'inHash':'yfw52mhef2qs3othhpylpxju7ucqq6jo',
     'outHash':'7ge24zbex4unjqhz5adhb3c5pu5ythpj',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    # TODO: fix symlinks?
]})
libgcc1 = 'libgcc1-linux64-prebuilt'
obj_set.add(libgcc1,{'in':[glibc6],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gcc-8/libgcc1_8-20180414-1ubuntu2_amd64.deb',
     'inHash':'4oxlxurm7fpvx3dayt2thsn3mqyd3ql3',
     'outHash':'cqwtmux5m6ellvlhmr6y24wk5yo75vuy',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'unwrapDir','path':'@stage/data/lib/x86_64-linux-gnu'},
    {'op':'moveToDir','src':'@stage/data/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
        '@tmpout/lib/libgcc_s.so.1',
    ]},
]})

# NOTE: the gcc binaries don't actually depend on glibc6-dev to run, however, I'm not sure how to
#       get gcc to find the glibc6-dev header files without adding an 'include' symlink into gcc.
gcc7_linux64 = 'gcc7-linux64-prebuilt'
obj_set.add(gcc7_linux64,{'in':[
    glibc6, libgmp10, libisl19, libmpc3, libmpfr6,
    zlib1g, cpp7, glibc6_dev, libgcc1, libgcc7_dev,
    binutils_linux64],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/g/gcc-7/gcc-7_7.3.0-16ubuntu3_amd64.deb',
     'inHash':'muy2fd2y5agwv57sccmfar5xtcroa6ky',
     'outHash':'2zqzdgxuzccslnd2j274bp3qndhn5unl',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    # I think that gcc looks for these lib files relative to where the binaries are stored
    {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    # TODO: change symbolic link libcc1.so, it's target does exist
    {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/liblto_plugin.so.0.0.0',
    ]},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6),'files':[
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/collect2',
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/lto-wrapper',
    ]},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6, libgmp10, libisl19, libmpc3, libmpfr6, zlib1g),'files':[
        '@tmpout/lib/gcc/x86_64-linux-gnu/7/lto1',
    ]},
    {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
    {'op':'fixElf','interp':interp,'rpath':make_rpath(glibc6),'files':[
        '@tmpout/bin/x86_64-linux-gnu-gcc-7',
        '@tmpout/bin/x86_64-linux-gnu-gcc-ar-7',
        '@tmpout/bin/x86_64-linux-gnu-gcc-nm-7',
        '@tmpout/bin/x86_64-linux-gnu-gcc-ranlib-7',
        '@tmpout/bin/x86_64-linux-gnu-gcov-7',
        '@tmpout/bin/x86_64-linux-gnu-gcov-dump-7',
        '@tmpout/bin/x86_64-linux-gnu-gcov-tool-7',
    ]},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/cc1','to':'@in.'+cpp7+'/lib/gcc/x86_64-linux-gnu/7/cc1'},
    {'op':'depend','in':'@in.'+glibc6},
    {'op':'depend','in':'@in.'+libgmp10},
    {'op':'depend','in':'@in.'+libisl19},
    {'op':'depend','in':'@in.'+libmpc3},
    {'op':'depend','in':'@in.'+libmpfr6},
    {'op':'depend','in':'@in.'+zlib1g},
    {'op':'depend','in':'@in.'+cpp7},
    #
    # Not sure how to get gcc to find glibc6-dev without this
    #
    # I only found that the gcc preprocess compiled by ubuntu searches 3 paths relative
    # to the binary.
    #   ../lib/gcc/x86_64-linux-gnu/7/include
    #   ../lib/gcc/x86_64-linux-gnu/7/include-fixed
    #   ../x86_64-linux-gnu/include
    # So I've linked to the libgcc-7-dev headers in the first 2 and the last one just contains
    # a copy of all the other system headers I need (i.e. the ones from glibc6-dev)
    #
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/include',
     'to':'@in.'+libgcc7_dev+'/lib/gcc/x86_64-linux-gnu/7/include'},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/include-fixed',
     'to':'@in.'+libgcc7_dev+'/lib/gcc/x86_64-linux-gnu/7/include-fixed'},
    {'op':'mkdirs','path':'@tmpout/x86_64-linux-gnu/include'},
    {'op':'linkDirEntries','src':'@in.'+glibc6_dev+'/include','dst':'@tmpout/x86_64-linux-gnu/include'},
    {'op':'linkDirEntries','src':'@in.'+glibc6_dev+'/include/x86_64-linux-gnu','dst':'@tmpout/x86_64-linux-gnu/include'},
    {'op':'depend','in':'@in.'+glibc6_dev},
    {'op':'depend','in':'@in.'+libgcc7_dev},
    #
    # Add symlinks so gcc can find binutils
    #
    #{'op':'mkdirs','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7'},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/as',
     'to':'@in.'+binutils_linux64+'/bin/x86_64-linux-gnu-as'},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/ld',
     'to':'@in.'+binutils_linux64+'/bin/x86_64-linux-gnu-ld.bfd'},
    {'op':'depend','in':'@in.'+binutils_linux64},
    #
    # Add symlinks so gcc can find linker libraries
    #
    {'op':'linkDirEntries','src':'@in.'+glibc6_dev+'/lib/x86_64-linux-gnu','dst':'@tmpout/lib/gcc/x86_64-linux-gnu/7'},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/libgcc_s.so.1',
     'to':'@in.'+libgcc1+'/lib/libgcc_s.so.1'},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/crtbeginS.o',
     'to':'@in.'+libgcc7_dev+'/lib/gcc/x86_64-linux-gnu/7/crtbeginS.o'},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/libgcc_s.so',
     'to':'@in.'+libgcc7_dev+'/lib/gcc/x86_64-linux-gnu/7/libgcc_s.so'},
    {'op':'symlink','path':'@tmpout/lib/gcc/x86_64-linux-gnu/7/libgcc.a',
     'to':'@in.'+libgcc7_dev+'/lib/gcc/x86_64-linux-gnu/7/libgcc.a'},
    #{'op':'linkDirEntries','src':'@in.'+libgcc7_dev+'/lib/gcc/x86_64-linux-gnu/7','dst':'@tmpout/lib/gcc/x86_64-linux-gnu/7'},
    ]})
