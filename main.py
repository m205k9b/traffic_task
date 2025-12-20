from IA import Incremental_Traffic_Assignment
from AON import All_or_Nothing_Traffic_Assignment
from load_data import get_demand, parse_network
from graph import get_graph, get_all_shortest_paths
from visualization import NetworkVisualizer
import networkx as nx
import traceback

if (__name__ == '__main__'):
    # 先导入节点和边，还有出行需求
    demand_path = 'json/demand.json'
    network_path = 'json/network.json'
    only_a_to_f_demand_path = 'json/demand_only_a_to_f.json'

    nodes, edges = parse_network(network_path)
    od_demand = get_demand(demand_path)
    nodes_names = sorted(list(nodes.keys()))

    print("1、不考虑拥堵，任意两点间的最快的路径是什么？")
    G: nx.DiGraph = get_graph(nodes, edges)
    paths = get_all_shortest_paths(G)
    
    for i in range(len(nodes_names)):
        for j in range(i + 1, len(nodes_names)):
            print(f"{nodes_names[i]} -> {nodes_names[j]} : {paths[nodes_names[i]][nodes_names[j]]}")

    print()

    print("2、假设各路段流量已知，考虑拥堵效应，任意两点之间的最快路径是什么？")
    print("以K=1000时IA的最终分配状态为例：")
    IA_dict = Incremental_Traffic_Assignment(nodes, edges, od_demand, K=1000)
    G = IA_dict['graph']
    link_travel_time = IA_dict['link_travel_time']

    # 更新G中每条边的通行时间
    for edge in edges:
        begin = edge['begin']
        end = edge['end']
        G[begin][end]['cost'] = link_travel_time[begin][end]
        G[end][begin]['cost'] = link_travel_time[end][begin]
    
    # 获得最短路径
    paths = get_all_shortest_paths(G)
    for i in range(len(nodes_names)):
        for j in range(i + 1, len(nodes_names)):
            print(f"{nodes_names[i]} -> {nodes_names[j]} : {paths[nodes_names[i]][nodes_names[j]]}")

    print()

    print("3、只考虑一个起迄点对的交通需求，例如A到F,各路段上的流量是多少？有多少被使用的路径？这些路径上的行程时间是否相等？")
    od_demand = get_demand(only_a_to_f_demand_path)
    print("1) 采用AON分配方法")
    AON_dict = All_or_Nothing_Traffic_Assignment(nodes, edges, od_demand)

    flow_AON = AON_dict['flow']
    for begin, end_dict in flow_AON.items():
        for end, Q in flow_AON[begin].items():
            print(f"{begin} -> {end}: Q = {Q:.2f}")

    # 可视化
    try:
        visualizer = NetworkVisualizer(AON_dict['graph'], nodes)
        visualizer.visualize_edge_flows(AON_dict['flow'], AON_dict['link_travel_times'], save_path='images/仅考虑A→F的AON分配.png', title="仅考虑A→F的AON分配流量分配")
    except Exception as e:
        print(f"图片导出失败: {e}")


    print("2) 采用IA分配方法，K=15")
    IA_dict = Incremental_Traffic_Assignment(nodes, edges, od_demand, 15)

    flow_IA = IA_dict['flow']
    for begin, end_dict in flow_IA.items():
        for end, Q in flow_IA[begin].items():
            if Q != 0:
                print(f"{begin} -> {end}: Q = {Q:.2f}")
    
    try:
        visualizer = NetworkVisualizer(IA_dict['graph'], nodes)
        visualizer.visualize_edge_flows(IA_dict['flow'], AON_dict['link_travel_times'], save_path='images/仅考虑A→F的IA分配 (K=15).png', title="仅考虑A→F的AON分配流量分配（K=15）")
    except Exception as e:
        print(f"图片导出失败: {e}")
        traceback.print_exc(e)

    print("3) 采用IA分配方法，K=1500")
    IA_dict = Incremental_Traffic_Assignment(nodes, edges, od_demand, 1500)

    flow_IA = IA_dict['flow']
    for begin, end_dict in flow_IA.items():
        for end, Q in flow_IA[begin].items():
            if Q != 0:
                print(f"{begin} -> {end}: Q = {Q:.2f}")
    
    try:
        visualizer = NetworkVisualizer(IA_dict['graph'], nodes)
        visualizer.visualize_edge_flows(IA_dict['flow'], AON_dict['link_travel_times'], save_path='images/仅考虑A→F的IA分配 (K=1500).png', title="仅考虑A→F的AON分配流量分配（K=1500）")
    except Exception as e:
        print(f"图片导出失败: {e}")
        traceback.print_exc(e)

    print()

    print("4、考虑所有起迄点对的交通需求，各路段的流量是多少，所有出行者的总行程时间是多少？")
    od_demand = get_demand(demand_path)
    print("1) 采用AON分配方法")
    AON_dict = All_or_Nothing_Traffic_Assignment(nodes, edges, od_demand)

    flow_AON = AON_dict['flow']
    for begin, end_dict in flow_AON.items():
        for end, Q in flow_AON[begin].items():
            print(f"{begin} -> {end}: Q = {Q:.2f}")

    # 可视化
    try:
        visualizer = NetworkVisualizer(AON_dict['graph'], nodes)
        visualizer.visualize_edge_flows(AON_dict['flow'], AON_dict['link_travel_times'], save_path='images/考虑所有OD对的AON分配.png', title="考虑所有OD对的AON分配流量分配")
    except Exception as e:
        print(f"图片导出失败: {e}")


    print("2) 采用IA分配方法，K=15")
    IA_dict = Incremental_Traffic_Assignment(nodes, edges, od_demand, 15)

    flow_IA = IA_dict['flow']
    for begin, end_dict in flow_IA.items():
        for end, Q in flow_IA[begin].items():
            if Q != 0:
                print(f"{begin} -> {end}: Q = {Q:.2f}")
    
    try:
        visualizer = NetworkVisualizer(IA_dict['graph'], nodes)
        visualizer.visualize_edge_flows(IA_dict['flow'], AON_dict['link_travel_times'], save_path='images/考虑所有OD对的IA分配 (K=15).png', title="考虑所有OD对的AON分配流量分配（K=15）")
    except Exception as e:
        print(f"图片导出失败: {e}")
        traceback.print_exc(e)

    print("3) 采用IA分配方法，K=1500")
    IA_dict = Incremental_Traffic_Assignment(nodes, edges, od_demand, 1500)

    flow_IA = IA_dict['flow']
    for begin, end_dict in flow_IA.items():
        for end, Q in flow_IA[begin].items():
            if Q != 0:
                print(f"{begin} -> {end}: Q = {Q:.2f}")
    
    try:
        visualizer = NetworkVisualizer(IA_dict['graph'], nodes)
        visualizer.visualize_edge_flows(IA_dict['flow'], AON_dict['link_travel_times'], save_path='images/考虑所有OD对的IA分配 (K=1500).png', title="考虑所有OD对的AON分配流量分配（K=1500）")
    except Exception as e:
        print(f"图片导出失败: {e}")
        traceback.print_exc(e)