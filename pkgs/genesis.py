python3 = obj_set.get_alias("python3")

genesis_version = "0.0"
if os.name == "nt":
    genesis_url = 'https://github.com/marler8997/genesis/archive/v' + genesis_version + '.zip'
else:
    genesis_url = 'https://github.com/marler8997/genesis/archive/v' + genesis_version + '.tar.gz'

obj_set.add(name='genesis-' + genesis_version, in_names=[python3], ops=[
    {'op':'fetchArchive',
     'url':genesis_url,
     'inHash':'rib2477auklfm66l2jastchgxw3wsq6u',
     'outHash':'gy4nz5qm2hzdhvlplv7vsw5tfwumysep',
     'to':'@stage'},
    {'op':'unwrapDir','path':'@stage/genesis-'+genesis_version},
    {'op':'mkdir','path':'@tmpout'},
    {'op':'mkdir','path':'@tmpout/bin'},
    {'op':'moveToDir','src':'@stage/corepkgs.py','dst':'@tmpout/bin'},
    {'op':'depend','in':'@'+python3},
])
