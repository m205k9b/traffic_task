import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

class NetworkVisualizer:
    """网络可视化工具类"""
    
    def __init__(self, graph: nx.DiGraph, nodes: Dict):
        """
        初始化可视化工具
        
        Parameters:
        graph: 网络图（nx.DiGraph）
        nodes: 节点字典 {节点名: [x坐标, y坐标]}
        """
        self.graph = graph
        self.nodes = nodes
        self.pos = {node: (self.nodes[node][0], self.nodes[node][1]) for node in self.graph.nodes()}
    
    def visualize_network_topology(self, save_path: str = None, title: str = "交通网络拓扑结构"):
        """
        可视化网络拓扑结构
        
        Parameters:
        save_path: 保存路径（None则不保存）
        title: 图表标题
        """
        plt.figure(figsize=(10, 8))
        
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8)
        
        # 绘制边
        nx.draw_networkx_edges(self.graph, self.pos, arrowstyle='->', arrowsize=20, 
                               edge_color='gray', alpha=0.6)
        
        # 添加节点标签
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold')
        
        # 添加边标签（起点-终点）
        edge_labels = {(u, v): f"{u}→{v}" for u, v in self.graph.edges()}
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, font_size=10)
        
        plt.title(title, fontsize=16, pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_edge_flows(self, edge_flows: Dict[Tuple, float], save_path: str = None, title: str = "边流量分布"):
        """
        可视化边流量分布
        
        Parameters:
        edge_flows: 边流量字典 {(起点, 终点): 流量}
        save_path: 保存路径（None则不保存）
        title: 图表标题
        """
        plt.figure(figsize=(12, 9))
        
        # 准备数据
        flows = [edge_flows[(u, v)] for u, v in self.graph.edges()]
        max_flow = max(flows) if flows else 1
        
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8)
        
        # 绘制边（根据流量着色和调整宽度）
        edge_colors = [flow / max_flow for flow in flows]
        edge_widths = [2 + 8 * (flow / max_flow) for flow in flows]
        
        nx.draw_networkx_edges(
            self.graph, self.pos, 
            edge_color=edge_colors, 
            edge_cmap=plt.cm.Reds,
            width=edge_widths,
            arrowstyle='->', 
            arrowsize=20,
            alpha=0.8
        )
        
        # 添加颜色条
        sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=0, vmax=max_flow))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca(), label='流量 (辆/小时)')
        
        # 添加节点标签
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold')
        
        # 添加边流量标签
        edge_labels = {(u, v): f"{edge_flows[(u, v)]:.0f}" for u, v in self.graph.edges()}
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, font_size=10)
        
        plt.title(title, fontsize=16, pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_link_performance(self, link_times: Dict[Tuple, float], save_path: str = None, title: str = "链路通行时间分布"):
        """
        可视化链路通行时间
        
        Parameters:
        link_times: 链路通行时间字典 {(起点, 终点): 通行时间}
        save_path: 保存路径（None则不保存）
        title: 图表标题
        """
        plt.figure(figsize=(12, 9))
        
        # 准备数据
        times = [link_times[(u, v)] for u, v in self.graph.edges()]
        max_time = max(times) if times else 1
        
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8)
        
        # 绘制边（根据通行时间着色）
        edge_colors = [time / max_time for time in times]
        edge_widths = [2 + 8 * (time / max_time) for time in times]
        
        nx.draw_networkx_edges(
            self.graph, self.pos, 
            edge_color=edge_colors, 
            edge_cmap=plt.cm.Oranges,
            width=edge_widths,
            arrowstyle='->', 
            arrowsize=20,
            alpha=0.8
        )
        
        # 添加颜色条
        sm = plt.cm.ScalarMappable(cmap=plt.cm.Oranges, norm=plt.Normalize(vmin=0, vmax=max_time))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca(), label='通行时间 (分钟)')
        
        # 添加节点标签
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold')
        
        # 添加边通行时间标签
        edge_labels = {(u, v): f"{link_times[(u, v)]:.1f}" for u, v in self.graph.edges()}
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, font_size=10)
        
        plt.title(title, fontsize=16, pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_comparison(self, edge_flows: Dict[Tuple, float], link_times: Dict[Tuple, float], 
                             save_path: str = None, main_title: str = "分配结果对比"):
        """
        可视化流量和通行时间对比（子图）
        
        Parameters:
        edge_flows: 边流量字典
        link_times: 链路通行时间字典
        save_path: 保存路径（None则不保存）
        main_title: 总标题
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
        
        # 准备数据
        flows = [edge_flows[(u, v)] for u, v in self.graph.edges()]
        times = [link_times[(u, v)] for u, v in self.graph.edges()]
        max_flow = max(flows) if flows else 1
        max_time = max(times) if times else 1
        
        # 子图1：流量分布
        plt.sca(ax1)
        edge_colors1 = [flow / max_flow for flow in flows]
        edge_widths1 = [2 + 8 * (flow / max_flow) for flow in flows]
        
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8, ax=ax1)
        nx.draw_networkx_edges(
            self.graph, self.pos, 
            edge_color=edge_colors1, 
            edge_cmap=plt.cm.Reds,
            width=edge_widths1,
            arrowstyle='->', 
            arrowsize=20,
            alpha=0.8,
            ax=ax1
        )
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold', ax=ax1)
        
        ax1.set_title('边流量分布', fontsize=14, pad=20)
        ax1.axis('off')
        
        # 子图2：通行时间分布
        plt.sca(ax2)
        edge_colors2 = [time / max_time for time in times]
        edge_widths2 = [2 + 8 * (time / max_time) for time in times]
        
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8, ax=ax2)
        nx.draw_networkx_edges(
            self.graph, self.pos, 
            edge_color=edge_colors2, 
            edge_cmap=plt.cm.Oranges,
            width=edge_widths2,
            arrowstyle='->', 
            arrowsize=20,
            alpha=0.8,
            ax=ax2
        )
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold', ax=ax2)
        
        ax2.set_title('链路通行时间分布', fontsize=14, pad=20)
        ax2.axis('off')
        
        # 添加总标题
        fig.suptitle(main_title, fontsize=18, y=0.95)
        
        # 添加颜色条
        fig.subplots_adjust(right=0.85)
        cbar_ax1 = fig.add_axes([0.87, 0.55, 0.02, 0.3])
        sm1 = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=0, vmax=max_flow))
        sm1.set_array([])
        cbar1 = fig.colorbar(sm1, cax=cbar_ax1, label='流量 (辆/小时)')
        
        cbar_ax2 = fig.add_axes([0.87, 0.15, 0.02, 0.3])
        sm2 = plt.cm.ScalarMappable(cmap=plt.cm.Oranges, norm=plt.Normalize(vmin=0, vmax=max_time))
        sm2.set_array([])
        cbar2 = fig.colorbar(sm2, cax=cbar_ax2, label='通行时间 (分钟)')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

# 便捷函数：直接从AONAssignment对象创建可视化器
def create_visualizer_from_aon(aon_assignment):
    """
    从AONAssignment对象创建可视化器
    
    Parameters:
    aon_assignment: AONAssignment实例
    
    Returns:
    NetworkVisualizer实例
    """
    return NetworkVisualizer(aon_assignment.graph, aon_assignment.nodes)