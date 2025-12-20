from AON import *
from graph import *
from calculate import *
from visualization import *

def Incremental_Traffic_Assignment(nodes, edges, od_demand,
    K=1000
):
    """
    执行增量交通分配（Incremental Assignment）
    
    Args:
        K: 将总需求分成 K 份逐步分配
    
    Returns:
        dict: {
            'flow': x,
            'total_travel_time': TTT,
            'K': K,
            'graph': graph,
            'links': links,
            'pos': pos,
            'node_names': node_names
        }
    """

    step_demand = {od: amt / K for od, amt in od_demand.items()}

    G = get_graph(nodes, edges)
    x = {} # 流量全是0
    link_travel_times = {} # 自由流时间
    for node in nodes:
        if node not in x: x[node] = {}
        for node1 in nodes:
            x[node][node1] = 0

    for edge in edges:
        begin = edge['begin']
        end = edge['end']
        if begin not in link_travel_times:
            link_travel_times[begin] = {}
        if end not in link_travel_times:
            link_travel_times[end] = {}
        link_travel_times[begin][end] = edge['free_flow_time']
        link_travel_times[end][begin] = edge['free_flow_time']

    for k in range(1, K + 1):
        # 获取当前行程时间列表
        t_current = {}
        for node in nodes:
            t_current[node] = {}
        for edge in edges:
            begin = edge['begin']
            end = edge['end']
            t_current[begin][end] = get_link_travel_time(x, edge, begin, end)
            t_current[end][begin] = get_link_travel_time(x, edge, end, begin)
        # 执行 AON 分配当前 step_demand 
        y_k = all_or_nothing_assignment(G, step_demand, t_current)
        for edge in edges:
            begin = edge['begin']
            end = edge['end']
            if begin in y_k and end in y_k[begin]:
                x[begin][end] += y_k[begin][end]
            if end in y_k and begin in y_k[end]:
                x[end][begin] += y_k[end][begin]


    for edge in edges:
        begin = edge['begin']
        end = edge['end']
        link_travel_times[begin][end] = get_link_travel_time(x, edge, begin, end)
        link_travel_times[end][begin] = get_link_travel_time(x, edge, end, begin)

    return {
        'nodes': nodes,
        'edges': edges,
        'flow': x,
        'link_travel_time': link_travel_times,
        'K': K,
        'graph': G,
    }

if __name__ == '__main__':
    network_file='data/network.json'
    demand_file='data/demand.json'
    
    ## 获取边和节点数据
    nodes, edges = parse_network(network_file)
    demands = get_demand(demand_file)

    dict1 = Incremental_Traffic_Assignment(nodes, edges, demands, K=1000)
    
    visualizer = NetworkVisualizer(dict1['graph'], nodes)
    visualizer.visualize_edge_flows(dict1['flow'], dict1['link_travel_time'])