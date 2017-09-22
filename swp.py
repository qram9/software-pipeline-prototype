#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#Comment: meant to be a top-level file. Do python swp.py to run.

from dep import Dep,Scoreboard

def setup_example_fig5():
    G = Dep('Fig5')
    for k in 'a','b','c','d','e':
        G.Nodes.append(k)
    G.Latency = {}
    for k in G.Nodes:
        G.Latency[k] = 1
    edges =[('a','b'),('b','e'),('a','c'),('c','e'),\
            ('b','e'),('a','d'),('d','e')]
    dist = []
    for k in edges:
        dist.append(0)
    G.do_init_work(edges,dist)
    print '-------------------------------------'
    print G
    print '-------------------------------------'
    with open('digraph_fig5.dot','w') as file:
        file.write(G.dot_graph())

def setup_example_fig1():
    while True:
        G = Dep('Fig1')
        G.Latency = {}
        for k in range(1,13):
            G.Nodes.append('n'+str(k))
            if k != 7:
                G.Latency['n'+str(k)] = 2
            else:
                G.Latency['n7'] = 1
        edges =[('n1','n3'),('n1','n5'),('n1','n6'),\
                ('n3','n4'),('n4','n7'),('n5','n8'),\
                ('n8','n10'),('n10','n11'),('n11','n12'),\
                ('n2','n8'),('n9','n10'),('n6','n11'),\
                ('n1','n4')]
        dist = []
        for k in edges:
            dist.append(0)        
        G.do_init_work(edges,dist)
        print '-------------------------------------'
        print G
        G.dot_graph()
        with open('digraph_fig1.dot','w') as file:
            file.write(G.dot_graph())
        G.typeof['n1'] = 'LdSt'
        G.typeof['n2'] = 'LdSt'
        G.typeof['n9'] = 'LdSt'
        G.typeof['n7'] = 'LdSt'
        G.typeof['n12'] = 'LdSt'
        G.typeof['n4'] = 'Mpy'
        G.typeof['n6'] = 'Mpy'
        G.typeof['n8'] = 'Mpy'
        G.typeof['n11'] = 'Mpy'
        for k in G.Nodes:
            if k not in G.typeof:
                G.typeof[k] = 'Alu'
        O = []
        G.Order([k for k in G.Nodes],O)
        G.MII = 4
        S = Scoreboard(1,1,2,G.MII)
        myO = [k for k in O]
        G.Early_Startu = {}
        G.Late_Startu = {}
        if G.schedule(myO,S) == True:
            print 'Order:', '<'+','.join(O)+'>'
            print S
            print '-------------------------------------'
            break
        G.MII += 1

def setup_example_fig7():
    G = Dep('Fig7')
    G.Latency = {}
    for k in 'ABCDEFGHIJKLM':
        G.Nodes.append(k)
        G.typeof[k] = 'Alu'
    for k in G.Nodes:
        G.Latency[k] = 2
    edges = ('AC','CF','DF','FA','AD','BD',
             'BE','DG','GJ','JM','FI','IL',
             'IG','IM','EH','HK','HJ')
    dist = []
    for k in edges:
        if k == 'FA': dist.append(1)
        elif k == 'IG' : dist.append(1)
        else: dist.append(0)
    roots = ['A']
    G.do_init_work(edges,dist,roots)
    print '-------------------------------------'
    print G
    with open('digraph_fig7.dot','w') as file:
        file.write(G.dot_graph())
    O = []
    G.Order(['A','C','D','F'],O)
    G.Order(['G','J','M','I'],O)
    G.Order(['B','E','H','K','L'],O)
    G.MII = 6
    while True:
        S = Scoreboard(4,4,4,G.MII)
        myO = [k for k in O]
        G.Early_Startu = {}
        G.Late_Startu = {}
        if G.schedule(myO,S) == True:
            print 'Order:', '<'+','.join(O)+'>'
            print S
            break
        G.MII += 1

if __name__ == '__main__':
    setup_example_fig1()
    setup_example_fig7()
    setup_example_fig5()
