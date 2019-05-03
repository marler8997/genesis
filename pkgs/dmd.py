
dmdver = '2.085.1'

fetch_dmd = {'op':'fetchArchive',
 'url':'https://github.com/dlang/dmd/archive/v'+dmdver+'.zip',
 'inHash':'ptrup2rjbklxqs6ik2qyiwblqbi3jvht',
 'outHash':'ddqmstcot53krfmzqax2c2wd6gjopa5g',
 'to':'@stage'}
fetch_druntime = {'op':'fetchArchive',
 'url':'https://github.com/dlang/druntime/archive/v'+dmdver+'.zip',
 'inHash':'m7jiedhuiqsg3pq7wjpaujzqi5txclws',
 'outHash':'qtlm42ic6kb2xyjzwueqwxsto5pmeqvt',
 'to':'@stage'}
fetch_phobos = {'op':'fetchArchive',
 'url':'https://github.com/dlang/phobos/archive/v'+dmdver+'.zip',
 'inHash':'vnon3umfrqvneknewxkgeydweynfpacm',
 'outHash':'zfcmwqn33o6hy4mugygexbtudaimdagy',
 'to':'@stage'}

if os.name == "nt":
    dmd_prebuilt = 'dmd-'+dmdver+'-win-prebuilt'
    config.set("dmd_prebuilt", dmd_prebuilt)
    dmd_prebuilt_fetch_op = {
        'op':'fetchArchive',
        'url':'http://downloads.dlang.org/releases/2.x/'+dmdver+'/dmd.'+dmdver+'.windows.7z',
        'inHash':'tqooghmxccn7rthlzlo4k6rhmudkudko',
        'outHash':'yumcixtbdbk3xjceghbabtzgqxhofkwt',
        'to':'@stage'}
    obj_set.add(dmd_prebuilt,{'in':[],'ops':[
        dmd_prebuilt_fetch_op,
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/dmd2','dst':'@tmpout'},
        {'op':'unwrapDir','path':'@tmpout/dmd2'},
        {'op':'makeFile','path':'@tmpout/genesis/extra-bin','content':
            'windows/bin/dmd.exe\n' +
            'windows/bin/ddemangle.exe\n' +
            'windows/bin/dub.exe\n' +
            'windows/bin/dustmite.exe\n' +
            'windows/bin/lib.exe\n' +
            'windows/bin/link.exe\n' +
            'windows/bin/lld-link.exe\n' +
            # put make in another package
            #'windows/bin/lld-link.exe\n' +
            'windows/bin/optlink.exe\n' +
            'windows/bin/rdmd.exe\n' +
            '','makeDirs':True},
    ]})

    dmc = obj_set.resolve_name('dmc')
    dmd = 'dmd-'+dmdver+'-win'
    obj_set.setalias('dmd',dmd)
    obj_set.add(dmd,{'in':[dmc,dmd_prebuilt],'ops':[
        fetch_dmd, fetch_druntime, fetch_phobos,
        {'op':'mkdirs','path':'@stage/dmd2/src'},
        {'op':'move','src':'@stage/dmd-'+dmdver,'dst':'@stage/dmd2/src/dmd'},
        {'op':'move','src':'@stage/druntime-'+dmdver,'dst':'@stage/dmd2/src/druntime'},
        {'op':'move','src':'@stage/phobos-'+dmdver,'dst':'@stage/dmd2/src/phobos'},
        {'op':'setEnv','name':'DM_HOME','value':'@stage'},
        {'op':'setEnv','name':'HOST_DC','value':'dmd'},
        {'op':'cd','path':'@stage/dmd2/src/dmd/src'},
        {'op':'prependPathEnv','path':'@in.'+dmd_prebuilt+'/windows/bin'},
        {'op':'prependPathEnv','path':'@in.'+dmc+'/bin'},
        {'op':'run','cmd':['make','-fwin32.mak','release']},
        {'op':'mkdirs','path':'@tmpout/windows/bin'},
        {'op':'copyToDir','src':'@stage/dmd2/src/dmd/src/dmd.exe','dst':'@tmpout/windows/bin'},
        {'op':'copyToDir','src':'@in.'+dmd_prebuilt+'/windows/bin/sc.ini','dst':'@tmpout/windows/bin'},
    ]})
