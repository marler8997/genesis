if os.name == "nt":
    pass
else:
    def add_glibc_prebuilt(ver, deb_plat):
        def platform_select(**kwargs):
            value = kwargs.get(deb_plat)
            if value == None:
                raise Exception("undefined platform_select '{}'".format(deb_plat))
            return value

        genplat = platform_select(amd64='linux64', i386='linux32')
        triple = platform_select(amd64='x86_64-linux-gnu', i386='i386-linux-gnu')

        deb_mirror = config.get("deb_mirror")
        glibc6 = 'glibc6-'+ver+'-'+genplat+'-prebuilt'
        obj_set.setalias('glibc6-'+genplat+'-prebuilt', glibc6)
        obj_set.setalias('glibc6-'+genplat, glibc6)
        obj_set.add(glibc6,{'in':[],'ops':[
            {'op':'fetchArchive',
             'url':deb_mirror + '/pool/main/g/glibc/libc6_'+ver+'-3ubuntu1_'+deb_plat+'.deb',
             'to':'@stage/libc6',
             **platform_select(amd64={
                 'inHash':'xaanohc3qbsu62l5tuve4ogecz7oqwr5',
                 'outHash':'czl3zqdayqw55ltk73xahu4mifk5o4r4',
             },i386={
                 'inHash':'ofz4bo5kssppugrttjdktjqjy6u65ffw',
                 'outHash':'4elwndvz2grf7allr6xwtqcnevd6l4eh',
             })},
            {'op':'mkdir','path':'@tmpout'},
            {'op':'moveDirEntries','src':'@stage/libc6/data/lib/'+triple,'dst':'@tmpout/lib'},
            {'op':'fetchArchive',
             'url':deb_mirror + '/pool/main/g/glibc/libc-dev-bin_'+ver+'-3ubuntu1_'+deb_plat+'.deb',
             'to':'@stage/libc6-dev-bin',
             **platform_select(amd64={
                 'inHash':'7y3hi6ntv5zr3t6cmqtzjey2252fntje',
                 'outHash':'2m7zdt73l6lsoiajo22si6pbi4b5n5gb',
             },i386={
                 'inHash':'omw5pv6cecparjmnz5obovbm3fvpqixq',
                 'outHash':'fkrv5zkw25haliz5x3w6sunxjvlgykpy',
             })},
            {'op':'moveDirEntries','src':'@stage/libc6-dev-bin/data/usr/bin','dst':'@tmpout/bin'},
            {'op':'fixElf','interp':'@finalout/lib/ld-'+ver+'.so','rpath':'@finalout/lib','files':[
                '@tmpout/bin/rpcgen',
                '@tmpout/bin/gencat',
                '@tmpout/bin/sprof',
                # for some reason these ones can't be patched?
                #'@tmpout/bin/mtrace',
                #'@tmpout/bin/sotruss',
                '@tmpout/lib/libc-'+ver+'.so',
                '@tmpout/lib/libc.so.6',
                '@tmpout/lib/libpthread-'+ver+'.so',
                '@tmpout/lib/libpthread.so.0',
            ]},
            {'op':'fixElf','interp':None,'rpath':'@finalout/lib','files':[
                # for some reason, changing this one causes a segfault?
                #'@tmpout/lib/ld-'+ver+'.so',
                '@tmpout/lib/libanl-'+ver+'.so',
                '@tmpout/lib/libBrokenLocale-'+ver+'.so',
                '@tmpout/lib/libcidn-'+ver+'.so',
                '@tmpout/lib/libcrypt-'+ver+'.so',
                '@tmpout/lib/libdl-'+ver+'.so',
                '@tmpout/lib/libm-'+ver+'.so',
                '@tmpout/lib/libmemusage.so',
                '@tmpout/lib/libnsl-'+ver+'.so',
                '@tmpout/lib/libnss_compat-'+ver+'.so',
                '@tmpout/lib/libnss_dns-'+ver+'.so',
                '@tmpout/lib/libnss_files-'+ver+'.so',
                '@tmpout/lib/libnss_files.so.2',
                '@tmpout/lib/libnss_hesiod-'+ver+'.so',
                '@tmpout/lib/libnss_nis-'+ver+'.so',
                '@tmpout/lib/libnss_nisplus-'+ver+'.so',
                '@tmpout/lib/libpcprofile.so',
                '@tmpout/lib/libresolv-'+ver+'.so',
                '@tmpout/lib/librt-'+ver+'.so',
                '@tmpout/lib/libSegFault.so',
                '@tmpout/lib/libthread_db-1.0.so',
                '@tmpout/lib/libutil-'+ver+'.so',
            ] + platform_select(amd64=[
                '@tmpout/lib/libmvec-'+ver+'.so',
            ],i386=[])},
            # gcc looks for libc.so.6 in this directory
            # TODO: fix this for the i386 platform
            #{'op':'mkdirs','path':'@tmpout/lib/tls/x86_64/x86_64/'},
            #{'op':'symlink','path':'@tmpout/lib/tls/x86_64/x86_64/libc.so.6','to':'../../../libc-'+ver+'.so'},
        ]})
        # linux kernel headers for development
        obj_set.add('linux-glibc-dev-'+genplat,{'in':[],'ops':[
            {'op':'fetchArchive',
             'url':deb_mirror + '/pool/main/l/linux/linux-libc-dev_4.15.0-47.50_'+deb_plat+'.deb',
             'to':'@stage',
             **platform_select(amd64={
                 'inHash':'xfojrwus5ac6tiywfmmucycxxln4ogfd',
                 'outHash':'vm7xe7wpid3n6uqh5p2wy6fb5qegn2kf',
             },i386={
                 'inHash':'mkbhxudu3bvs5jwaisvpopnx6ac2dt7p',
                 'outHash':'5cxxdveqq4w5iebixxvitappl6pj53qw',
             })},
            {'op':'mkdir','path':'@tmpout'},
            {'op':'moveToDir','src':'@stage/data/usr/include','dst':'@tmpout'},
        ]})
        glibc6_dev = 'glibc6-dev-'+genplat+'-prebuilt'
        obj_set.add(glibc6_dev,{'in':[glibc6],'ops':[
            {'op':'fetchArchive',
             'url':deb_mirror + '/pool/main/g/glibc/libc6-dev_'+ver+'-3ubuntu1_'+deb_plat+'.deb',
             'to':'@stage',
             **platform_select(amd64={
                 'inHash':'oj6n7g3mdilpychxogu5hfrxoythbvy2',
                 'outHash':'qums2gettl3ftbyesopiqvhokpu2nk2y',
             },i386={
                 'inHash':'yifnw7qzh4g73fliprh4sd7wxslwjriq',
                 'outHash':'iebnb24ss2h2plbfz55yh3exmwr227k7',
             })},
            {'op':'mkdir','path':'@tmpout'},
            {'op':'moveToDir','src':'@stage/data/usr/include','dst':'@tmpout'},
            {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libBrokenLocale.so','to':'@in.'+glibc6+'/lib/libBrokenLocale.so.1'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libanl.so'         ,'to':'@in.'+glibc6+'/lib/libanl.so.1'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libcidn.so'        ,'to':'@in.'+glibc6+'/lib/libcidn.so.1'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libcrypt.so'       ,'to':'@in.'+glibc6+'/lib/libcrypt.so.1'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libdl.so'          ,'to':'@in.'+glibc6+'/lib/libdl.so.2'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libnsl.so'         ,'to':'@in.'+glibc6+'/lib/libnsl.so.1'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libnss_compat.so'  ,'to':'@in.'+glibc6+'/lib/libnss_compat.so.2'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libnss_dns.so'     ,'to':'@in.'+glibc6+'/lib/libnss_dns.so.2'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libnss_files.so'   ,'to':'@in.'+glibc6+'/lib/libnss_files.so.2'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libnss_hesiod.so'  ,'to':'@in.'+glibc6+'/lib/libnss_hesiod.so.2'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libnss_nis.so'     ,'to':'@in.'+glibc6+'/lib/libnss_nis.so.2'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libnss_nisplus.so' ,'to':'@in.'+glibc6+'/lib/libnss_nispllus.so.2'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libresolv.so'      ,'to':'@in.'+glibc6+'/lib/libresolv.so.2'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/librt.so'          ,'to':'@in.'+glibc6+'/lib/librt.so.1'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libthread_db.so'   ,'to':'@in.'+glibc6+'/lib/libthread_db.so.1'},
            {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libutil.so'        ,'to':'@in.'+glibc6+'/lib/libutil.so.1'},
            *platform_select(amd64=[
                {'op':'fixSymlink','path':'@tmpout/lib/'+triple+'/libmvec.so'        ,'to':'@in.'+glibc6+'/lib/libmvec.so.1'},
            ],i386=[
            ]),
            # TODO: need to patch these scripts
            #       replace /lib/'+triple+' with either libc6/lib or finalout/lib or something
            #{'op':'fixElf','interp':None,'rpath':make_rpath(glibc6),'files':[
            #    '@tmpout/lib/'+triple+'/libc.so'
            #    '@tmpout/lib/'+triple+'/libm.so'
            #    '@tmpout/lib/'+triple+'/libpthread.so'
            #]},
        ]})

    add_glibc_prebuilt('2.27', 'amd64')
    add_glibc_prebuilt('2.27', 'i386')

    def make_glibc_objects(bootstrap):
        gnu_mirror = config.get("gnu_mirror")
        def bootstrap_select_name(name):
            return name + ('-bootstrap' if bootstrap else '')
        glibc_before_install = bootstrap_select_name('glibc6-before-install')
        obj_set.add(glibc_before_install,{'config':{'notmpout':True},'in':[],'ops':[
            # does not declare any dependencies, instead, it depends on
            # the host environment having the needed tools
            {'op':'fetchArchive',
             'url':gnu_mirror+'/glibc/glibc-2.29.tar.bz2',
             'inHash':'ad6stg6tye5uonmu7ztwfhakitikwiyx',
             'outHash':'giu2evnig5f4mhl6hagdi24mfbjwgzjr',
             'to':'@stage'},
            {'op':'mkdir','path':'@stage/out'},
            {'op':'cd','path':'out'},
            {'op':'run','cmd':['../glibc-2.29/configure','--prefix=@finalout']},
            {'op':'runMake','args':[]},
        ]})
        glibc = bootstrap_select_name('glibc6')
        #config.set(bootstrap_select_name('libc6'), glibc)
        obj_set.add(glibc,{'config':{'notmpout':True},'in':[glibc_before_install],'ops':[
            {'op':'runMake','args':['install']},
        ] + select(bootstrap, [
            # I currently don't know how to compile glibc with the correct
            # rpath.  So for now I'm just going to patch it after the fact.
            {'op':'fixElf','interp':None,'rpath':'@finalout/lib','files':[
                '@tmpout/bin/gencat',
                '@tmpout/bin/getconf',
                '@tmpout/bin/getent',
                '@tmpout/bin/iconv',
                '@tmpout/bin/locale',
                '@tmpout/bin/localedef',
                '@tmpout/bin/makedb',
                '@tmpout/bin/pcprofiledump',
                '@tmpout/bin/pldd',
                '@tmpout/bin/sprof',
                '@tmpout/sbin/iconvconfig',
                '@tmpout/sbin/nscd',
                '@tmpout/sbin/zdump',
                '@tmpout/sbin/zic',
                '@tmpout/lib/audit/sotruss-lib.so',
                '@tmpout/lib/libanl-2.29.so',
                '@tmpout/lib/libBrokenLocale-2.29.so',
                '@tmpout/lib/libc-2.29.so',
                '@tmpout/lib/libcrypt-2.29.so',
                '@tmpout/lib/libdl-2.29.so',
                '@tmpout/lib/libm-2.29.so',
                '@tmpout/lib/libmemusage.so',
                '@tmpout/lib/libmvec-2.29.so',
                '@tmpout/lib/libnsl-2.29.so',
                '@tmpout/lib/libnss_compat-2.29.so',
                '@tmpout/lib/libnss_db-2.29.so',
                '@tmpout/lib/libnss_dns-2.29.so',
                '@tmpout/lib/libnss_files-2.29.so',
                '@tmpout/lib/libnss_hesiod-2.29.so',
                '@tmpout/lib/libpcprofile.so',
                '@tmpout/lib/libpthread-2.29.so',
                '@tmpout/lib/libresolv-2.29.so',
                '@tmpout/lib/librt-2.29.so',
                '@tmpout/lib/libSegFault.so',
                '@tmpout/lib/libthread_db-1.0.so',
                '@tmpout/lib/libutil-2.29.so',
            ]},
            # TODO: fix all the so files in @tmpout/lib/gconv/*
            # TODO: fix shebang for bash on these
            #   @tmpout/bin/ldd
            #   @tmpout/bin/sotruss
            #   @tmpout/bin/tzselect
            #   @tmpout/bin/xtrace
            # TODO: fix shebang for perl
            #   @tmpout/bin/mtrace
            # TODO: check out @tmpout/etc/ld.so.cache
        ],[])
        })
        glibc_dev = bootstrap_select_name('glibc6-dev')
        #config.set(bootstrap_select_name('libc6-dev'), glibc_dev)
        obj_set.add(glibc_dev,{'config':{'notmpout':True},'in':[glibc_before_install],'ops':[
            {'op':'runMake','args':['install']},
        ] + select(bootstrap, [
        ],[])
        })
    make_glibc_objects(True)
    make_glibc_objects(False)
