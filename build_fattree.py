from mininet.topo import Topo

class FatTree(Topo):
    ''' Builds topology '''
    def build(self):
        self.build_from_json()

    ''' Builds topology from given json file of graph adjacency list'''
    def build_from_json(self, filename='fattree_graph.json'):
        with open(filename, 'r') as fp:
            adj_dict = byteify(json.load(fp))
            
            linkopts = dict(bw=1)

            # add all switches. The first port will always connect to a host.
            for node in adj_dict.keys():
                switch_ip = ip = "10.0.0.%s" % node
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

def main():
    pass

if __name__ == "__main__":
    main()

