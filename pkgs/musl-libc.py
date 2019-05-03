def musl_template(*, name, version, platform, prebuilt):
    deb_mirror = config.get('deb_mirror')
    def platform_select(**kwargs):
        value = kwargs.get(platform)
        if value == None:
            raise Exception("undefined platform_select '{}'".format(debian_platform))
        return value
    debian_platform = platform_select(linux64='amd64', linux32='i386')
    triple = platform_select(linux64='x86_64-linux-musl', linux32='i386-linux-musl')
    return {'in':[],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/universe/m/musl/musl_1.1.19-1_'+debian_platform+'.deb',
         'to':'@stage',
         **platform_select(linux64={
             'inHash':'uvbz5vosoh2pdupn773rc2zficxhfx4r',
             'outHash':'fdxycnvnhmuzzvsvh4edkuvpq67nsnm5',
         },linux32={
             'inHash':'2yp6cugvazqeqc2js2xrx47b65pq6tdn',
             'outHash':'g7zlctjwo2ow7c3iez7slvn4p7tdcdu6',
         })},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'mkdir','path':'@tmpout/lib'},
        {'op':'moveToDir','src':'@stage/data/lib/'+triple+'/libc.so','dst':'@tmpout/lib'},
    ]}
obj_set.add_variation_set('musl', musl_template).add({
    'version':['1.1.19'],
    'platform':['linux64','linux32'],
    'prebuilt':[True],
})

def musl_dev_template(*, name, version, platform, prebuilt):
    deb_mirror = config.get('deb_mirror')
    def platform_select(**kwargs):
        value = kwargs.get(platform)
        if value == None:
            raise Exception("undefined platform_select '{}'".format(debian_platform))
        return value
    debian_platform = platform_select(linux64='amd64', linux32='i386')
    triple = platform_select(linux64='x86_64-linux-musl', linux32='i386-linux-musl')
    return {'in':[],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/universe/m/musl/musl-dev_1.1.19-1_'+debian_platform+'.deb',
         'to':'@stage',
         **platform_select(linux64={
             'inHash':'lrdypkifa7mewpmisdzllnghsgrupwmb',
             'outHash':'rz73p6jcmsapwsdyjute5cdpwvduuub7',
         },linux32={
             'inHash':'g2uqhm3etzmiy327jmdwf7uomju3klif',
             'outHash':'kkvpdxrl7ys6em3dsr7uxicm5qzoiq5g',
         })},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'unwrapDir','path':'@stage/data/usr/include/'+triple},
        {'op':'moveToDir','src':'@stage/data/usr/include','dst':'@tmpout'},
        {'op':'unwrapDir','path':'@stage/data/usr/lib/'+triple},
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    ]}

obj_set.add_variation_set('musl-dev', musl_dev_template).add({
    'version':['1.1.19'],
    'platform':['linux64','linux32'],
    'prebuilt':[True],
})



'''
def add_musl_libc_prebuilt(deb_plat):
    deb_mirror = config.get('deb_mirror')

    def platform_select(**kwargs):
        value = kwargs.get(deb_plat)
        if value == None:
            raise Exception("undefined platform_select '{}'".format(deb_plat))
        return value
    genplat = platform_select(amd64='linux64', i386='linux32')
    triple = platform_select(amd64='x86_64-linux-musl', i386='i386-linux-musl')

    obj_set.add('musl-libc-1.1.19-'+genplat+'-prebuilt',{'in':[],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/universe/m/musl/musl_1.1.19-1_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'uvbz5vosoh2pdupn773rc2zficxhfx4r',
             'outHash':'fdxycnvnhmuzzvsvh4edkuvpq67nsnm5',
         },i386={
             'inHash':'2yp6cugvazqeqc2js2xrx47b65pq6tdn',
             'outHash':'g7zlctjwo2ow7c3iez7slvn4p7tdcdu6',
         })},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'mkdir','path':'@tmpout/lib'},
        {'op':'moveToDir','src':'@stage/data/lib/'+triple+'/libc.so','dst':'@tmpout/lib'},
    ]})
    obj_set.add('musl-libc-dev-1.1.19-'+genplat+'-prebuilt',{'in':[],'ops':[
        {'op':'fetchArchive',
         'url':deb_mirror + '/pool/universe/m/musl/musl-dev_1.1.19-1_'+deb_plat+'.deb',
         'to':'@stage',
         **platform_select(amd64={
             'inHash':'lrdypkifa7mewpmisdzllnghsgrupwmb',
             'outHash':'rz73p6jcmsapwsdyjute5cdpwvduuub7',
         },i386={
             'inHash':'g2uqhm3etzmiy327jmdwf7uomju3klif',
             'outHash':'kkvpdxrl7ys6em3dsr7uxicm5qzoiq5g',
         })},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'unwrapDir','path':'@stage/data/usr/include/'+triple},
        {'op':'moveToDir','src':'@stage/data/usr/include','dst':'@tmpout'},
        {'op':'unwrapDir','path':'@stage/data/usr/lib/'+triple},
        {'op':'moveToDir','src':'@stage/data/usr/lib','dst':'@tmpout'},
    ]})

add_musl_libc_prebuilt('amd64')
add_musl_libc_prebuilt('i386')
#obj_set.setalias('musl-libc', 'musl-libc-1.1.19-linux64-prebuilt')
#obj_set.setalias('musl-libc-dev', 'musl-libc-dev-1.1.19-linux64-prebuilt')
'''
