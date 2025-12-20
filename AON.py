from graph import *
from load_data import *
from visualization import NetworkVisualizer
from calculate import *

def all_or_nothing_assignment(G: nx.digraph, od_demand, link_travel_times: Dict[str, Dict[str, float]]):
    """
    执行一次全有全无（AON）分配
    
    Args:
        nodes: 节点
        edges: 边
        od_demand: dict[(orig, dest)] = demand_value
        link_travel_times: 当前各 link 的行程时间（用于最短路计算）
    
    Returns:
        list[float]: 每条 link 上的分配流量 y[i]
    """
    y = {}

    for (orig, dest), demand_val in od_demand.items():
        if demand_val <= 0:
            continue
        path = get_shortest_path(G, orig, dest, link_travel_times)
        if path is None:
            print(f"Warning: No path from {orig} to {dest}")
            continue
        for i in range(len(path) - 1):
            # 遍历数组
            begin=path[i]
            end=path[i+1]
            
            if begin not in y:
                y[begin] = {}
            
            if end not in y[begin]:
                y[begin][end] = 0

            y[begin][end] += demand_val

    return y

def All_or_Nothing_Traffic_Assignment(nodes, edges, od_demand):
    """
    执行基于自由流时间的全有全无交通分配
    
    Returns:
        dict: {
            'flow': flow_vector,
            'total_travel_time': TTT,
            'graph': graph,
            'links': links,
            'pos': pos,
            'node_names': node_names
        }
    """
    G = get_graph(nodes, edges)
    link_travel_times = {}

    # 构建自由流行程时间
    for edge in edges:
        begin = edge['begin']
        end = edge['end']
        if begin not in link_travel_times:
            link_travel_times[begin] = {}
        if end not in link_travel_times:
            link_travel_times[end] = {}
        link_travel_times[begin][end] = edge['free_flow_time']
        link_travel_times[end][begin] = edge['free_flow_time']

    
    # 调用 AON 函数
    flow_aon = all_or_nothing_assignment(G, od_demand, link_travel_times)
    
    for edge in edges:
        edge_begin = edge['begin']
        edge_end = edge['end']
        link_travel_times[edge_begin][edge_end] = get_link_travel_time(flow_aon, edge, edge_begin, edge_end)
        link_travel_times[edge_end][edge_begin] = get_link_travel_time(flow_aon, edge, edge_end, edge_begin)

    print(link_travel_times)

    return {
        'nodes': nodes,
        'edges': edges,
        'flow': flow_aon,
        'link_travel_times': link_travel_times,
        'graph': G,
    }

if __name__ == '__main__':
    network_file='data/network.json'
    demand_file='data/demand.json'
    
    ## 获取边和节点数据
    nodes, edges = parse_network()
    demands = get_demand()

    dict1 = All_or_Nothing_Traffic_Assignment(nodes, edges, demands)

    visualizer = NetworkVisualizer(dict1['graph'], nodes)
    visualizer.visualize_edge_flows(dict1['flow'], dict1['link_travel_times'])