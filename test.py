import requests

from stem import Signal
from stem.control import Controller


def renewIp():
    arequests = requests.session()
    arequests.proxies = {'http':  'socks5://127.0.0.1:9050',
                         'https': 'socks5://127.0.0.1:9050'}

    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="anonbynuamf1204vujw")
        controller.signal(Signal.NEWNYM)
        print("renewingIp")
    
    return arequests

ar = renewIp()
print(ar.get("http://httpbin.org/ip").text)
br = renewIp()
print(br.get("http://httpbin.org/ip").text)


