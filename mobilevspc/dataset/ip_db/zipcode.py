import urllib2 as urllib
import fileinput
import json

# Requires https://github.com/fiorix/freegeoip/releases

url = "http://localhost:8080/json/{}"

for ip in fileinput.input():
    ip = ip.strip()
    req = urllib.urlopen(url.format(ip))
    res = json.loads(req.read())
    print ip, res.get('region_code', ''), res.get('city', ''), res.get('zip_code', '')
    


