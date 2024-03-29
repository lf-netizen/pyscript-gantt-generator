import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict
import js
import math

class Activity:
    def __init__(self, i, j, tc, tm, tp):
        self.i = i
        self.j = j
        self.tc = tc
        self.tm = tm
        self.tp = tp
        self.t0 = (tc + 4 * tm + tp) / 6
        self.var = ((tp - tc) / 6) ** 2
        self.zc = None


class Event:
    def __init__(self, id) -> None:
        self.id =  id
        self.pre = []
        self.next = []
        
        self.tw = None
        self.tp = None

class PERT:

    def add_activity(self, t: Activity) -> None:
        if t.i not in self.events:
            self.events[t.i] = Event(t.i)
        if t.j not in self.events:
            self.events[t.j] = Event(t.j)

        p = self.events[t.i]
        n = self.events[t.j]
        p.next.append(n)
        n.pre.append(p)
        self.activities[(t.i, t.j)] = t

    def create_from_data(self, data: pd.DataFrame) -> None:
        events = max(data['dst'].max(), data['src'].max())
        m = np.zeros((events, events), dtype=int)
        for s, d in zip(data['src'], data['dst']):
            m[s-1][d-1] = 1

        self._renum(m)
        for _, _, src, dst, tc, tm, tp  in data.to_records():
            id_src = self.event_ids[src]
            id_dst = self.event_ids[dst]
            self.add_activity(Activity(id_src, id_dst, tc, tm, tp))

        

    @staticmethod
    def _find_next(m: np.array) -> int:
        for idx in range(m.shape[0]):
            if m[idx, idx] == -1:
                continue
            found = True
            for row in m:
                if row[idx] == -1:
                    continue
                if row[idx] == 1:
                    found = False
                    break 
            
            if found:
                return idx


    def _renum(self, m: np.array, id=1) -> None:
        if len(self.event_ids) == m.shape[0]:
            return None
        
        next = self._find_next(m)
        self.event_ids[next+1] = id
        m[next, :] = -1
        m[:, next] = -1
        self._renum(m, id+1)

    def __init__(self, data: pd.DataFrame) -> None:
        self.events = {}
        self.activities = {}
        self.event_ids = {}
        self.create_from_data(data)
        self.paths = []


    def _determine_min_terms(self) -> None:
        visited = set()

        start = [e for  _, e in list(self.events.items()) if not e.pre][0]
        start.tw = 0

        q = [start]

        while len(q) > 0:
            event = q.pop(0)

            def all_pre_visited():
                nonlocal event
                for pre in event.pre:
                    if pre not in visited:
                        return False
                return True

            if not all_pre_visited() or event in visited:
                continue   
            
            for next in event.next:
                q.append(next)
            
            event.tw = max([pre.tw + self.activities[(pre.id, event.id)].t0 \
                            for pre in event.pre], default=0)
            visited.add(event)

    def _determine_max_terms(self) -> None:
        visited = set()

        end = [e for  _, e in list(self.events.items()) if not e.next][0]
        end.tp = end.tw

        q = [end]

        while len(q) > 0:
            event = q.pop(0)

            def all_next_visited():
                nonlocal event
                for next in event.next:
                    if next not in visited:
                        return False
                return True

            if not all_next_visited() or event in visited:
                continue   
            
            for pre in event.pre:
                q.append(pre)
            
            event.tp = min([next.tp - self.activities[(event.id, next.id)].t0 
                                    for next in event.next], default=event.tp)
            visited.add(event)

            for next in event.next:
                activity = self.activities[(event.id, next.id)]
                activity.zc = next.tp - event.tw - activity.t0

    def _make_paths(self) -> List[List[int]]:
        start = [e for  _, e in list(self.events.items()) if not e.pre][0]
        end = [e for  _, e in list(self.events.items()) if not e.next][0]
        
        self.paths = self._make_paths_recur(start, end.id, [], self.activities)
        
    @staticmethod
    def _make_paths_recur(event, last_id, path, a):
        if last_id == event.id:
            path.append(event.id)
            return [path]

        paths = []
        for next in event.next:
            if np.abs(a[(event.id, next.id)].zc) <= 1E-14:
                paths += (PERT._make_paths_recur(next, last_id, \
                                                 path + [event.id], a))
        
        paths = list(filter(lambda el: el is not None, paths))
        if len(paths) == 0:
            return None
        return paths    

    def _get_total_var(self) -> float:
        var = 0
        self._make_paths()
        for path in self.paths:
            this_path_var = 0
            for i in range(len(path) - 1):
                this_path_var += self.activities[path[i], path[i+1]].var
            var = max(var, this_path_var)
            
        return var

    def _calculate(self) -> None:
        self._determine_min_terms()
        self._determine_max_terms()
        self._make_paths()

    def get_answer(self) -> float:
        self._calculate()
        var = self._get_total_var()
        _, end = list(self.events.items())[-1]
        return end.tp + 1.28 * var**0.5, var

    def plot(self, data: pd.DataFrame):
        start = []
        duration = []
        limit = []
        for s, d in zip(data['src'], data['dst']):
            s_id = self.event_ids[s]
            d_id = self.event_ids[d]
            a = self.activities[(s_id, d_id)]
            start.append(self.events[s_id].tw)
            duration.append(a.t0)
            limit.append(self.events[d_id].tp - self.events[s_id].tw - a.t0)
            

        data['start'] = start
        data['duration'] = duration
        data['limit'] = limit
        data = data[data['duration'] > 0].copy()
        
        data['color'] = len(self.paths)
        for it, path in enumerate(self.paths):
            for i in range(len(path) - 1):
                src_id = list(self.event_ids.keys()) \
                        [list(self.event_ids.values()).index(path[i])]
                dst_id = list(self.event_ids.keys()) \
                        [list(self.event_ids.values()).index(path[i+1])]

                data.loc[np.logical_and(data['src'] == src_id, 
                                        data['dst'] == dst_id), 'color'] = it

        fig, ax = plt.subplots(figsize=(12,6))
        ax.set_title('Gantt Chart', size=18)
        
        n_colors = max(data['color']) + 1
        colors = plt.cm.rainbow(np.linspace(0, 1, n_colors))
        data['color'] = data['color'].apply(lambda i: colors[i])
        ax.barh(y=data.name, left=data.start, width=data.duration,
                alpha=1, color=data.color, zorder=2)
        
        ax.barh(y=data.name, left=data.start+data.duration, width=data.limit, 
                alpha=0.3, color='black', height=0.5, zorder=2)
        ax.grid(axis='x', zorder=1)
        ax.set_xlabel('Time')
        plt.gca().invert_yaxis()
        return fig


