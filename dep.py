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

# Some comments:
# Results in the schedules as required by the paper
# SCC detection etc need to be done by hand now.
# At some point to introduce a more sophisticated Scoreboard so that non-pipelined units can be
# handled properly etc.
# Should work with python if tabulate is available. If tabulate is not available comment out.
class Bundle(object):
    def __init__(self,slots=4):
        self.bundle = []
        self.max_bundle_size = slots
    def add_to_bundle(self,n,it):
        self.bundle.append(n)
        if len(self.bundle) > self.max_bundle_size:
            raise Exception
    def has_free_slot(self):
        if len(self.bundle) < self.max_bundle_size:
            return True
        else:
            return False
    def __str__(self):
        def add_str(a,b):
            ret = ''
            if a == '':
                ret += b
            elif b != '':
                ret += a + ',' + b
            return ret
        ret = ''
        for k in self.bundle:
            ret = add_str(ret,k)
        return ret

class Scoreboard(object):
    ''' The scoreboard can be made more sophisticated to 
be able to handle non-pipelined units, other stuff'''
    def __init__(self,Alu,Mpy,LdSt,MII):
        self.Alu = Alu
        self.LdSt = LdSt
        self.Mpy = Mpy
        self.Phi = 1500
        self.Scalar = 1
        self.Scheduled = {}
        self.Table = {}
        self.Bundles = {}
        self.cycles = []
        self.pschedule = {}
        self.MII = MII

    def check_typ(self,typ):
        if typ not in ('Alu','LdSt','Mpy', 'Scalar', 'Phi'):
            raise Exception

    def can_sched_at_cycle(self,cyc,typ):
        self.check_typ(typ)
        mod = cyc % self.MII
        if mod in self.Table:
            di = self.Table[mod]
            if di[typ] == getattr(self,typ):
                return False
            else:
                if mod not in self.Bundles:
                    return True
                if self.Bundles[mod].has_free_slot():
                    return True
                else:
                    return False
        else:
            return True
    def sched_at_cycle(self,cyc,typ,n):
        self.check_typ(typ)
        mod = cyc % self.MII
        if mod in self.Table:
            di = self.Table[mod]
            if di[typ] == getattr(self,typ):
                raise Exception
            else:
                di[typ] = di[typ] + 1
        else:
            self.Table[mod] = {'Alu' : 0,
                    'Scalar' : 0,
                    'LdSt' : 0,
                    'Mpy' : 0,
                    'Phi' : 0}
            self.Table[mod][typ] = 1
            self.cycles.append(mod)
            self.Bundles[mod] = Bundle()
            self.Scheduled[mod] = \
                    {'Alu' : [], 'Scalar' : [],
                     'LdSt' : [], 'Mpy' : [], 'Phi' : []}
        self.Bundles[mod].add_to_bundle(n,cyc)
        self.Scheduled[mod][typ].append(n)
    def __str__(self):
        ret = ''
        mycyc = [l for l in self.cycles]
        mycyc.sort()
        for k in mycyc:
            ret += 'At cycle:' + str(k) + '\n ' + ' Fu:'\
                    + str(self.Table[k]) + '\n ' + 'Bundles:'\
                    + str(self.Bundles[k])+ '\n}\n'
        return ret

