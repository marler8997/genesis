if os.name == "nt":
    pass
else:
    def gnumake_template(*, name, version, platform, prebuilt):
        if prebuilt:
            deb_mirror = config.get('deb_mirror')
            debian_platform = kwselect(platform, linux64='amd64', linux32='i386')
            glibcver = '2.27'
            glibc = obj_set.resolve_hash_name('glibc6-'+glibcver+'-linux64-prebuilt')
            return {'in':[glibc],'ops':[
                {'op':'fetchArchive',
                 'url':deb_mirror + '/pool/main/m/make-dfsg/make_'+version+'.1ubuntu1_'+debian_platform+'.deb',
                 'to':'@stage/make',
                 **kwselect(platform, linux64={
                     'inHash':'k2bgcerinyizh3fg3oarnpusm2cwt4yo',
                     'outHash':'rozq5ftbkdirmoshw5mwyobrtu3chmel',
                 },linux32={
                     'inHash':'',
                     'outHash':'',
                 })},
                {'op':'mkdir','path':'@tmpout'},
                {'op':'mkdir','path':'@tmpout/bin'},
                {'op':'moveToDir','src':'@stage/make/data/usr/bin/make','dst':'@tmpout/bin'},
                # ignoring make-first-existing-target because it requires perl
                # if it's needed it can be in a separate package
                {'op':'fixElf','interp':'@'+glibc+'/lib/ld-2.27.so','rpath':make_rpath2(glibc),'files':[
                    '@tmpout/bin/make',
                ]},
                {'op':'depend','in':'@'+glibc},
            ]}
    obj_set.add_or_get_variation_set('gnumake', gnumake_template).add({
        'version':['4.1-9'],
        'platform':['linux64'],
        'prebuilt':[True],
    })

    '''
    def add_gnumake():
        deb_mirror = config.get("deb_mirror")
        glibc6 = 'glibc6-2.27-linux64-prebuilt'
        gnumake_prebuilt = 'gnumake-linux64-prebuilt'
        obj_set.setalias('gnumake', 'gnumake-prebuilt')
        obj_set.add(gnumake_prebuilt, {'in':[glibc6],'ops':[
            {'op':'mkdir','path':'@tmpout'},
            {'op':'fetchArchive',
             'url':deb_mirror + '/pool/main/m/make-dfsg/make_4.1-9.1ubuntu1_amd64.deb',
             'inHash':'k2bgcerinyizh3fg3oarnpusm2cwt4yo',
             'outHash':'rozq5ftbkdirmoshw5mwyobrtu3chmel',
             'to':'@stage/make'},
            {'op':'mkdir','path':'@tmpout/bin'},
            {'op':'moveToDir','src':'@stage/make/data/usr/bin/make','dst':'@tmpout/bin'},
            # ignoring make-first-existing-target because it requires perl
            # if it's needed it can be in a separate package
            {'op':'fixElf','interp':'@in.'+glibc6+'/lib/ld-2.27.so','rpath':make_rpath(glibc6),'files':[
                '@tmpout/bin/make',
            ]},
        ]})

    add_gnumake()
    '''
