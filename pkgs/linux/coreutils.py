
deb_mirror = config.get('deb_mirror')
glibcver = '2.27'
glibc6 = 'glibc6-'+glibcver+'-linux64-prebuilt'

#
# Level 1: dependent on glibc
#
libpcre3 = 'libpcre3-8.39-linux64-prebuilt'
obj_set.add(libpcre3,{'in':[glibc6],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/p/pcre3/libpcre3_8.39-9_amd64.deb',
     'inHash':'poyficabvuqemqecy7wnhxuyum2apkwt',
     'outHash':'m5bjsmvcsll4hgdnrxizdvd22ouxmkc7',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/lib','dst':'@tmpout'},
    {'op':'copyDirEntries','src':'@stage/data/usr/lib/x86_64-linux-gnu','dst':'@tmpout/lib'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
        '@tmpout/lib/libpcre.so.3.13.3',
        '@tmpout/lib/libpcreposix.so.3.13.3',
    ]},
]})

libattr1 = 'libattr1-2.4.47-linux64-prebuilt'
obj_set.add(libattr1,{'in':[glibc6],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/a/attr/libattr1_2.4.47-2build1_amd64.deb',
     'inHash':'2c7u6fkbuqbbhseistsd23dmsyiibsin',
     'outHash':'hjuuksxwgvcwf7hmuxslwctqlel7npzr',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
        '@tmpout/lib/libattr.so.1',
    ]},
]})

#
# Level 2: dependent on level 1 packages
#
libselinux1 = 'libselinux1-2.7-linux64-prebuilt'
obj_set.add(libselinux1,{'in':[glibc6,libpcre3],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/libs/libselinux/libselinux1_2.7-2build2_amd64.deb',
     'inHash':'6fhcleyzhua6b2hjdm7ublq5mbdglmtr',
     'outHash':'nlk3ubppbwg3moodf7ktjokph335sqan',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6,libpcre3),'files':[
        '@tmpout/lib/libselinux.so.1',
    ]},
    {'op':'depend','in':'@in.'+libpcre3},
]})

libacl1 = 'libacl1-2.7-linux64-prebuilt'
obj_set.add(libacl1,{'in':[glibc6,libattr1],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/a/acl/libacl1_2.2.52-3build1_amd64.deb',
     'inHash':'fh4whjumhsvdf6iq2zqfoniuahjorbcg',
     'outHash':'le4yxadyss3fcjcktg5bg6pq3edhva5g',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/data/lib/x86_64-linux-gnu'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/lib','dst':'@tmpout'},
    {'op':'fixElf','interp':None,'rpath':make_rpath(glibc6,libattr1),'files':[
        '@tmpout/lib/libacl.so.1.1.0',
    ]},
    {'op':'depend','in':'@in.'+libattr1},
]})

#
# Level 3: dependent on level 2 packages
#
coreutils_prebuilt = 'coreutils-8.28-linux64-prebuilt'
config.set('coreutils_prebuilt', coreutils_prebuilt)
config.set('coreutils', coreutils_prebuilt)
obj_set.add(coreutils_prebuilt,{'in':[glibc6,libselinux1,libattr1,libacl1],'ops':[
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/c/coreutils/coreutils_8.28-1ubuntu1_amd64.deb',
     'inHash':'qkoxpkugzn26iinntfqkg5oauf42wyhk',
     'outHash':'rfravlcrpy5ih23ju775v55vk746hlwq',
     'to':'@stage'},
    {'op':'fetchArchive',
     'url':deb_mirror + '/pool/main/d/debianutils/debianutils_4.8.6_amd64.deb',
     'inHash':'4bdx2j4vj7arzwmbzoh5rc4xtc7rng6g',
     'outHash':'k6gc52rz36wsfr7rwp5flzsk7cvuu5fx',
     'to':'@stage/debianutils'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'moveToDir','src':'@stage/data/bin','dst':'@tmpout'},
    # NOTE: 'which' is a small shell script, dependent on /bin/sh
    #       maybe this should be in another package?
    {'op':'moveToDir','src':'@stage/debianutils/data/bin/which','dst':'@tmpout/bin'},
    # TODO: there's more programs in usr/bin and usr/sbin
    {'op':'fixElf','interp':'@in.'+glibc6+'/lib/ld-'+glibcver+'.so','rpath':make_rpath(glibc6),'files':[
        '@tmpout/bin/cat',
        '@tmpout/bin/chgrp',
        '@tmpout/bin/chmod',
        '@tmpout/bin/chown',
        '@tmpout/bin/date',
        '@tmpout/bin/dd',
        '@tmpout/bin/df',
        '@tmpout/bin/dir',
        '@tmpout/bin/echo',
        '@tmpout/bin/false',
        '@tmpout/bin/ln',
        '@tmpout/bin/mktemp',
        '@tmpout/bin/pwd',
        '@tmpout/bin/readlink',
        '@tmpout/bin/rm',
        '@tmpout/bin/rmdir',
        '@tmpout/bin/sleep',
        '@tmpout/bin/stty',
        '@tmpout/bin/sync',
        '@tmpout/bin/touch',
        '@tmpout/bin/true',
        '@tmpout/bin/uname',
        '@tmpout/bin/vdir',
    ]},
    {'op':'fixElf','interp':'@in.'+glibc6+'/lib/ld-'+glibcver+'.so','rpath':make_rpath(glibc6,libselinux1),'files':[
        '@tmpout/bin/ls',
        '@tmpout/bin/mkdir',
        '@tmpout/bin/mknod',
    ]},
    {'op':'fixElf','interp':'@in.'+glibc6+'/lib/ld-'+glibcver+'.so','rpath':make_rpath(glibc6,libselinux1,libattr1,libacl1),'files':[
        '@tmpout/bin/cp',
        '@tmpout/bin/mv',
    ]},
    {'op':'depend','in':'@in.'+glibc6},
    {'op':'depend','in':'@in.'+libselinux1},
    {'op':'depend','in':'@in.'+libattr1},
    {'op':'depend','in':'@in.'+libacl1},
]})
