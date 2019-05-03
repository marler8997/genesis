if os.name == "nt":
    dmc = 'dmc-8.57-win-prebuilt'
    obj_set.setalias('dmc', dmc)
    obj_set.add(dmc,{'in':[],'ops':[
        {'op':'fetchArchive',
         'url':'http://ftp.digitalmars.com/Digital_Mars_C++/Patch/dm857c.zip',
         'inHash':'tamaireeuevxtzpf4ewd2g3jofvr6pcr',
         'outHash':'ud3m72k4r3fcyazwflvupj3nrtjaiblg',
         'to':'@stage'},
        {'op':'mkdir','path':'@tmpout'},
        {'op':'moveToDir','src':'@stage/dm/bin','dst':'@tmpout'},
        {'op':'moveToDir','src':'@stage/dm/lib','dst':'@tmpout'},
        {'op':'moveToDir','src':'@stage/dm/include','dst':'@tmpout'},
    ]})
