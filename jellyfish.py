#!/usr/bin/env python

class JellyFishTop(Topo):
    ''' Builds topology '''
    def build(self):
        self.build_from_json()
        #self.build_from_algorithm()

    ''' Builds topology from given json file of graph adjacency list'''
    def build_from_json(self, filename='graph.json'):
        with open(filename, 'r') as fp:
            adj_dict = byteify(json.load(fp))
            
            linkopts = dict(bw=1)

            # add all switches. The first port will always connect to a host.
            for node in adj_dict.keys():
                switch_ip = ip="10.0.0.%s" % node
                s = self.addSwitch('s' + str(node))

            # connect every switch to a host. Each connection is on sequentially allocated
            # ports each starting at 2. 
            for node in adj_dict.keys():
                s = 's' + node
                host_ip = "10.1.%s.0" % node
                h = self.addHost('h' + node, ip=host_ip)
                self.addLink(h, s, port1=1025, port2=1)
                # self.addLink(h, s)

            # connect switches to each other
            connected_switches = set()
            for node, neighbors in adj_dict.iteritems():
                s = 's' + node
                for i in neighbors:
                    n = 's' + str(i)
                    if (s, n) not in connected_switches \
                            and (n, s) not in connected_switches:

                        opts = { 'bw': .1}
                        self.addLink(s, n, port1=int(i)+2, port2=int(node)+2, opts=opts)
                        # self.addLink(s, n)
                        connected_switches.add((s, n))

    ''' Builds topology from algorithm described in paper '''
    def build_from_algorithm(self, nswitches=3, nhosts=3, k=3, r=1):
        nPortsUsed = defaultdict(int) # switch => num ports that have been connected to a link
        switches = [self.addSwitch('s' + str(i), ip="10.0.0.%d" % i) for i in range(nswitches)]
        hosts = [self.addHost('h' + str(i), ip="10.1.%d.0" % i, mac="00:00:00:%0.2X:00:00" % i) for i in range(nhosts)]

        # Dict of vertices to the list of vertices they connect to; this is a graph adjacency list.
        # We ulitamtely output this representation of the graph in json, so another script can
        # compute edge popularity among paths.
        adj_list = {}

        # Connect each host to one switch
        for h in hosts:
            while True:
                s = random.choice(switches)
                nPorts = nPortsUsed[s]
                if r - nPorts > 0:
                    self.addLink(h, s)
                    # Add links to graph adjacency list
                    self.update_adj_list(adj_list, h ,s)
                    self.update_adj_list(adj_list, s, h)
                    nPortsUsed[s] = nPorts + 1
                    # print h, "is connected to", s
                    break

        # Connect switches to each other
        linkPairs = set()

        switchPairs = []
        for idx, s1 in enumerate(switches):
            for idx2 in range(idx + 1, len(switches)):
                switchPairs.append((s1, switches[idx2]))

        # random.shuffle(switchPairs)
        for s1, s2 in switchPairs:
            if nPortsUsed[s1] < k and nPortsUsed[s2] < k:
                self.addLink(s1, s2)
                # Add links to graph adjacency list
                self.update_adj_list(adj_list, s1, s2)
                self.update_adj_list(adj_list, s2, s1)
                # print s1, "is connected to", s2
                nPortsUsed[s1] += 1
                nPortsUsed[s2] += 1

        # Output adjacency list in json format into temp file.
        # with open('jellyfish_graph_adj_list.json', 'w') as fp:
            # json.dump(adj_list, fp)

    def update_adj_list(self, adj_list, v1, v2):
        adj_list.setdefault(v1, [])
        adj_list[v1].append(v2)

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Link, Intf, TCLink
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
import logging
import os 

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger( __name__ )

