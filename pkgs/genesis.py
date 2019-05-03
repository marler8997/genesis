python3 = obj_set.resolve_name("python3")

genesis_version = "0.0"
if os.name == "nt":
    genesis_url = 'https://github.com/marler8997/genesis/archive/v' + genesis_version + '.zip'
else:
    genesis_url = 'https://github.com/marler8997/genesis/archive/v' + genesis_version + '.tar.gz'

obj_set.add('genesis-' + genesis_version,{'in':[python3],'ops':[
    {'op':'fetchArchive',
     'url':genesis_url,
     'inHash':'zeiuwa4busa27ckamz5punavxnl3ysuo',
     'outHash':'3qt7so3gedcglumrxvqoevpfp7awxf6o',
     'to':'@stage'},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'move','src':'@stage/genesis-'+genesis_version,'dst':'@tmpout/src'},
    {'op':'mkdir','path':'@tmpout/bin'},
    {'op':'makeFile','path':'@tmpout/bin/gen.bat','content':'@@@in.'+python3+'\python.exe %~dp0..\src\gen %*'},
    {'op':'makeFile','path':'@tmpout/bin/makegens.bat','content':'@@@in.'+python3+'\python.exe %~dp0..\src\makegens %*'},
    {'op':'depend','in':'@in.'+python3},
]})
