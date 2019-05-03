
def add_nix(ver):
    nix = 'nix-' + ver + '-linux64-prebuilt-bootstrap'
    platform ='x86_64-linux'
    obj_set.add(nix, {'in':[],'ops':[
        {'op':'fetchArchive',
         'url':'https://nixos.org/releases/nix/nix-' + ver + '/nix-' + ver + '-' + platform + '.tar.bz2',
         'inHash':'yjfcuyzkfcwliu55xy37ywgagxh7n3mu',
         'outHash':'7bjpwivdibsbgb67noedxfqnuje3cqta',
         'to':'@stage'},
        {'op':'run','cmd':['@stage/nix-' + ver + '-' + platform + '/install']},
    ]})

add_nix('2.2.2')
