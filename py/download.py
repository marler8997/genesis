import sys
import os

#import requests
import urllib.request

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log
import genesis

if os.name == "nt":
    import winreg
    INTERNET_SETTINGS = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
    def winregGetValue(key, name):
        try:
            return winreg.QueryValueEx(key, name)
        except WindowsError as e:
            if e.errno == 2:
                return None, None
            raise
    def winregGetTypedValue(key, name, type):
        value, actual_type = winregGetValue(key, name)
        if actual_type and actual_type != type:
            raise Exception("expected registry value '{}' to be type {} but is {}".format(
                name, type, actual_type
            ))
        return value
    def winregGetString(key, name):
        return winregGetTypedValue(key, name, winreg.REG_SZ)

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import re
    #value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = str(re.sub('[^\w\s-]', '_', value).strip().lower())
    value = str(re.sub('[-\s]+', '-', value))
    return value

'''
Example using the new requests library
request = requests.get(url)
with open(downloading, "wb") as file:
    file.write(request.content)

if request.status_code != 200:
    os.remove(downloading)
    sys.exit("GET '{}' failed with HTTP response {}".format(url, request.status_code))
'''

_proxy_settings_instance = None
class ProxySettings:
    def init():
        global _proxy_settings_instance
        if not _proxy_settings_instance:
            _proxy_settings_instance = ProxySettings()
        return _proxy_settings_instance
    def __init__(self):
        self.proxies = urllib.request.getproxies()
        if os.name == "nt":
            # check if an auto configure script is being used
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, INTERNET_SETTINGS, 0, winreg.KEY_READ) as key:
                autoconfurl = winregGetString(key, "AutoConfigURL")
                if autoconfurl:
                    slug_url = slugify(autoconfurl)
                    downloaded_path = os.path.join(genesis.get_proxy_path(), slug_url)
                    if os.path.exists(downloaded_path):
                        log.verbose("autoconf script '{}' has already been downloaded".format(downloaded_path))
                    else:
                        tmp_path = downloaded_path + ".downloading"
                        if os.path.exists(tmp_path):
                            sys.exit("not impl: download path '{}' already exists".format(tmp_path))
                        download_no_proxy_init(autoconfurl, tmp_path)
                        log.rename(tmp_path, downloaded_path)
                    log.log("WARNING: need to parse/use '{}' (probably need spidermonkey and/or pypac)".format(downloaded_path))

def getproxies():
    return ProxySettings.init().proxies

def download_no_proxy_init(url, dst):
    log.log("FETCH   {}".format(url))
    log.verbose("downloading '{}' to '{}'...".format(url, dst))
    #urllib.request.urlretrieve(url, dst)
    response = urllib.request.urlopen(url)
    with open(dst, "wb") as file:
        file.write(response.read())

def download(url, dst):
    ProxySettings.init()
    download_no_proxy_init(url, dst)
