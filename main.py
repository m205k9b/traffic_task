from IA import example_ia_network
from load_data import load_data, get_demand, parse_network
from graph import get_graph, get_shortest_path, get_all_shortest_paths
import networkx as nx

if (__name__ == '__main__'):
    # 先导入节点和边
    nodes, edges = parse_network()
    nodes_names = sorted(list(nodes.keys()))

    print("1、不考虑拥堵，任意两点间的最快的路径是什么？")
    G: nx.DiGraph = get_graph(nodes, edges)
    paths = get_all_shortest_paths(G)
    
    for i in range(len(nodes_names)):
        for j in range(i + 1, len(nodes_names)):
            print(f"{nodes_names[i]} -> {nodes_names[j]} : {paths[nodes_names[i]][nodes_names[j]]}")

    print()

    print("2、假设各路段流量已知，考虑拥堵效应，任意两点之间的最快路径是什么？")
    