class HugeTopo(Topo):
    logger.debug("Class HugeTopo")
    CoreSwitchList = []
    AggSwitchList = []
    EdgeSwitchList = []
    HostList = []
    iNUMBER = 0
    def __init__(self):
        logger.debug("Class HugeTopo init")
        iNUMBER = 4
        
        self.iNUMBER = iNUMBER
        self.iCoreLayerSwitch = iNUMBER
        self.iAggLayerSwitch = iNUMBER * 2
        self.iEdgeLayerSwitch = iNUMBER * 2
        self.iHost = self.iEdgeLayerSwitch * 2 
    
    
        #Init Topo
        Topo.__init__(self)

    def createTopo(self):    
        logger.debug("Start create Core Layer Swich")
        self.createCoreLayerSwitch(self.iCoreLayerSwitch)
        logger.debug("Start create Agg Layer Swich ")
        self.createAggLayerSwitch(self.iAggLayerSwitch)
        logger.debug("Start create Edge Layer Swich ")
        self.createEdgeLayerSwitch(self.iEdgeLayerSwitch)
        logger.debug("Start create Host")
        self.createHost(self.iHost)

    """
    Create Switch and Host
    """

    def createCoreLayerSwitch(self, NUMBER):
        logger.debug("Create Core Layer")
        for x in range(1, NUMBER+1):
            PREFIX = "100"
            if x >= int(10):
                PREFIX = "10"
            self.CoreSwitchList.append(self.addSwitch(PREFIX + str(x)))

    def createAggLayerSwitch(self, NUMBER):
        logger.debug( "Create Agg Layer")
        for x in range(1, NUMBER+1):
            PREFIX = "200"
            if x >= int(10):
                PREFIX = "20"
            self.AggSwitchList.append(self.addSwitch(PREFIX + str(x)))

    def createEdgeLayerSwitch(self, NUMBER):
        logger.debug("Create Edge Layer")
        for x in range(1, NUMBER+1):
            PREFIX = "300"
            if x >= int(10):
                PREFIX = "30"
            self.EdgeSwitchList.append(self.addSwitch(PREFIX + str(x)))
    
    def createHost(self, NUMBER):
        logger.debug("Create Host")
        for x in range(1, NUMBER+1):
            PREFIX = "400"
            if x >= int(10):
                PREFIX = "40"
            self.HostList.append(self.addHost(PREFIX + str(x))) 

    """
    Create Link 
    """
    def createLink(self):
        logger.debug("Create Core to Agg")
        for x in range(0, self.iAggLayerSwitch, 2):
            self.addLink(self.CoreSwitchList[0], self.AggSwitchList[x], bw=1000, loss=5)
            self.addLink(self.CoreSwitchList[1], self.AggSwitchList[x], bw=1000, loss=5)
        for x in range(1, self.iAggLayerSwitch, 2):
            self.addLink(self.CoreSwitchList[2], self.AggSwitchList[x], bw=1000, loss=5)
            self.addLink(self.CoreSwitchList[3], self.AggSwitchList[x], bw=1000, loss=5)
        
        logger.debug("Create Agg to Edge")
        for x in range(0, self.iAggLayerSwitch, 2):
            self.addLink(self.AggSwitchList[x], self.EdgeSwitchList[x], bw=100)
            self.addLink(self.AggSwitchList[x], self.EdgeSwitchList[x+1], bw=100)
            self.addLink(self.AggSwitchList[x+1], self.EdgeSwitchList[x], bw=100)
            self.addLink(self.AggSwitchList[x+1], self.EdgeSwitchList[x+1], bw=100)

        logger.debug("Create Edge to Host")
        for x in range(0, self.iEdgeLayerSwitch):
            ## limit = 2 * x + 1 
            self.addLink(self.EdgeSwitchList[x], self.HostList[2 * x])
            self.addLink(self.EdgeSwitchList[x], self.HostList[2 * x + 1])

def enableSTP():
    """
    //HATE: Dirty Code
    """
    for x in range(1,5):
        cmd = "ovs-vsctl set Bridge %s stp_enable=true" % ("100" + str(x))
        os.system(cmd)
        print cmd 

    for x in range(1, 9):
        cmd = "ovs-vsctl set Bridge %s stp_enable=true" % ("200" + str(x))
        os.system(cmd)  
        print cmd 
        cmd = "ovs-vsctl set Bridge %s stp_enable=true" % ("300" + str(x))
        os.system(cmd)
        print cmd

def iperfTest(net, topo):
    logger.debug("Start iperfTEST")
    h1000, h1015, h1016 = net.get(topo.HostList[0], topo.HostList[14], topo.HostList[15])
    
    #iperf Server
    h1000.popen('iperf -s -u -i 1 > iperf_server_differentPod_result', shell=True)

    #iperf Server
    h1015.popen('iperf -s -u -i 1 > iperf_server_samePod_result', shell=True)

    #iperf Client
    h1016.cmdPrint('iperf -c ' + h1000.IP() + ' -u -t 10 -i 1 -b 100m')
    h1016.cmdPrint('iperf -c ' + h1015.IP() + ' -u -t 10 -i 1 -b 100m')

def pingTest(net):
    logger.debug("Start Test all network")
    net.pingAll()

def createTopo():
    logging.debug("LV1 Create HugeTopo")
    topo = HugeTopo()
    topo.createTopo() 
    topo.createLink() 
    
    logging.debug("LV1 Start Mininet")
    CONTROLLER_IP = "127.0.0.1"
    CONTROLLER_PORT = 6633
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.addController( 'controller',controller=RemoteController,ip=CONTROLLER_IP,port=CONTROLLER_PORT)
    net.start()

    logger.debug("LV1 dumpNode")
    enableSTP()
    dumpNodeConnections(net.hosts)
    
    pingTest(net)
    iperfTest(net, topo)
    

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    if os.getuid() != 0:
        logger.debug("You are NOT root")
    elif os.getuid() == 0:
        createTopo()

