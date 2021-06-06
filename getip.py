import logging
import socket
import time

global_get_internal_ip = []
global_get_external_ip = []


def get_external_ip():
    import urllib.request
    import requests
    from json import load
    from urllib.request import urlopen

    try:
        ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        ip2 = requests.get('https://checkip.amazonaws.com').text.strip()
        ip3 = load(urlopen('https://api.ipify.org/?format=json'))['ip']

        global_get_external_ip.append(ip)
        logging.info((ip, " added to the list."))
        global_get_external_ip.append(ip2)
        logging.info((ip2, " added to the list."))
        global_get_external_ip.append(ip3)
        logging.info((ip3, " added to the list."))

        return ip, ip2, ip3
    except:
        logging.error("Exception with getting the external IP.")
        return "Exception with getting the external IP."


def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        temp_local_ip = s.getsockname()[0]
        global_get_internal_ip.append(temp_local_ip)
        s.close()

        return temp_local_ip
    except:
        return "Exception with getting the internal IP."


if __name__ == "__main__":
    get_external_ip()
    get_local_ip()
    for items in global_get_external_ip:
        print("Ext IP:", items)
    print("Local IP:", global_get_internal_ip[-1])
