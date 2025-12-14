import numpy as np
from typing import Dict, List, Tuple
import networkx as nx
import load_data as ld
import visualization as vis

class IAAssignment:
    """增量分配算法（Incremental Assignment）实现"""
    
    def __init__(self, nodes: Dict, edges: List[Tuple]):
        """
        初始化网络
        
        Parameters:
        nodes: 节点字典 {节点名: [x坐标, y坐标]}
        edges: 边列表，每个元素为 (起点, 终点, 自由流时间, 容量)
        """
        self.graph = nx.DiGraph()
        self.nodes = nodes  # 保存节点坐标信息
        self.graph.add_nodes_from(nodes.keys())
        
        # 初始化边属性
        for u, v, free_flow_time, capacity in edges:
            self.graph.add_edge(
                u, v, 
                free_flow_time=free_flow_time,  # 自由流时间
                capacity=capacity,              # 容量
                flow=0,                         # 当前流量
                cost=free_flow_time,            # 当前阻抗（初始为自由流时间）
                original_cost=free_flow_time    # 原始自由流时间
            )

            self.graph.add_edge(
                v, u, 
                free_flow_time=free_flow_time,  # 自由流时间
                capacity=capacity,              # 容量
                flow=0,                         # 当前流量
                cost=free_flow_time,            # 当前阻抗（初始为自由流时间）
                original_cost=free_flow_time    # 原始自由流时间
            )
    
    def update_link_impedance(self, bpr_params=(0.15, 4)):
        """
        根据当前流量更新链路阻抗（BPR函数）
        
        Parameters:
        bpr_params: (alpha, beta) BPR函数参数
        """
        alpha, beta = bpr_params
        
        for u, v in self.graph.edges():
            flow = self.graph[u][v]['flow']
            capacity = self.graph[u][v]['capacity']
            free_flow_time = self.graph[u][v]['free_flow_time']
            
            if capacity > 0:
                # BPR函数: t = t0 * [1 + α*(v/c)^β]
                travel_time = free_flow_time * (1 + alpha * (flow / capacity) ** beta)
                self.graph[u][v]['cost'] = travel_time
            else:
                self.graph[u][v]['cost'] = float('inf')
    
    def calculate_all_pairs_shortest_path(self):
        """基于当前链路阻抗计算所有节点对最短路径"""
        self.shortest_paths = {}
        
        for source in self.graph.nodes():
            for target in self.graph.nodes():
                if source != target:
                    try:
                        # 使用当前链路阻抗作为权重
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
    
    def assign_increment(self, demand_matrix: Dict[Tuple, float], increment_ratio: float):
        """
        分配单份增量需求
        
        Parameters:
        demand_matrix: 完整需求矩阵
        increment_ratio: 增量比例（如0.1表示10%）
        
        Returns:
        本次增量分配的边流量
        """
        incremental_flows = {(u, v): 0 for u, v in self.graph.edges()}
        
        # 对每个OD对分配增量需求
        for (origin, destination), total_demand in demand_matrix.items():
            if total_demand <= 0:
                continue
                
            # 计算本次增量需求
            incremental_demand = total_demand * increment_ratio
            
            # 获取基于当前阻抗的最短路径
            if (origin, destination) in self.shortest_paths:
                path, _ = self.shortest_paths[(origin, destination)]
                
                if not path:
                    print(f"警告: {origin} 到 {destination} 无路径")
                    continue
                
                # 在路径上分配增量需求
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    
                    if self.graph.has_edge(u, v):
                        # 更新总流量
                        self.graph[u][v]['flow'] += incremental_demand
                        # 记录本次增量流量
                        incremental_flows[(u, v)] += incremental_demand
                    else:
                        print(f"错误: 边 {u}→{v} 不存在")
        
        return incremental_flows
    
    def assign_demand(self, demand_matrix: Dict[Tuple, float], num_increments: int = 10, bpr_params=(0.15, 4)):
        """
        执行增量分配
        
        Parameters:
        demand_matrix: 需求矩阵
        num_increments: 增量份数（默认10份）
        bpr_params: BPR函数参数
        
        Returns:
        最终边流量、各增量分配记录
        """
        if num_increments <= 0:
            raise ValueError("增量份数必须大于0")
        
        # 初始化
        increment_ratio = 1.0 / num_increments
        increment_records = []  # 记录每一步的分配结果
        self.total_iterations = num_increments
        
        print(f"开始增量分配，共分为 {num_increments} 份增量")
        print("-" * 60)
        
        for i in range(num_increments):
            print(f"\n第 {i+1}/{num_increments} 份增量分配:")
            
            # 1. 基于当前流量更新链路阻抗
            self.update_link_impedance(bpr_params)
            
            # 2. 计算当前阻抗下的最短路径
            self.calculate_all_pairs_shortest_path()
            
            # 3. 分配当前增量
            incremental_flows = self.assign_increment(demand_matrix, increment_ratio)
            
            # 4. 记录本次增量
            increment_records.append({
                'iteration': i+1,
                'flows': incremental_flows.copy(),
                'link_impedance': {(u, v): self.graph[u][v]['cost'] for u, v in self.graph.edges()}
            })
            
            # 打印本次增量的主要结果
            print(f"  分配完成，非零流量边数: {sum(1 for f in incremental_flows.values() if f > 0)}")
        
        print("\n" + "-" * 60)
        print("增量分配完成！")
        
        return self.get_edge_flows(), increment_records
    
    def get_edge_flows(self):
        """获取最终边流量"""
        edge_flows = {}
        for u, v in self.graph.edges():
            edge_flows[(u, v)] = self.graph[u][v]['flow']
        return edge_flows
    
    def calculate_link_performance(self):
        """计算最终链路性能（通行时间）"""
        link_performance = {}
        
        for u, v in self.graph.edges():
            link_performance[(u, v)] = self.graph[u][v]['cost']
        
        return link_performance
    
    def reset_network(self):
        """重置网络状态（流量和阻抗）"""
        for u, v in self.graph.edges():
            self.graph[u][v]['flow'] = 0
            self.graph[u][v]['cost'] = self.graph[u][v]['original_cost']
    
    def get_visualizer(self):
        """创建可视化器"""
        return vis.NetworkVisualizer(self.graph, self.nodes)
    
    def visualize_increment_process(self, increment_records: List[Dict], save_dir: str = "./"):
        """
        可视化增量分配过程
        
        Parameters:
        increment_records: 增量分配记录
        save_dir: 保存目录
        """
        visualizer = self.get_visualizer()
        
        # 可视化每一步的流量变化
        for record in increment_records:
            iteration = record['iteration']
            flows = record['flows']
            impedances = record['link_impedance']
            
            print(f"\n可视化第 {iteration} 步增量分配结果...")
            
            # 流量可视化
            visualizer.visualize_edge_flows(
                flows,
                save_path=f"{save_dir}ia_increment_{iteration}_flows.png",
                title=f"IA算法 - 第{iteration}/{self.total_iterations}步增量流量分布"
            )
            
            # 阻抗可视化
            visualizer.visualize_link_performance(
                impedances,
                save_path=f"{save_dir}ia_increment_{iteration}_impedance.png",
                title=f"IA算法 - 第{iteration}/{self.total_iterations}步链路阻抗分布"
            )

