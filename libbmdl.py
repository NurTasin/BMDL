#!/usr/bin/env python3
"""
libbmdl.py
Base Library For BMDL (Backup My Digital Life)
The Common Library for Using Both In Server Side and Client Side.
Note: There will always be a free version of BMDL

Author: Nur Mahmud Ul Alam Tasin (@nurtasin)
Version: 1.0.0 alpha
Date: 04 November 2021
License: MIT
"""
#======================imports=================

import socket
import requests
import os
import multiprocessing
import subprocess


#===================constants=======================
BMDL_SERVER_PORT=6942
BMDL_CLIENT_PORT=6943

#===================exceptions=====================
class LocalNetworkNotFound(Exception):
    """Exception Thrown If No Local Network Is Found"""

#====================functions======================

def getLocalIpAddress():
    """returns the local ip address of this device"""
    return socket.gethostbyname(socket.gethostname())


def __pinger(job_q, results_q):
    """pings device on the local network"""
    DEVNULL = open(os.devnull, 'w')
    while True:
        ip = job_q.get()
        if ip is None:
            break
        try:
            subprocess.check_call(['ping', '-c1', ip],stdout=DEVNULL)
            results_q.put(ip)
        except:
            pass



def __map_network(pool_size=255):
    """Scans the local device and returns all the device connected to it."""
    ip_list = list()
    ip_parts = getLocalIpAddress().split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
    jobs = multiprocessing.Queue()
    results = multiprocessing.Queue()
    pool = [multiprocessing.Process(target=__pinger, args=(jobs, results)) for i in range(pool_size)]
    for p in pool:
        p.start()
    for i in range(1, 255):
        jobs.put(base_ip + '{0}'.format(i))
    for p in pool:
        jobs.put(None)
    for p in pool:
        p.join()
    while not results.empty():
        ip = results.get()
        ip_list.append(ip)
    return ip_list


def getAvailableClients():
    """Scans the local network for BMDL clients and returns a list containing address and BMDL client name"""
    client_list=[]
    hosts_list=__map_network()
    for host in hosts_list:
        res=requests.get(f"{host}:{BMDL_CLIENT_PORT}",timeout=2)
        if res.status_code==200:
            client_list.append([host,res.json()["BMDL_Name"]])
    return client_list


def getAvailableClients():
    """Scans the local network for BMDL servers and returns a list containing address and BMDL client name"""
    client_list=[]
    hosts_list=__map_network()
    for host in hosts_list:
        res=requests.get(f"{host}:{BMDL_SERVER_PORT}",timeout=2)
        if res.status_code==200:
            client_list.append([host,res.json()["BMDL_Name"]])
    return client_list


if __name__=="__main__":
    print(getLocalIpAddress())
    print(getAvailableClients())