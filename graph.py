import networkx as nx
from typing import *
from load_data import parse_network

def get_graph(nodes: Dict, edges: Dict) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_nodes_from(nodes.keys())
    for edge in edges:
        G.add_edge(edge['begin'], edge['end'], cost=edge['free_flow_time'], capacity=edge['capacity'], flow=0)
        # 注释掉反向边，避免可视化混乱（如需双向网络可保留）
        G.add_edge(edge['end'], edge['begin'], cost=edge['free_flow_time'], capacity=edge['capacity'], flow=0)
    return G

def get_shortest_path(G: nx.DiGraph, source: str, target: str, link_travel_time: Dict[str, Dict[str, float]]) -> List[str]:
    for begin, end_dict in link_travel_time.items():
        for end, travel_time in end_dict.items():
            G.edges[begin, end]['cost'] = travel_time
    path = nx.dijkstra_path(G, source=source, target=target, weight='cost')
    return path

def get_all_shortest_paths(G: nx.DiGraph) -> Dict[str, List[str]]:
    all_paths = nx.all_pairs_dijkstra_path(G, weight='cost')
    return dict(all_paths)

if __name__ == '__main__':
    nodes, edges = parse_network()
    G = get_graph(nodes, edges)
    path = get_shortest_path(G, source='A', target='F')
    paths = get_all_shortest_paths(G)
    print(f"Dijkstra最短路径: {path}")
    print(f"所有最短路径: {paths}")