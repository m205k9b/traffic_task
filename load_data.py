from typing import Dict, List, Tuple
import json
import numpy as np
from math import sqrt

network_path = 'json/network.json'
demand_path = 'json/demand.json'

# 获取图的数据
def load_data(file_path: str) -> Dict:
    with open(file_path) as f:
        data = json.load(f)
    return data

# 获取需求数据
def get_demand() -> Dict[Tuple[str, str], float]:
    demand_data: Dict[str, List] = load_data(demand_path)
    begins = demand_data['from']
    ends = demand_data['to']
    amounts = demand_data['amount']

    demands = {(begin, end): amount for begin, end, amount in zip(begins, ends, amounts)}
    return demands

def parse_network() -> Tuple[Dict, List[Dict[str, any]]]:
    """
    Docstring for parse_network
    
    :return: Description
    :rtype: Tuple[List[str], List[Dict[str, any]]]: 
        节点列表和边列表
        节点包括名称
        边：一个列表，每条边包括：
        {
            'from': 源节点名称,
            'to': 目标节点名称,
            'capacity': 边的容量,
            'free_flow_time': 边的自由流时间（单位：秒）
            'length': 距离
            'speedmax': 边的最大速度（单位：km/h）
        }
    """

    network_data = load_data(network_path)

    nodes: Dict[str, List] = network_data['nodes']
    nodes_dict: Dict = {node_name: [node_x, node_y] for node_name, node_x, node_y in zip(nodes['name'], nodes['x'], nodes['y'])}

    edges_dict: Dict[str, List] = network_data['links'] # 遍历边
    edges_list: List[List] = [edges_dict['between'], edges_dict['speedmax'], edges_dict['capacity']]

    ret_edges = [] # 返回的边数据
    for i in range(len(edges_list[0])):
        edge_dict = {}
        edge_between = edges_list[0][i]
        edge_begin, edge_end = edge_between
        edge_dict['begin'] = edge_begin # 边的起点
        edge_dict['end'] = edge_end # 边的终点

        # 算出边的距离
        edge_distance = sqrt((nodes_dict[edge_begin][0] - nodes_dict[edge_end][0]) ** 2 
                                + (nodes_dict[edge_begin][1] - nodes_dict[edge_end][1]) ** 2)
        edge_dict['distance'] = edge_distance

        # 算出自由流时间（距离/速度）
        edge_free_flow_time = edge_distance / edges_list[1][i]
        edge_dict['free_flow_time'] = edge_free_flow_time

        capacity = edges_list[2][i]
        edge_dict['capacity'] = capacity

        ret_edges.append(edge_dict)

    return nodes_dict, ret_edges