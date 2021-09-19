import toml
import os

ACCESSKEY = toml.load('config.toml')['ACCESSKEY']
CACHELOCATION = toml.load('config.toml')['CACHELOCATION']
CACHELOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHELOCATION)

def geoipapirequiest(ipaddr):
    """
    make api request to http://api.ipstack.com/
    """
    import requests
    url = "http://api.ipstack.com/" + ipaddr + f"?access_key={ACCESSKEY}"
    response = requests.get(url)
    return response.json()

def loadgeoipdata(filename):
    """
    load geoip data from file. if file doesn't exist, return empty dict
    """
    import json
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def dumpgeoipdata(filename, data):
    """
    dump geoip data to file
    """
    import json
    with open(filename, 'w') as f:
        json.dump(data, f)

def getgeoipdata(ipaddrs, data, verbose=False):
    """
    get geoip data from api, do not request if ip is in data
    """
    reqcount = 0
    for ipaddr in ipaddrs:
        if ipaddr not in data:
            if verbose: print(f"Not found: {ipaddr}; Requesting...")
            data[ipaddr] = geoipapirequiest(ipaddr)
            reqcount += 1
        else:
            if verbose: print(f"Found: {ipaddr}; Skipping...")
    return data, reqcount

def runapi(ipaddrs):
    global CACHELOCATION
    cachedata = loadgeoipdata(CACHELOCATION)
    if len(cachedata) == 0:
        print("No data in cache")
        if input("Do you want to request data? (y/n) ") == "n":
            print("No data requested. Aborting")
            exit(0)
    print(f"Cache size: {len(cachedata)}; Request size: {len(ipaddrs)}")
    data, reqcount = getgeoipdata(ipaddrs, cachedata)
    print(f"Requested {reqcount} times")
    dumpgeoipdata(CACHELOCATION, data)
