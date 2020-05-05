def zig_template(*, name, version, platform, prebuilt):

    hashTable = {
        'freebsd-x86_64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        },
        'linux-aarch64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        },
        'linux-armv6kz':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        },
        'linux-armv7a':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        },
        'linux-i386':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        },
        'linux-riscv64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        },
        'linux-x86_64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            'inHash':'ax6czp2ojvipneukgwpm7iil2p4nbfok',
            'outHash':'oajtrtqor6fetasn7uc52jlon6yzoy55',
        },
        'macos-x86_64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        },
        'windows-i386':{
            'archiveExt':'.zip',
            'exeExt':'.exe',
            'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        },
        'windows-x86_64':{
            'archiveExt':'.zip',
            'exeExt':'.exe',
            'inHash':'jbaakrh3g5kc6hi7et46jwhnraupy46f',
            'outHash':'fqtteizbgdgrx6tm3u32l6y6nwwgvrl3',
        },
    }
    platformData = hashTable[platform]
    exeExt = platformData['exeExt']

    name = 'zig-' + platform + '-' + version
    return {'config':{'ifaces':['c-compiler','zig-compiler']},'in':[],'ops':[
        {'op':'fetchArchive',
         'url':'https://ziglang.org/download/' + version + '/' + name + platformData['archiveExt'],
         'inHash':platformData['inHash'],
         'outHash':platformData['outHash'],
         'to':'@stage'},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'mkdirs','path':'@tmpout/genesis/i'},
        {'op':'moveToDir','src':'@stage/'+name+'/doc','dst':'@tmpout'},
        {'op':'mkdir','path':'@tmpout/bin'},
        {'op':'moveToDir','src':'@stage/'+name+'/zig'+exeExt,'dst':'@tmpout/bin'},
        {'op':'moveToDir','src':'@stage/'+name+'/lib','dst':'@tmpout/bin'},
        {'op':'exelink','path':'@tmpout/genesis/i/c-compiler'  ,'to':'../../bin/zig'+exeExt},
        {'op':'exelink','path':'@tmpout/genesis/i/zig-compiler','to':'../../bin/zig'+exeExt},
    ]}

obj_set.add_or_get_variation_set('zig', zig_template).add({
    #'version':['0.6.0','0.5.0'],
    'version':['0.6.0'],
    'platform':[
        'freebsd-x86_64',
        'linux-aarch64',
        'linux-armv6kz',
        'linux-armv7a',
        'linux-i386',
        'linux-riscv64',
        'linux-x86_64',
        'macos-x86_64',
        'windows-i386',
        'windows-x86_64',
    ],
    'prebuilt':[True],
})