class Dep(object):
    def __init__(self,Name='namen'):
        self.Pred = {}
        self.Succ = {}
        self.Nodes = []
        self.Latency = {}
        self.Anti = {}
        self.Distance = {}
        self.ASAPu = {}
        self.ALAPu = {}
        self.MOVu = {}
        self.Du = {}
        self.Hu = {}
        self.MII = 0
        self.MaxASAP = 0
        self.Name=Name
        self.typeof = {}
    def __str__(self):
        ret = ''
        for n in self.Nodes:
            ret += 'Node:'+ n + ' ASAP='+str(self.ASAPu[n])+\
                    ' ALAP='+str(self.ALAPu[n])+' Mov='+str(self.MOVu[n])+\
                    ' DEPTH='+str(self.Du[n])+' HEIGHT='+str(self.Hu[n])+'\n'
        return ret
    def dot_graph(self):
        def do_node_lab(self):
            ret = ''
            for k in self.Nodes:
                ret += '"'+k+'" '+'[shape=box label="' + k\
                       + '\\nASAP=' + str(self.ASAPu[k])+'\\nALAP='+str(self.ALAPu[k])\
                       +'\\nM='+str(self.MOVu[k])\
                       + '\\nD='+str(self.Du[k])+'\\nH='+str(self.Hu[k])\
                       +'"];\n'
            return ret
        ret = 'digraph G {\n'
        ret += do_node_lab(self)
        for k,edge in self.Succ.items():
            for e in edge:
                if k in self.Anti:
                    ret += '\"' + k + '\" -> ' + '\"'\
                           + e + '\" [color=red,style=dashed];\n'
                    continue
                ret += '\"' + k + '\" -> ' + '\"' + e + '";\n'
        ret += '}'
        return ret
    def add_edge(self,u,v):
        if u not in self.Nodes:
            print(u+' not in self.Nodes')
            raise Exception
        if v not in self.Nodes:
            print(v+' not in self.Nodes')
            raise Exception
        if v in self.Pred:
            self.Pred[v].add(u)
        else:
            self.Pred[v] = set()
            self.Pred[v].add(u)
        if u in self.Succ:
            self.Succ[u].add(v)    
        else:
            self.Succ[u] = set()
            self.Succ[u].add(v)

    def dfs_impl(self,x):
        self.visited.add(x)
        if x in self.Succ:
            for y in self.Succ[x]:
                if y not in self.visited:
                    self.dfs_impl(y)
        self.post_order.append(x)
    def do_dfs(self,roots=[]):
        self.roots = [r for r in roots]
        self.visited = set()
        self.post_order = []
        for k in self.Nodes:
            if k not in self.Pred:
                self.roots.append(k)
        for r in self.roots:
            if r not in self.visited:
                self.dfs_impl(r)
        self.rpo = [k for k in self.post_order]
        self.rpo.reverse()
        #print("RPO is:", self.rpo)
    def do_asap(self):
        for u in self.Nodes:
            self.ASAPu[u]= 0
        self.MaxASAP = 0
        for u in self.rpo:
            if u in self.Pred:
                for v in self.Pred[u]:
                    if self.Distance[(v,u)] != 0: continue
                    self.ASAPu[u] = max(self.ASAPu[u],self.ASAPu[v]+self.Latency[v])
                if self.MaxASAP < self.ASAPu[u]:
                    self.MaxASAP = self.ASAPu[u]
            self.Du[u] = self.ASAPu[u]
    def do_alap(self):
        for u in self.post_order:
            self.ALAPu[u] = self.MaxASAP
            self.Hu[u] = 0
            if u in self.Succ:
                for v in self.Succ[u]:
                    if self.Distance[(u,v)] != 0: continue
                    self.ALAPu[u] = min(self.ALAPu[u],self.ALAPu[v] - self.Latency[u])
                    self.Hu[u] = max(self.Hu[u],self.Hu[v]+self.Latency[u])

    def do_init_work(self,edges,dist,roots=[]):
        ii = 0
        for u,v in edges:
            self.add_edge(u,v)
            self.Distance[(u,v)] = dist[ii]
            ii+=1
        self.do_dfs(roots)
        self.do_asap()
        self.do_alap()
        for k in self.Nodes:
            self.MOVu[k] = self.ALAPu[k] - self.ASAPu[k]

        self.MII = self.MaxASAP + 2 -1
    def Pred_L(self,O):
        ret = []
        for k in O:
            if k in self.Pred:
                ret.extend(self.Pred[k])
        pred_L = set()
        for k in ret:
            if k not in O:
                pred_L.add(k)
        return pred_L
    def Succ_L(self,O):
        ret = []
        for k in O:
            if k in self.Succ:
                ret.extend(self.Succ[k])
        succ_L = set()
        for k in ret:
            if k not in O:
                succ_L.add(k)
        return succ_L
    def Order(self,S,O):
        P_L = self.Pred_L(O)
        S_L = self.Succ_L(O)
        if len(P_L) > 0 and P_L.issubset(S):
            R = P_L.intersection(S)
            order = 'bottom-up'
        elif len(S_L) > 0 and S_L.issubset(S):
            R = S_L.intersection(S)
            order = 'top-down'
        else:
            maxasap = -199
            item = S[0]
            for u in S:
                if self.ASAPu[u] > maxasap:
                    item = u
                    maxasap = self.ASAPu[u]
            R = set()
            R.add(item)
            order = 'bottom-up'
        while True:
            if order == 'top-down':
                while len(R) > 0:
                    hi = []
                    max_h = -199;
                    for v in R:
                        if self.Hu[v] > max_h:
                            max_h = self.Hu[v]
                    min_mov = 10000
                    for v in R:
                        if self.Hu[v] == max_h:
                            if self.MOVu[v] < min_mov:
                                choice = v
                                min_mov = self.MOVu[v]
                    O.append(choice)
                    vset = set()
                    vset.add(choice)
                    R = R.difference(vset)
                    if choice in self.Succ:
                        K = set()
                        s = set()
                        for ii in self.Succ[choice]:
                            if ii not in O:
                                s.add(ii)
                        K = K.union(s)
                        K = K.intersection(S)
                        R = R.union(K)
                order = 'bottom-up'
                R = set()
                R = R.union(self.Pred_L(O))
                R = R.intersection(S)
            else:
                while len(R) > 0:
                    max_dv = -199;
                    for v in R:
                        if self.Du[v] > max_dv:
                            max_dv = self.Du[v]
                            choice = v
                    min_mov = 10000
                    for v in R:
                        if self.Du[v] == max_dv:
                            if self.MOVu[v] < min_mov:
                                choice = v
                                min_mov = self.MOVu[v]
                    O.append(choice)
                    vset = set()
                    vset.add(choice)
                    R = R.difference(vset)
                    if choice in self.Pred:
                        K = set()
                        p = set()
                        for ii in self.Pred[choice]:
                            if ii not in O:
                                p.add(ii)
                        K = K.union(p)
                        K = K.intersection(S)
                        R = R.union(K)
                order = 'top-down'
                R = set()
                R = R.union(self.Succ_L(O))
                R = R.intersection(S)
            if len(R) == 0:
                break
        #print("Order is:",O)
    def pred_in_psched(self,op,sched):
        if op in self.Pred:
            for k in self.Pred[op]:
                if k in sched:
                    return True
        return False
    def succ_in_psched(self,op,sched):
        if op in self.Succ:
            for k in self.Succ[op]:
                if k in sched:
                    return True
        return False
    def do_early_pred(self,op,sched):
        if op in self.Pred:
            alis = []
            for v in self.Pred[op]:
                if v in sched:
                    tv = sched[v]
                    lat_op = self.Latency[v]
                    dist_op = self.Distance[(v,op)] *self.MII
                    alis.append(tv+lat_op-dist_op)
            return max(alis)
        return 0
    def do_late_succ(self,op,sched):
        if op in self.Succ:
            alis = []
            #print op+' has :',
            for v in self.Succ[op]:
                if v in sched:
                    tv = sched[v]
                    lat_op = self.Latency[v]
                    dist_op = self.Distance[(op,v)] *self.MII
                    alis.append(tv-lat_op+dist_op)
            #        print v,
            return min(alis)
        return 0
    def scan(self,e,l,inc,typ,op,S):
        scheduled = False
        for k in range(e,l,inc):
            if S.can_sched_at_cycle(k,typ):
                S.pschedule[op] = k
                S.sched_at_cycle(k,typ,op)
                scheduled=True
                break
            #else:
            #    print(op,"does not go in:",k)
        if not scheduled:
            print ('Failed to schedule:' + op,typ)
            return False
        return True

    def schedule(self,O,S):
        psched = S.pschedule
        while len(O) > 0:
            op = O.pop(0)
            has_pred = self.pred_in_psched(op,psched)
            has_succ = self.succ_in_psched(op,psched)
            typ = self.typeof[op]
            if has_pred and has_succ:
                self.Early_Startu[op] = self.do_early_pred(op,psched)
                self.Late_Startu[op] = self.do_late_succ(op,psched)
                if self.Late_Startu[op] <= self.Early_Startu[op] + self.MII:
                    starti = self.Early_Startu[op]
                    endi = min(self.Early_Startu[op]+self.MII, self.Late_Startu[op]+1)
                    step = 1
                else:
                    raise Exception
            elif has_pred:
                self.Early_Startu[op] = self.do_early_pred(op,psched)
                starti = self.Early_Startu[op]
                endi = starti + self.MII
                step = 1
                #print('pred-only, scan from',starti,endi,op)
            elif has_succ:
                self.Late_Startu[op] = self.do_late_succ(op,psched)
                starti = self.Late_Startu[op]
                endi = starti - self.MII
                step = -1
                #print("succ-only, scan from",starti,endi,op)
            else:
                self.Early_Startu[op] = self.ASAPu[op]
                starti = self.Early_Startu[op]
                endi = starti + self.MII 
                step = 1
                #print('has neither, scan from',starti,endi,op)
            self.scan(starti,endi,step,typ,op,S)
            if op not in psched:
                #print("failing for:",op)
                return False
            #print (op,' goes to:',psched[op])

        return True
