def zig_template(*, name, version, platform, prebuilt):

    dummy = {
        'inHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'outHash':'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    }

    hashTable = {
        'freebsd-x86_64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            '0.6.0': dummy,
            '0.8.1': dummy,
        },
        'linux-aarch64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            '0.6.0': dummy,
            '0.8.1': dummy,
        },
        'linux-armv6kz':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            '0.6.0': dummy,
            '0.8.1': dummy,
        },
        'linux-armv7a':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            '0.6.0': dummy,
            '0.8.1': dummy,
        },
        'linux-i386':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            '0.6.0': dummy,
            '0.8.1': dummy,
        },
        'linux-riscv64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            '0.6.0': dummy,
            '0.8.1': dummy,
        },
        'linux-x86_64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            '0.6.0':{
                'inHash':'ax6czp2ojvipneukgwpm7iil2p4nbfok',
                'outHash':'oajtrtqor6fetasn7uc52jlon6yzoy55',
            },
            '0.8.1':{
                'inHash':'iqe7xn3gz2l64xbubvuzckg7phhhavfc',
                'outHash':'c4xh6al7ir5kebj6tjl4vq34uipftrs4',
            },
        },
        'macos-x86_64':{
            'archiveExt':'.tar.xz',
            'exeExt':'',
            '0.6.0': dummy,
            '0.8.1': dummy,
        },
        'windows-i386':{
            'archiveExt':'.zip',
            'exeExt':'.exe',
            '0.6.0': dummy,
            '0.8.1': dummy,
        },
        'windows-x86_64':{
            'archiveExt':'.zip',
            'exeExt':'.exe',
            '0.6.0':{
                'inHash':'jbaakrh3g5kc6hi7et46jwhnraupy46f',
                'outHash':'fqtteizbgdgrx6tm3u32l6y6nwwgvrl3',
            },
            '0.8.1':{
                'inHash':'gzdwxtsekxlvy4g6m65h3psfezjgiaom',
                'outHash':'bbuvbedin5737oyzliannguvgl3xo5xg',
            },
        },
    }
    platformData = hashTable[platform]
    exeExt = platformData['exeExt']
    platformVersionData = platformData[version]

    name = 'zig-' + platform + '-' + version
    return {'config':{'ifaces':['c-compiler','zig-compiler']},'in':[],'ops':[
        {'op':'fetchArchive',
         'url':'https://ziglang.org/download/' + version + '/' + name + platformData['archiveExt'],
         'inHash':platformVersionData['inHash'],
         'outHash':platformVersionData['outHash'],
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
    'version':['0.6.0', '0.8.1'],
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
