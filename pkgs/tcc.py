def tcc_template(*, name, version, libc, libc_dev, coreutils, make, cc):
    is_glibc = 'glibc6' in libc

    inlist = [libc, libc_dev]
    if coreutils:
        inlist.append(coreutils)
    if make:
        inlist.append(make)
    if cc:
        inlist.append(cc)

    bootstrap = name.endswith("-bootstrap")

    extra_config = {}
    if bootstrap:
        extra_config = {**extra_config, 'notmpout':True}

    return {'config':{**extra_config, 'ifaces':['c-compiler']},'in':inlist,'ops':[
        {'op':'fetchArchive',
         'url':'http://download.savannah.gnu.org/releases/tinycc/tcc-'+version+'.tar.bz2',
         'inHash':'c2j35iiyxbiqezdm64tvs5am4qhjzpwa',
         'outHash':'mfjdbifcrs73pspxcaleftdiszfq4phb',
         'to':'@stage'},
    ] + select(coreutils, [
        {'op':'prependPathEnv','path':f'@{coreutils}/bin'},
    ], []) + [
    ] + select(make, [
        {'op':'prependPathEnv','path':f'@{make}/bin'},
    ], []) + [
        {'op':'mkdir','path':'@stage/out'},
        {'op':'cd','path':'out'},
        {'op':'fileReplace','replace':' /usr/bin/perl','with':'/run/current-system/sw/bin/perl','files':[
            '@stage/tcc-'+version+'/texi2pod.pl',
        ]},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'mkdir','path':'@tmpout/lib'},
    ] + select(is_glibc, [
        {'op':'symlink','path':'@tmpout/lib/libc.so','to':'@'+libc+'/lib/libc.so.6'},
        {'op':'symlink','path':'@tmpout/lib/ld-linux-x86-64.so.2','to':'@'+libc+'/lib/ld-linux-x86-64.so.2'},
        {'op':'run',
         'cmd':['../tcc-'+version+'/configure',
                '--prefix=@tmpout',
                '--sysincludepaths='
                +  '@'+libc_dev+'/include'
                + ':@'+libc_dev+'/include/x86_64-linux-gnu'
                + ':@finalout/lib/tcc/include',
                '--libpaths=@finalout/lib:@'+libc_dev+'/lib/x86_64-linux-gnu',
                '--crtprefix=@'+libc_dev+'/lib/x86_64-linux-gnu',
                '--elfinterp=@'+libc+'/lib/ld-2.27.so',
                #'--sysroot=@'+libc,
         ] + select(bootstrap, [], [
             f'--cc=@{cc}/genesis/i/c-compiler',
         ])},
    ],[
        {'op':'run',
         'cmd':['../tcc-'+version+'/configure',
                '--prefix=@tmpout',
                '--sysincludepaths='
                +  '@'+libc_dev+'/include',
                '--libpaths=@'+libc+'/lib',
                '--crtprefix=@'+libc_dev+'/lib',
                '--elfinterp=@'+libc+'/lib/libc.so',
                '--config-musl',
                #'--sysroot=@'+libc,
         ] + select(bootstrap, [], [
             f'--cc=@{cc}/genesis/i/c-compiler',
         ])},
    ]) + [
        {'op':'runMake','args':['tcc']},
        # we need to install before building libtcc1.a because
        # tcc will need to access the header files in their final output path
        {'op':'runMake','args':['install']},
        {'op':'runMake','args':['libtcc1.a']},
        {'op':'runMake','args':['install']},
        {'op':'depend','in':'@'+libc},
        {'op':'depend','in':'@'+libc_dev},
        # TODO: for prebuilt glibc:
        #           tcc: error: undefined symbol '__libc_csu_fini'
        #           tcc: error: undefined symbol '__libc_csu_init'
        #       Need to include @libc-dev/lib/x86_64-linux-gnu/libc_nonshared.a
        #       Also need to tell tcc to add rpaths
        {'op':'mkdir','path':'@tmpout/genesis/i'},
        {'op':'symlink','path':'@tmpout/genesis/i/c-compiler','to':'../../bin/tcc'},
    ]}

