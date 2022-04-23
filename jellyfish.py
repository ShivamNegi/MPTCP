from mininet.topo import Topo
import json

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

class JellyFishTop(Topo):
    ''' Builds topology '''
    def build(self):
        self.build_from_json()

    ''' Builds topology from given json file of graph adjacency list'''
    def build_from_json(self, filename='./data/graph.json'):
        with open(filename, 'r') as fp:
            adj_dict = byteify(json.load(fp))

            # Create Switches and hosts
            for node, neighbors in adj_dict.iteritems():
                number = node[1:]
                
                if 's' in node:
                    switch_ip = "10.0.0.%s" % number
                    s = self.addSwitch(node, ip=switch_ip, stp=True, failMode='standalone')
                else:
                    host_ip = "10.1.%s.0" % number
                    h = self.addHost(node, ip=host_ip)


            for node, neighbors in adj_dict.iteritems():
                for neighbor in neighbors:
                    opts = { 'bw': .1}
                    self.addLink(node, neighbor, opts=opts)

