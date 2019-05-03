if os.name == "nt":
    pass
else:
    deb_mirror = config.get("deb_mirror")
    gnu_mirror = config.get('gnu_mirror')
    libc6 = 'libc6-2.27-linux64-prebuilt'

    # the GNU C preprocessor
    # https://packages.ubuntu.com/bionic/cpp-7
    '''
    obj_set.add("gnucpp-linux64",{'in':[libc6],'ops':[
        {'op':'mkdir','path':'@tmpout'},
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/m/make-dfsg/make_4.1-9.1ubuntu1_amd64.deb',
         'inHash':'k2bgcerinyizh3fg3oarnpusm2cwt4yo',
         'outHash':'rozq5ftbkdirmoshw5mwyobrtu3chmel',
         'to':'@stage/make'},
        {'op':'moveDirEntries','src':'@stage/make/data/usr/bin','dst':'@tmpout/bin'},
        {'op':'fixElf','interp':'@in.'+libc6+'/lib/ld-2.27.so','rpath':make_rpath(libc6),'files':[
            '@tmpout/bin/make',
            # for some reason this ones can't be patched?
            #'@tmpout/bin/make-first-existing-target',
        ]},
    ]})
    '''

    def add_gcc_objects(bootstrap):
        global gnu_mirror
        global obj_set
        def bootstrap_select_name(name):
            return name + ('-bootstrap' if bootstrap else '')

        glibc = bootstrap_select_name('glibc6')

        gmpver = '6.1.2'
        gmp = bootstrap_select_name('gmp-'+gmpver)
        obj_set.add(gmp,{'in':[glibc],'ops':[
            {'op':'fetchArchive',
             'url':gnu_mirror+'/gmp/gmp-'+gmpver+'.tar.xz',
             'inHash':'4kbm3lwa4h7jfjwlja3mhl3lc4epxcgr',
             'outHash':'yzbc6xfe5s42733o4ynvql47a24gm56j',
             'to':'@stage'},
            {'op':'mkdir','path':'@stage/out'},
            {'op':'cd','path':'out'},
            {'op':'run',
             'cmd':['../gmp-'+gmpver+'/configure','--prefix=@tmpout',
                    '--with-sysroot=@in.'+glibc,
             ],'env':{
                 #'LDFLAGS':'-nostdinc',
                 'LT_SYS_LIBRARY_PATH':'@in.'+glibc+'/lib',
             }},
            {'op':'runMake','args':[]},
            {'op':'runMake','args':['install']},
            {'op':'fileReplace','replace':'@tmpout','with':'@finalout','files':['@tmpout/lib/libgmp.la']},
            {'op':'depend','in':'@in.'+glibc},
        ] + select(bootstrap, [
            {'op':'fixElf','rpath':'@in.'+glibc+'/lib','files':[
                '@tmpout/lib/libgmp.so.10.3.2',
            ]},
        ],[])
        })
        mpfrver = '4.0.2'
        mpfr = bootstrap_select_name('mpfr-'+mpfrver)
        obj_set.add(mpfr,{'in':[glibc, gmp],'ops':[
            {'op':'fetchArchive',
             'url':gnu_mirror+'/mpfr/mpfr-'+mpfrver+'.tar.xz',
             'inHash':'fonqnd5sdhlyzgwocyjm2ujxebu5e5p3',
             'outHash':'bmgqsgqaoww6ieqeiqkjzlafdxkqatuc',
             'to':'@stage'},
            {'op':'mkdir','path':'@stage/out'},
            {'op':'cd','path':'out'},
            {'op':'run','cmd':['../mpfr-'+mpfrver+'/configure','--prefix=@tmpout',
                               '--with-libc=@in.'+glibc,
                               '--with-gmp=@in.'+gmp,
                               ]},
            {'op':'runMake','args':[]},
            {'op':'runMake','args':['install']},
            {'op':'fileReplace','replace':'@tmpout','with':'@finalout','files':[
                '@tmpout/lib/libmpfr.la',
                '@tmpout/lib/pkgconfig/mpfr.pc',
            ]},
            {'op':'depend','in':'@in.'+glibc},
            {'op':'depend','in':'@in.'+gmp},
        ] + select(bootstrap, [
            {'op':'fixElf','rpath':'@in.'+glibc+'/lib','files':[
                '@tmpout/lib/libmpfr.so.6.0.2',
            ]},
        ],[])
        })
        mpcver = '1.1.0'
        mpc = bootstrap_select_name('mpc-'+mpcver)
        obj_set.add(mpc,{'in':[glibc, gmp, mpfr],'ops':[
            {'op':'fetchArchive',
             'url':gnu_mirror+'/mpc/mpc-'+mpcver+'.tar.gz',
             'inHash':'742z75cxvoven2iv2uicp5nexwqtz275',
             'outHash':'z6rssnmvsv3spkopsjdfe5c4djyeh5uj',
             'to':'@stage'},
            {'op':'mkdir','path':'@stage/out'},
            {'op':'cd','path':'out'},
            {'op':'run','cmd':['../mpc-'+mpcver+'/configure','--prefix=@tmpout',
                               '--with-gmp=@in.'+gmp,
                               '--with-mpfr=@in.'+mpfr,
                               ]},
            {'op':'runMake','args':[]},
            {'op':'runMake','args':['install']},
            {'op':'fileReplace','replace':'@tmpout','with':'@finalout','files':[
                '@tmpout/lib/libmpc.la',
            ]},
            {'op':'depend','in':'@in.'+glibc},
            {'op':'depend','in':'@in.'+gmp},
            {'op':'depend','in':'@in.'+mpfr},
        ] + select(bootstrap, [
            {'op':'fixElf','rpath':make_rpath(glibc, gmp, mpfr),'files':[
                '@tmpout/lib/libmpc.so.3.1.0',
            ]},
        ],[])
        })
        gccver = '8.3.0'
        gcc = bootstrap_select_name('gcc-'+gccver)
        obj_set.add(gcc,{'in':[glibc, gmp, mpfr, mpc],'ops':[
            {'op':'fetchArchive',
             'url':gnu_mirror+'/gcc/gcc-'+gccver+'/gcc-'+gccver+'.tar.xz',
             'inHash':'ulg6vva6j2ansdz7niipjm4acnkictbi',
             'outHash':'6xuq66jkawm4vazmsvpzsh372uvwic7c',
             'to':'@stage'},
            {'op':'mkdir','path':'@stage/out'},
            {'op':'cd','path':'out'},
            # NOTE sure if I need this CPPFLAGS environment variable, I got this error
            # cc1: error: no include path in which to search for stdc-predef.h
            {'op':'setEnv','name':'CPPFLAGS','value':'-I@in.'+glibc+'/include'},
            {'op':'run','cmd':['../gcc-'+gccver+'/configure','--prefix=@tmpout',
                               '--with-gmp=@in.'+gmp,
                               '--with-mpfr=@in.'+mpfr,
                               '--with-mpc=@in.'+mpc,
                               '--disable-multilib',
                               #'--enabled-shared',
                               #'--enabled-threads=posix',
                               #'--enabled-__cxa-atexit',
                               #'--enabled-clocale=gnu',
                               #'--enabled-languages=all',
                               ]},
            {'op':'runMake','args':[]},
            {'op':'runMake','args':['install']},
        ]})
    add_gcc_objects(True)
    add_gcc_objects(False)
