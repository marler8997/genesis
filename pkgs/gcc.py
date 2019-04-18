if os.name == "nt":
    pass
else:
    deb_mirror = obj_set.get_alias("deb_mirror")
    libc = 'libc6-prebuilt-linux64'

    # the GNU C preprocessor
    # https://packages.ubuntu.com/bionic/cpp-7
    '''
    obj_set.add(name="gnucpp-linux64", in_names=[libc], ops=[
        {'op':'mkdir','path':'@tmpout'},
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/main/m/make-dfsg/make_4.1-9.1ubuntu1_amd64.deb',
         'inHash':'k2bgcerinyizh3fg3oarnpusm2cwt4yo',
         'outHash':'rozq5ftbkdirmoshw5mwyobrtu3chmel',
         'to':'@stage/make'},
        {'op':'moveDirEntries','src':'@stage/make/data/usr/bin','dst':'@tmpout/bin'},
        {'op':'fixElf','interp':'@'+libc+'/lib/ld-2.27.so','rpath':make_rpath(libc),'files':[
            '@tmpout/bin/make',
            # for some reason this ones can't be patched?
            #'@tmpout/bin/make-first-existing-target',
        ]},
    ])
    '''
