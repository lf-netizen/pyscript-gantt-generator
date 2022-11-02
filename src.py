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
        events = max(data['dst'])
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

        _, start = list(self.events.items())[0]
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

        _, end = list(self.events.items())[-1]
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
        _, start = list(self.events.items())[0]
        _, end = list(self.events.items())[-1]
        
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
        paths = self._make_paths()
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

        data['color'] = len(self.paths)
        for it, path in enumerate(self.paths):
            for i in range(len(path) - 1):
                src_id = list(self.event_ids.keys()) \
                        [list(self.event_ids.values()).index(path[i])]
                dst_id = list(self.event_ids.keys()) \
                        [list(self.event_ids.values()).index(path[i+1])]

                data.loc[np.logical_and(data['src'] == src_id, 
                                        data['dst'] == dst_id), 'color'] = it

        data.sort_values(by=['color', 'start'], inplace=True)

        fig, ax = plt.subplots(figsize=(12,6))
        ax.set_title('Gantt Chart', size=18)
        n_colors = max(data['color']) + 1
        color = iter(plt.cm.rainbow(np.linspace(0, 1, n_colors)))
        for i in range(n_colors):
            df = data[data['color']==i]
            ax.barh(y=df.name, left=df.start, width=df.duration,
                    alpha=1, color=next(color), zorder=2)
            if i < n_colors - 1:
                print('Ścieżka krytyczna nr {}'.format(i+1))
                print(df['name'].values)
        
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
    print('Całkowity czas przedsięwzięcia z prawdopodobieństwem 90% wyniesie \
nie więcej niż {}.'.format(ans))    
    print('Wariancja wyniosła {}.'.format(var))
    return p.plot(data)
    
def read_data():
    edges = js.document.getElementById("graph_iframe").contentWindow.edges.to_py()
    nodes_weights = js.document.getElementById('list_iframe').contentWindow.getInfo().to_py()
    if np.any([math.isnan(w) for w in nodes_weights]):
        return 'nan in time'
    nodes_weights = [0] + nodes_weights

    num_nodes = len(nodes_weights)
    graph_matrix = np.empty((num_nodes, num_nodes))
    graph_matrix[:] = np.nan

    for edge in edges:
        src = edge['from']['num']
        dst = edge['to']['num']
        graph_matrix[src, dst] = nodes_weights[dst]


    graph_isnan = np.isnan(graph_matrix)
    for i in range(1, num_nodes):
        if np.all(graph_isnan[:, i]):
            graph_matrix[0, i] = nodes_weights[i]
    print(graph_matrix)
    
    graph_isnan = np.isnan(graph_matrix)
    input_data = []
    for src in range(num_nodes):
        for dst in range(1, num_nodes):
            if graph_isnan[src, dst]:
                continue
            record = [str(dst)+'.', src, dst if not np.all(graph_isnan[dst, :]) else num_nodes] + 3 * [nodes_weights[dst]]
            input_data.append(record) 
    
    return np.array(input_data)
    # print(only_src, only_dst)



