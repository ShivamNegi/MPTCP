import os
import sys
import json
import itertools

from collections import defaultdict
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import OVSController
from mininet.node import Controller
from mininet.node import RemoteController
from mininet.cli import CLI
from time import sleep
from jellyfish import JellyFishTop
from fattree import FatTree


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b) 

def iperf_baseline(hosts):
    # runs flows from 1 host to another in isolation
    for client, server in pairwise(hosts):
        print "  getting baseline from %s to %s" % (client.name, server.name)
        for i in range(2):
            output_file = "iperf_baseline_%s_to_%s_%d.txt" % (
                client.name, server.name, i)
            server_cmd = "iperf -s -p %d &" % (5555)
            client_cmd = "iperf -c %s -p %d -t %d > %s &" % (server.IP(),
                5555, 5, output_file)
            
            print "    on %s running command: %s" % (server.name, server_cmd)
            server.sendCmd(server_cmd)
            # wait until command has executed
            server.waitOutput(verbose=True)
            print "    on %s running command: %s" % (client.name, client_cmd)
            client.sendCmd(client_cmd)
            client.waitOutput(verbose=True)

            try:
                # wait until processes are completely done
                # only a pair of hosts is tested at a time
                pid = int(client.cmd('echo $!'))
                client.cmd('wait', pid)
                server.cmd('kill -9 %iperf')
                server.cmd('wait')
            except:
                pass

def iperf_test(hosts, test_type, index=0):
    # host to pid of the iperf client process
    host_to_pid = {}
    for client, server in pairwise(hosts):
        print "  testing throughput from %s to %s" % (client.name, server.name)

        output_file = "iperf_%s_%s_to_%s_%d.txt" % (test_type,
            client.name, server.name, index)
        server_cmd = "iperf -s -p %d &" % (5555)
        client_cmd = "iperf -c %s -p %d %s -t %d > %s &" % (server.IP(),
            5555, ("-P 8" if test_type.endswith("8flow") else ""), 5, output_file)
        
        print "    on %s running command: %s" % (server.name, server_cmd)
        server.sendCmd(server_cmd)
        # wait until command has executed
        server.waitOutput(verbose=True)
        print "    on %s running command: %s" % (client.name, client_cmd)
        client.sendCmd(client_cmd)
        client.waitOutput(verbose=True)
        pid = int(client.cmd('echo $!'))
        host_to_pid[client] = pid

    print "Waiting for iperf tests to finish..."
    for host, pid in host_to_pid.iteritems():
        host.cmd('wait', pid)

    print "Killing all iperf instances..."
    # need to kill iperf instances so we can rerun these tests on the same mininet
    for client, server in pairwise(hosts):
        server.cmd( "kill -9 %iperf" )
        # Wait for iperf server to terminate
        server.cmd( "wait" )

def experiment_8shortest(net):
    print "Starting mininet..."
    net.start()
    # sleep to wait for switches to come up and connect to controller
    sleep(3)

    num_runs = 2

    # run tests to estimate link capacity
    print "Running tests to estimate link capacity"
    iperf_baseline(net.hosts)

    print "Starting k_shortest experiments"

    print "Running TCP 1-flow experiment on jellyfish"
    for i in range(0, num_runs):
        iperf_test(net.hosts, "shortest8_1flow", i)

    print "Running TCP 8-flow experiment on jellyfish"
    for i in range(0, num_runs):
        iperf_test(net.hosts, "shortest8_8flow", i)
    
    print "Done with k_shortest experiments"
    net.stop()

def experiment_ecmp(net):
    print "Starting ecmp experiments"
    net.start()
    # sleep to wait for switches to come up and connect to controller
    sleep(3)

    num_runs = 5
    
    print "Running TCP 1-flow experiment on jellyfish"
    for i in range(0, num_runs):
        iperf_test(net.hosts, "ecmp_1flow", i)

    '''
    print "Running TCP 8-flow experiment on jellyfish"
    for i in range(0, num_runs):
        iperf_test(net.hosts, "ecmp_8flow", i)
    '''
   
    print "Done with ecmp experiments"
    net.stop()

def call_cli(net):
    ''' Call Mininet Cmd line for testing the network '''
    net.start()
    sleep(100)
    CLI(net)
    net.stop()

TOPOS = {'JellyTopo' : (lambda : JellyFishTop()),
         'FatTree' : ( lambda k : FatTree(k))}

def main():
    # Initializing topology
    jelly_topo = JellyFishTop()
    fat_topo = FatTree(4)

    # Creating Mininet instance for the network
    jelly_net = Mininet(topo=jelly_topo, host=CPULimitedHost, link=TCLink)
    fat_net = Mininet(topo=fat_topo, host=CPULimitedHost, link=TCLink)

    call_cli(fat_net)
    # experiment_8shortest(fat_net)

if __name__ == "__main__":
    main()

