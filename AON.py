import numpy as np
from typing import Dict, List, Tuple
import networkx as nx
import load_data as ld

class AONAssignment:
    """全有全无分配算法实现"""
    
    def __init__(self, nodes: List[str], edges: List[Tuple]):
        """
        初始化网络
        
        Parameters:
        nodes: 节点列表
        edges: 边列表，每个元素为 (起点, 终点, 成本, 容量)
        """
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(nodes)
        
        for u, v, cost, capacity in edges:
            self.graph.add_edge(u, v, cost=cost, capacity=capacity, flow=0)
            self.graph.add_edge(v, u, cost=cost, capacity=capacity, flow=0)
    def calculate_all_pairs_shortest_path(self):
        """计算所有节点对之间的最短路径"""
        self.shortest_paths = {}
        
        for source in self.graph.nodes():
            for target in self.graph.nodes():
                if source != target:
                    try:
                        # 使用网络成本作为权重
                        path = nx.shortest_path(
                            self.graph, 
                            source, 
                            target, 
                            weight='cost'
                        )
                        cost = nx.shortest_path_length(
                            self.graph, 
                            source, 
                            target, 
                            weight='cost'
                        )
                        self.shortest_paths[(source, target)] = (path, cost)
                    except:
                        self.shortest_paths[(source, target)] = ([], float('inf'))
    
    def assign_demand(self, demand_matrix: Dict[Tuple, float]):
        """
        根据需求矩阵进行AON分配
        
        Parameters:
        demand_matrix: 字典，键为(起点, 终点)，值为需求量
        """
        # 重置所有边的流量
        for u, v in self.graph.edges():
            self.graph[u][v]['flow'] = 0
        
        # 对每个OD对进行分配
        for (origin, destination), demand in demand_matrix.items():
            if demand <= 0:
                continue
                
            # 获取最短路径
            if (origin, destination) in self.shortest_paths:
                path, _ = self.shortest_paths[(origin, destination)]
                
                if not path:
                    print(f"警告: {origin} 到 {destination} 无路径")
                    continue
                
                # 在路径的每条边上增加流量
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    
                    # 检查边是否存在
                    if self.graph.has_edge(u, v):
                        self.graph[u][v]['flow'] += demand
                    else:
                        print(f"错误: 边 {u}→{v} 不存在")
        
        return self.get_edge_flows()
    
    def get_edge_flows(self):
        """获取所有边的流量"""
        edge_flows = {}
        for u, v in self.graph.edges():
            edge_flows[(u, v)] = self.graph[u][v]['flow']
        return edge_flows
    
    def calculate_link_performance(self, bpr_params=(0.15, 4)):
        """
        计算链路性能（基于BPR函数）
        
        Parameters:
        bpr_params: (alpha, beta) BPR函数参数
        """
        link_performance = {}
        
        for u, v in self.graph.edges():
            flow = self.graph[u][v]['flow']
            capacity = self.graph[u][v]['capacity']
            free_flow_time = self.graph[u][v]['cost']
            
            if capacity > 0:
                # BPR函数: t = t0 * [1 + α*(v/c)^β]
                alpha, beta = bpr_params
                travel_time = free_flow_time * (1 + alpha * (flow / capacity) ** beta)
                link_performance[(u, v)] = travel_time
            else:
                link_performance[(u, v)] = float('inf')
        
        return link_performance

# 使用示例
def example_network():
    """创建一个示例网络"""
    
    # 定义边: (起点, 终点, 自由流时间, 容量)
    nodes, edges = ld.parse_network()
    
    # 创建AON分配器
    assigner = AONAssignment(nodes, edges)
    
    # 计算所有最短路径
    assigner.calculate_all_pairs_shortest_path()
    
    # 定义需求矩阵
    demand_matrix = ld.get_demand()
    
    # 执行AON分配
    edge_flows = assigner.assign_demand(demand_matrix)
    
    print("全有全无分配结果:")
    for edge, flow in edge_flows.items():
        if flow > 0:
            print(f"{edge[0]}→{edge[1]}: {flow:.2f} 辆/小时")
    
    # 计算链路性能
    link_times = assigner.calculate_link_performance()
    print("\n链路通行时间:")
    for edge, time in link_times.items():
        if edge_flows[edge] > 0:
            print(f"{edge[0]}→{edge[1]}: {time:.2f} 分钟")
    
    return assigner, edge_flows

if __name__ == "__main__":
    assigner, flows = example_network()