def solve(data: pd.DataFrame):
    for col in ['src', 'dst', 'tc', 'tm', 'tp']:
        data[col] = pd.to_numeric(data[col])

    p = PERT(data)

    ans, var = p.get_answer()
    js.console.log('Całkowity czas przedsięwzięcia z prawdopodobieństwem 90% wyniesie \
nie więcej niż {}.'.format(ans))    
    js.console.log('Wariancja wyniosła {}.'.format(var))
    return p.plot(data)
    
def has_cycles(g):
    L = []
    S = []
    for i in range(1, g.shape[0]):
        if np.all(~g[:, i]):
            S.append(i)
    
    while len(S):
        n = S.pop(0)
        L.append(n)
        for m, has_edge in enumerate(g[n, :]):
            if not has_edge:
                continue
            g[n, m] = False
            if np.all(~g[:, m]):
                S.append(m)
    return not np.all(~g)


def read_data():
    graph = js.document.getElementById("graph_iframe").contentWindow.graph.to_py()
    edges = graph.edges
    
    task_info = js.document.getElementById('list_iframe').contentWindow.getInfo().to_py()
    nodes_weights = task_info['weights']
    nodes_labels = task_info['labels']
    if not nodes_weights:
        return 'graph is empty'
    if np.any([math.isnan(w) for w in nodes_weights]):
        return 'nan in time'
    nodes_weights = [0] + nodes_weights + [0]
    nodes_labels = [0] + nodes_labels + [0]

    num_nodes = len(nodes_weights)
    graph_matrix = np.empty((num_nodes-1, num_nodes), dtype=bool)
    graph_matrix[:] = False

    for edge in edges:
        src = edge.source.data.label 
        dst = edge.target.data.label
        if src and dst and src!= 'start' and dst != 'end':
            graph_matrix[src, dst] = True

    if has_cycles(graph_matrix.copy()):
        return 'graph has cycle(s)'

    for i in range(1, num_nodes-1):
        if np.all(~graph_matrix[:, i]):
            graph_matrix[0, i] = True
        if np.all(~graph_matrix[i, :]):
            graph_matrix[i, -1] = True
    
    input_data = []
    free_dst_idx = num_nodes + 1
    for dst in range(1, num_nodes):
        srcs = np.argwhere(graph_matrix[:, dst]).flatten()
        if len(srcs) > 1:
            for src in srcs:
                record = [dst, nodes_labels[dst], src+1, free_dst_idx+1] + 3 * [0]
                input_data.append(record)
            record = [dst, nodes_labels[dst], free_dst_idx+1, dst+1] + 3 * [nodes_weights[dst]]
            input_data.append(record)
            free_dst_idx += 1
        else:
            record = [dst, nodes_labels[dst], srcs[0]+1, dst+1] + 3 * [nodes_weights[dst]]
            input_data.append(record)
    
    output = pd.DataFrame(np.array(input_data), columns=['id', 'name', 'src', 'dst', 'tc', 'tm', 'tp'])
    output['id'] = output.id.astype('int')
    output.sort_values(by='id', inplace=True)
    output.drop(columns='id', inplace=True)
    return output