if os.name != 'nt':
    #obj_set.add_or_get_variation_set('tcc', tcc_template).add({
    #    'version':['0.9.27'],
    #    'libc': [obj_set.resolve_name('glibc6-prebuilt')],
    #    'libc_dev': [obj_set.resolve_name('glibc6-dev-prebuilt')],
    #})
    obj_set.add_or_get_variation_set('tcc-bootstrap', tcc_template).add({
        'version':['0.9.27'],
        'libc': [obj_set.resolve_name('glibc6-prebuilt')],
        'libc_dev': [obj_set.resolve_name('glibc6-dev-prebuilt')],
        'coreutils':[None],
        'make':[None],
        'cc':[None],
    })
    obj_set.add_or_get_variation_set('tcc-bootstrap', tcc_template).add({
        'version':['0.9.27'],
        'libc': [obj_set.get_variation('musl', platform='linux64')],
        'libc_dev': [obj_set.get_variation('musl-dev', platform='linux64')],
        'coreutils':[None],
        'make':[None],
        'cc':[None],
    })
    obj_set.add_or_get_variation_set('tcc-bootstrap2', tcc_template).add({
        'version':['0.9.27'],
        'libc': [obj_set.get_variation('musl', platform='linux64')],
        'libc_dev': [obj_set.get_variation('musl-dev', platform='linux64')],
        'coreutils':[obj_set.get_variation('busybox')],
        'make':[obj_set.get_variation('gnumake')],
        'cc':[obj_set.get_variation('tcc-bootstrap', libc=obj_set.get_variation('musl', platform='linux64'))],
    })

'''
import enum
class CLib(enum.Enum):
    GLIBC = 0
    MUSL  = 1

def add_tcc(ver, bootstrap, clib, libc_name, libc6, libc6_dev):
    global CLib
    tcc = 'tcc-' + libc_name + '-' + ver + select(bootstrap, '-bootstrap', '')
    config.set('tcc-' + libc_name + select(bootstrap, '-bootstrap', ''), tcc)
    obj_set.add_no_resolve(tcc,{'config':{'notmpout':True},'in':[libc6, libc6_dev],'ops':[
        {'op':'fetchArchive',
         'url':'http://download.savannah.gnu.org/releases/tinycc/tcc-'+ver+'.tar.bz2',
         'inHash':'c2j35iiyxbiqezdm64tvs5am4qhjzpwa',
         'outHash':'mfjdbifcrs73pspxcaleftdiszfq4phb',
         'to':'@stage'},
        {'op':'mkdir','path':'@stage/out'},
        {'op':'cd','path':'out'},
        {'op':'fileReplace','replace':' /usr/bin/perl','with':'/run/current-system/sw/bin/perl','files':[
            '@stage/tcc-'+ver+'/texi2pod.pl',
        ]},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'mkdir','path':'@tmpout/lib'},
    ] + select(clib == CLib.GLIBC, [
        {'op':'symlink','path':'@tmpout/lib/libc.so','to':'@'+libc6+'/lib/libc.so.6'},
        {'op':'symlink','path':'@tmpout/lib/ld-linux-x86-64.so.2','to':'@'+libc6+'/lib/ld-linux-x86-64.so.2'},
        {'op':'run',
         'cmd':['../tcc-'+ver+'/configure',
                '--prefix=@tmpout',
                '--sysincludepaths='
                +  '@'+libc6_dev+'/include'
                + ':@'+libc6_dev+'/include/x86_64-linux-gnu'
                + ':@finalout/lib/tcc/include',
                '--libpaths=@finalout/lib:@'+libc6_dev+'/lib/x86_64-linux-gnu',
                '--crtprefix=@'+libc6_dev+'/lib/x86_64-linux-gnu',
                '--elfinterp=@'+libc6+'/lib/ld-2.27.so',
                #'--sysroot=@'+libc6,
                ]},
    ],[
        {'op':'run',
         'cmd':['../tcc-'+ver+'/configure',
                '--prefix=@tmpout',
                '--sysincludepaths='
                +  '@'+libc6_dev+'/include',
                '--libpaths=@'+libc6+'/lib',
                '--crtprefix=@'+libc6_dev+'/lib',
                '--elfinterp=@'+libc6+'/lib/libc.so',
                '--config-musl',
                #'--sysroot=@'+libc6,
         ]},
    ]) + [
        {'op':'runMake','args':['tcc']},
        # we need to install before building libtcc1.a because
        # tcc will need to access the header files in their final output path
        {'op':'runMake','args':['install']},
        {'op':'runMake','args':['libtcc1.a']},
        {'op':'runMake','args':['install']},
        {'op':'depend','in':'@'+libc6},
        {'op':'depend','in':'@'+libc6_dev},
        # TODO: for prebuilt glibc:
        #           tcc: error: undefined symbol '__libc_csu_fini'
        #           tcc: error: undefined symbol '__libc_csu_init'
        #       Need to include @libc-dev/lib/x86_64-linux-gnu/libc_nonshared.a
        #       Also need to tell tcc to add rpaths
    ]})

if os.name != 'nt':
    add_tcc('0.9.27', True, CLib.GLIBC, 'glibc6-prebuilt',
            obj_set.resolve_name('glibc6-prebuilt'),
            obj_set.resolve_name('glibc6-dev-prebuilt'))
    add_tcc('0.9.27', True, CLib.MUSL, 'musl-prebuilt',
            obj_set.get_variation('musl', platform='linux64'),
            obj_set.get_variation('musl-dev', platform='linux64'))
'''
