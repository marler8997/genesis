if os.name == "nt":
    obj_set.set_alias('python3', 'python-3.7.3-prebuilt-win64')
    obj_set.add(name='python-3.7.3-prebuilt-win64', in_names=[], ops=[
        {'op':'fetchArchive',
         'url':'https://www.python.org/ftp/python/3.7.3/python-3.7.3-embed-amd64.zip',
         'inHash':'qhlluanoomgihh2gxaaaqfk4gubuiubr',
         'outHash':'pzfz6347fzrnopbnpfrgl7sy3rnhpizs',
         'to':'@tmpout'},
        {'op':'makeFile','path':'@tmpout/genesis/extra-bin','content':'python.exe\n','makeDirs':True},
    ])
else:
    obj_set.set_alias('python3', 'python-3.7.3-linux64')
    obj_set.add(name='python-3.7.3-linux64', in_names=[], ops=[
        {'op':'fetchArchive',
         'url':'https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz',
         'inHash':'knkcz3xq43ffwjruejfr5pymqa3gqsx3',
         'outHash':'p6oj66mvzq4eifqgpt5qx6ujf42xdsly',
         'to':'@stage'},
    ])