# 使用示例
def example_ia_network():
    """IA算法示例"""
    
    # 1. 加载数据
    nodes, edges = ld.parse_network()
    demand_matrix = ld.get_demand()
    
    # 2. 创建IA分配器
    ia_assigner = IAAssignment(nodes, edges)
    
    # 3. 执行增量分配（分为10份）
    final_flows, increment_records = ia_assigner.assign_demand(
        demand_matrix, 
        num_increments=1000,
        bpr_params=(0.15, 4)
    )
    
    # 4. 打印最终结果
    print("\n" + "=" * 60)
    print("IA算法最终分配结果:")
    print("=" * 60)
    for edge, flow in final_flows.items():
        if flow > 0:
            print(f"{edge[0]}→{edge[1]}: {flow:.2f} 辆/小时")
    
    # 5. 计算最终链路性能
    final_link_times = ia_assigner.calculate_link_performance()
    print("\n" + "=" * 60)
    print("最终链路通行时间:")
    print("=" * 60)
    for edge, time in final_link_times.items():
        if final_flows[edge] > 0:
            print(f"{edge[0]}→{edge[1]}: {time:.2f} 分钟")
    
    # 6. 可视化
    print("\n" + "=" * 60)
    print("开始可视化IA分配结果...")
    print("=" * 60)
    
    visualizer = ia_assigner.get_visualizer()
    
    # # 6.1 网络拓扑
    # visualizer.visualize_network_topology(
    #     save_path="images/ia_network_topology.png",
    #     title="IA算法 - 网络拓扑结构"
    # )
    
    # 6.2 最终流量分布
    visualizer.visualize_edge_flows(
        final_flows,
        save_path="images/ia_final_flows.png",
        title="IA算法 - 最终流量分布"
    )
    
    # 6.3 最终链路性能
    visualizer.visualize_link_performance(
        final_link_times,
        save_path="images/ia_final_performance.png",
        title="IA算法 - 最终链路通行时间"
    )
    
    # # 6.4 最终结果对比
    # visualizer.visualize_comparison(
    #     final_flows,
    #     final_link_times,
    #     save_path="images/ia_final_comparison.png",
    #     main_title="IA增量分配算法 - 最终结果对比"
    # )
    
    # 6.5 可视化增量过程（可选，会生成多幅图）
    # ia_assigner.visualize_increment_process(increment_records)
    
    return ia_assigner, final_flows, increment_records
