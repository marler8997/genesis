if os.name == "nt":
    obj_set.set_alias('dmc', 'dmc-8.57-prebuilt-win')
    obj_set.add(name='dmc-8.57-prebuilt-win', in_names=[], ops=[
        {'op':'fetchArchive',
         'url':'http://ftp.digitalmars.com/Digital_Mars_C++/Patch/dm857c.zip',
         'inHash':'tamaireeuevxtzpf4ewd2g3jofvr6pcr',
         'outHash':'ud3m72k4r3fcyazwflvupj3nrtjaiblg',
         'to':'@stage'},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/dm/bin','dst':'@tmpout'},
        {'op':'moveToDir','src':'@stage/dm/lib','dst':'@tmpout'},
        {'op':'moveToDir','src':'@stage/dm/include','dst':'@tmpout'},
    ])
