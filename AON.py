import numpy as np
from typing import Dict, List, Tuple
import networkx as nx
import load_data as ld
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import FancyArrowPatch
from visualization import NetworkVisualizer
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

class AONAssignment:
    """全有全无分配算法实现"""
    
    def __init__(self, nodes: Dict, edges: List[Tuple]):
        """
        初始化网络
        
        Parameters:
        nodes: 节点字典 {节点名: [x坐标, y坐标]}
        edges: 边列表，每个元素为 (起点, 终点, 成本, 容量)
        """
        self.graph = nx.DiGraph()
        self.nodes = nodes  # 保存节点坐标信息
        self.graph.add_nodes_from(nodes.keys())
        
        for u, v, cost, capacity in edges:
            self.graph.add_edge(u, v, cost=cost, capacity=capacity, flow=0)
            # 注释掉反向边，避免可视化混乱（如需双向网络可保留）
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
                    except nx.NetworkXNoPath:
                        self.shortest_paths[(source, target)] = ([], float('inf'))
                    except Exception as e:
                        print(f"计算{source}到{target}最短路径出错: {e}")
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
def AON_get_network():
    """创建一个示例网络"""
    
    # 解析网络数据
    nodes, edges = ld.parse_network()
    
    # 创建AON分配器
    assigner = AONAssignment(nodes, edges)
    
    # 计算所有最短路径
    assigner.calculate_all_pairs_shortest_path()
    
    # 获取需求矩阵
    demand_matrix = ld.get_demand()
    
    # 执行AON分配
    edge_flows = assigner.assign_demand(demand_matrix)
    
    # 打印分配结果
    print("="*50)
    print("全有全无分配结果:")
    print("="*50)
    for edge, flow in edge_flows.items():
        if flow > 0:
            print(f"{edge[0]}→{edge[1]}: {flow:.2f} 辆/小时")
    
    # 计算链路性能
    link_times = assigner.calculate_link_performance()
    print("\n" + "="*50)
    print("链路通行时间:")
    print("="*50)
    for edge, time in link_times.items():
        if edge_flows[edge] > 0:
            print(f"{edge[0]}→{edge[1]}: {time:.2f} 分钟")

    # 可视化展示
    AONVisualizer = NetworkVisualizer(assigner.graph, assigner.nodes)

    AONVisualizer.visualize_edge_flows(
        edge_flows, 
        save_path="images/AON_edge_flows.png",
        title= "全有全无分配结果" )
        
    AONVisualizer.visualize_link_performance(
        link_times,
        save_path="images/AON_link_times.png",
        title= "全有全无情况下的链路通行时间")

    
    return assigner, edge_flows, link_times
