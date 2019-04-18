if os.name == "nt":
    obj_set.set_alias("dmd", "dmd-2.085.1-prebuilt-win")
    obj_set.add(name="dmd-2.085.1-prebuilt-win", in_names=[], ops=[
        {'op':'fetchArchive',
         'url':'http://downloads.dlang.org/releases/2.x/2.085.1/dmd.2.085.1.windows.7z',
         'inHash':'tqooghmxccn7rthlzlo4k6rhmudkudko',
         'outHash':'yumcixtbdbk3xjceghbabtzgqxhofkwt',
         'to':'@stage'},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/dmd2','dst':'@tmpout'},
        {'op':'makeFile','path':'@tmpout/genesis/extra-bin','content':
            'dmd2/windows/bin/dmd.exe\n' +
            'dmd2/windows/bin/ddemangle.exe\n' +
            'dmd2/windows/bin/dub.exe\n' +
            'dmd2/windows/bin/dustmite.exe\n' +
            'dmd2/windows/bin/lib.exe\n' +
            'dmd2/windows/bin/link.exe\n' +
            'dmd2/windows/bin/lld-link.exe\n' +
            # put make in another package
            #'dmd2/windows/bin/lld-link.exe\n' +
            'dmd2/windows/bin/optlink.exe\n' +
            'dmd2/windows/bin/rdmd.exe\n' +
            '','makeDirs':True},
    ])
    dmc = obj_set.get_alias('dmc')
    obj_set.add(name="dmd-2.085.1-win", in_names=[dmc], ops=[
        {'op':'fetchArchive',
         'url':'https://github.com/dlang/dmd/archive/v2.085.1.tar.gz',
         'inHash':'pj34z4ikit5rtwrzghj4dm2tpwgcc7df',
         'outHash':'ddqmstcot53krfmzqax2c2wd6gjopa5g',
         'to':'@stage'},
        # TODO: rename dmd-2.085.1 to dmd
        #{'op':'mkdir','path':'@tmpout'},
        #{'op':'moveToDir','src':'@stage/dm/bin','dst':'@tmpout'},
        #{'op':'moveToDir','src':'@stage/dm/lib','dst':'@tmpout'},
        #{'op':'moveToDir','src':'@stage/dm/include','dst':'@tmpout'},
    ])
else:
    def add_prebuilt_dmd(name, platform, url, in_hash, out_hash):
        obj_set.add(name=name, in_names=[], ops=[
            {'op':'fetchArchive',
             'url':url,
             'inHash':in_hash,
             'outHash':out_hash,
             'to':'@stage'},
            {'op':'mkdir','path':'@tmpout'},
            {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
            {'op':'move','src':'@stage/data/usr/lib/' + platform,'dst':'@tmpout/lib'},
        ])
    add_prebuilt_dmd(
        'dmd-2.085.1-prebuilt-linux32',
        'i386-linux-gnu',
        'http://downloads.dlang.org/releases/2019/dmd_2.085.1-0_i386.deb',
        'vk664n75onp26msifvh4bf446gdytul7',
        '')
    add_prebuilt_dmd(
        'dmd-2.085.1-prebuilt-linux64',
        'x86_64-linux-gnu',
        'http://downloads.dlang.org/releases/2019/dmd_2.085.1-0_amd64.deb',
        'lmbhnzf2ffui7aqohsgpxtoak7cwxmyz',
        '2ru3mhddoind7mwqldwtb5z32nptghye')
    obj_set.set_alias('dmd', 'dmd-2.085.1-prebuilt-linux64')

dmd = obj_set.get_alias('dmd')
obj_set.add(name="dmd-env", in_names=[dmd], ops=[
    {'op':'addPackageLinks','path':'@'+dmd},
])
