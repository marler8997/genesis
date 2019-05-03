if os.name == "nt":
    python3 = 'python-3.7.3-win64-prebuilt'
    obj_set.add(python3,{'in':[],'ops':[
        {'op':'fetchArchive',
         'url':'https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip',
         'inHash':'qhlluanoomgihh2gxaaaqfk4gubuiubr',
         'outHash':'pzfz6347fzrnopbnpfrgl7sy3rnhpizs',
         'to':'@tmpout'},
        {'op':'makeFile','path':'@tmpout/genesis/extra-bin','content':'python.exe\n','makeDirs':True},
    ]})
else:
    python3 = 'python-3.7.3-linux64'
    obj_set.add(python3,{'in':[],'ops':[
        {'op':'fetchArchive',
         'url':'https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz',
         'inHash':'knkcz3xq43ffwjruejfr5pymqa3gqsx3',
         'outHash':'p6oj66mvzq4eifqgpt5qx6ujf42xdsly',
         'to':'@stage'},
    ]})

obj_set.setalias('python3', python3)
