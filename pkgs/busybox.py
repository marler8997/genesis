def busybox_template(*, name, version, platform, prebuilt):#, libc, libc_dev, cc):

    if prebuilt:
        deb_mirror = config.get('deb_mirror')
        debian_platform = kwselect(platform, linux64='amd64', linux32='i386')
        glibcver = '2.27'
        glibc = obj_set.resolve_hash_name('glibc6-'+glibcver+'-linux64-prebuilt')
        return {'in':[glibc],'ops':[
            {'op':'fetchArchive',
             'url':deb_mirror+'/pool/universe/b/busybox/busybox_'+version+'-15ubuntu1.4_'+debian_platform+'.deb',
             'to':'@stage',
             **kwselect(platform, linux64={
                 'inHash':'famdif4qdqy4rfdd73c6ioeylhyopgzo',
                 'outHash':'s3vy6faahyg7mitq2knm73yacss4f3ui',
             },linux32={
                 'inHash':'',
                 'outHash':'',
             })},
            {'op':'mkdir','path':'@tmpout'},
            {'op':'moveToDir','src':'@stage/data/bin','dst':'@tmpout'},
            {'op':'fixElf','interp':'@'+glibc+'/lib/ld-'+glibcver+'.so','rpath':'@'+glibc+'/lib','files':[
                '@tmpout/bin/busybox',
            ]},
            # create a script to install all the symlinks
            {'op':'makeFile','path':'@tmpout/makesymlinks','content':
f'''for prog in $(@tmpout/bin/busybox --list); do
  ln -s busybox @tmpout/bin/$prog
done
'''},
            {'op':'run','cmd':['@tmpout/bin/busybox', 'ash', '@tmpout/makesymlinks']},
            {'op':'depend','in':'@'+glibc},
        ]}

if os.name != 'nt':
    obj_set.add_or_get_variation_set('busybox', busybox_template).add({
        'version':['1.22.0'],
        'platform':['linux64'],
        'prebuilt':[True],
        #'libc': [obj_set.resolve_name('glibc6-prebuilt')],
        #'libc_dev': [obj_set.resolve_name('glibc6-dev-prebuilt')],
        #'cc':[None],
    })