else:
    def add_prebuilt_dmd(name, platform, url, in_hash, out_hash):
        glibcver = '2.27'
        glibc6 = 'glibc6-'+glibcver+'-linux64-prebuilt'
        libgcc1 = 'libgcc1-linux64-prebuilt'
        obj_set.add(name,{'in':[glibc6,libgcc1],'ops':[
            {'op':'fetchArchive',
             'url':url,
             'inHash':in_hash,
             'outHash':out_hash,
             'to':'@stage'},
            {'op':'mkdir','path':'@tmpout'},
            {'op':'moveToDir','src':'@stage/data/usr/bin','dst':'@tmpout'},
            {'op':'move','src':'@stage/data/usr/lib/' + platform,'dst':'@tmpout/lib'},
            {'op':'fixElf','interp':'@in.'+glibc6+'/lib/ld-'+glibcver+'.so','rpath':make_rpath(glibc6,libgcc1),'files':[
                '@tmpout/bin/ddemangle',
                '@tmpout/bin/dmd',
                '@tmpout/bin/dub',
                '@tmpout/bin/dumpobj',
                '@tmpout/bin/dustmite',
                '@tmpout/bin/obj2asm',
                '@tmpout/bin/rdmd',
            ]},
        ]})
    add_prebuilt_dmd(
        'dmd-'+dmdver+'-linux32-prebuilt',
        'i386-linux-gnu',
        'http://downloads.dlang.org/releases/2019/dmd_'+dmdver+'-0_i386.deb',
        'vk664n75onp26msifvh4bf446gdytul7',
        '')
    dmd_prebuilt_basename = 'dmd-'+dmdver+'-linux64-prebuilt'
    config.set('dmd_prebuilt', dmd_prebuilt_basename)
    obj_set.setalias('dcompiler', dmd_prebuilt_basename)
    add_prebuilt_dmd(
        dmd_prebuilt_basename,
        'x86_64-linux-gnu',
        'http://downloads.dlang.org/releases/2019/dmd_'+dmdver+'-0_amd64.deb',
        'lmbhnzf2ffui7aqohsgpxtoak7cwxmyz',
        '2ru3mhddoind7mwqldwtb5z32nptghye')

    coreutils = obj_set.resolve_name(config.get('coreutils'))
    gnumake = obj_set.get_variation('gnumake')
    dmd_prebuilt = obj_set.resolve_name(dmd_prebuilt_basename)
    dmd = 'dmd-'+dmdver+'-linux'
    config.set('dmd', dmd)
    obj_set.add_no_resolve(dmd,{'in':[gnumake, coreutils, dmd_prebuilt],'ops':[
        fetch_dmd, fetch_druntime, fetch_phobos,
        {'op':'mkdirs','path':'@stage/dmd2/src'},
        {'op':'move','src':'@stage/dmd-'+dmdver,'dst':'@stage/dmd2/src/dmd'},
        {'op':'move','src':'@stage/druntime-'+dmdver,'dst':'@stage/dmd2/src/druntime'},
        {'op':'move','src':'@stage/phobos-'+dmdver,'dst':'@stage/dmd2/src/phobos'},
        {'op':'setEnv','name':'DM_HOME','value':'@stage'},
        {'op':'setEnv','name':'HOST_DC','value':'dmd'},
        {'op':'cd','path':'@stage/dmd2/src/dmd/src'},
        {'op':'prependPathEnv','path':'@'+coreutils+'/bin'},
        {'op':'prependPathEnv','path':'@'+gnumake+'/bin'},
        {'op':'prependPathEnv','path':'@'+dmd_prebuilt+'/windows/bin'},
        #{'op':'prependPathEnv','path':'@'+dmc+'/bin'},
        {'op':'run','cmd':['make','-fposix.mak','release']},
        {'op':'mkdirs','path':'@tmpout/windows/bin'},
        {'op':'copyToDir','src':'@stage/dmd2/src/dmd/src/dmd.exe','dst':'@tmpout/windows/bin'},
        {'op':'copyToDir','src':'@'+dmd_prebuilt+'/windows/bin/sc.ini','dst':'@tmpout/windows/bin'},
    ]})
