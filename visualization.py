import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

class NetworkVisualizer:
    """网络可视化工具类（优化双向边显示）"""
    
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
        
        # 预计算双向边和偏移位置
        self.bidirectional_edges = self._find_bidirectional_edges()
        self.offset_pos = self._calculate_offset_positions(offset=0.08)
    
    def _find_bidirectional_edges(self) -> set:
        """找出所有双向边对"""
        bidirectional = set()
        for u, v in self.graph.edges():
            if (v, u) in self.graph.edges() and (v, u) not in bidirectional:
                bidirectional.add((u, v))
        return bidirectional
    
    def _calculate_offset_positions(self, offset: float = 0.1) -> Dict[Tuple, Tuple[float, float]]:
        """
        计算偏移后的节点位置（避免双向边重叠）
        
        Parameters:
        offset: 偏移量（根据坐标范围调整）
        
        Returns:
        偏移位置字典 {(u, v): (偏移后的u坐标, 偏移后的v坐标)}
        """
        offset_pos = {}
        
        for u, v in self.graph.edges():
            # 获取原始坐标
            u_x, u_y = self.pos[u]
            v_x, v_y = self.pos[v]
            
            # 计算边的方向向量
            dx = v_x - u_x
            dy = v_y - u_y
            length = np.sqrt(dx**2 + dy**2)
            
            if length > 0:
                # 单位法向量（垂直于边的方向）
                nx = -dy / length
                ny = dx / length
                
                # 双向边偏移（正向和反向向不同方向偏移）
                if (u, v) in self.bidirectional_edges:
                    # 正向边 (u→v) 向上/右偏移
                    offset_u_x = u_x + nx * offset
                    offset_u_y = u_y + ny * offset
                    offset_v_x = v_x + nx * offset
                    offset_v_y = v_y + ny * offset
                elif (v, u) in self.bidirectional_edges:
                    # 反向边 (v→u) 向下/左偏移
                    offset_u_x = u_x - nx * offset
                    offset_u_y = u_y - ny * offset
                    offset_v_x = v_x - nx * offset
                    offset_v_y = v_y - ny * offset
                else:
                    # 单向边不偏移
                    offset_u_x, offset_u_y = u_x, u_y
                    offset_v_x, offset_v_y = v_x, v_y
                
                offset_pos[(u, v)] = ((offset_u_x, offset_u_y), (offset_v_x, offset_v_y))
            else:
                offset_pos[(u, v)] = ((u_x, u_y), (v_x, v_y))
        
        return offset_pos
    
    def _draw_edges_with_offset(self, ax, edge_colors, edge_widths, alpha=0.8):
        """绘制带偏移的边（解决双向边重叠）"""
        for i, (u, v) in enumerate(self.graph.edges()):
            # 获取偏移后的起点和终点坐标
            (u_x, u_y), (v_x, v_y) = self.offset_pos[(u, v)]
            
            # 计算曲率（双向边添加曲率）
            curvature = 0.2 if (u, v) in self.bidirectional_edges or (v, u) in self.bidirectional_edges else 0.0
            
            # 创建弯曲箭头
            arrow = patches.FancyArrowPatch(
                (u_x, u_y), (v_x, v_y),
                connectionstyle=f"arc3,rad={curvature}",
                arrowstyle='->',
                mutation_scale=20,
                color=edge_colors[i] if isinstance(edge_colors, list) else edge_colors,
                linewidth=edge_widths[i] if isinstance(edge_widths, list) else edge_widths,
                alpha=alpha,
                zorder=1
            )
            ax.add_patch(arrow)
    
    def visualize_network_topology(self, save_path: str = None, title: str = "交通网络拓扑结构"):
        """
        可视化网络拓扑结构（优化双向边显示）
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8, ax=ax)
        
        # 绘制带偏移的边
        self._draw_edges_with_offset(ax, edge_colors='gray', edge_widths=2, alpha=0.6)
        
        # 添加节点标签
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold', ax=ax)
        
        # 添加边标签（调整位置避免重叠）
        edge_labels = {(u, v): f"{u}→{v}" for u, v in self.graph.edges()}
        label_pos = {}
        
        for (u, v), label in edge_labels.items():
            # 计算标签位置（偏移边的中点）
            (u_x, u_y), (v_x, v_y) = self.offset_pos[(u, v)]
            mid_x = (u_x + v_x) / 2
            mid_y = (u_y + v_y) / 2
            
            # 双向边标签额外偏移
            if (u, v) in self.bidirectional_edges:
                mid_y += 0.05
            elif (v, u) in self.bidirectional_edges:
                mid_y -= 0.05
                
            label_pos[(u, v)] = (mid_x, mid_y)
        
        nx.draw_networkx_edge_labels(self.graph, label_pos, edge_labels, font_size=9, ax=ax)
        
        ax.set_title(title, fontsize=16, pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_edge_flows(self, edge_flows: Dict[Tuple, float], save_path: str = None, title: str = "边流量分布"):
        """
        可视化边流量分布（优化双向边显示）
        """
        fig, ax = plt.subplots(figsize=(12, 9))
        
        # 准备数据
        flows = [edge_flows[(u, v)] for u, v in self.graph.edges()]
        max_flow = max(flows) if flows else 1
        
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8, ax=ax)
        
        # 计算边颜色和宽度
        edge_colors = [plt.cm.Reds(flow/max_flow) for flow in flows]
        edge_widths = [2 + 8 * (flow / max_flow) for flow in flows]
        
        # 绘制带偏移的边
        self._draw_edges_with_offset(ax, edge_colors, edge_widths, alpha=0.8)
        
        # 添加颜色条
        sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=0, vmax=max_flow))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label='流量 (辆/小时)')
        
        # 添加节点标签
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold', ax=ax)
        
        # 添加边流量标签（调整位置）
        edge_labels = {(u, v): f"{edge_flows[(u, v)]:.0f}" for u, v in self.graph.edges()}
        label_pos = {}
        
        for (u, v), label in edge_labels.items():
            (u_x, u_y), (v_x, v_y) = self.offset_pos[(u, v)]
            mid_x = (u_x + v_x) / 2
            mid_y = (u_y + v_y) / 2
            
            # 双向边标签位置调整
            if (u, v) in self.bidirectional_edges:
                mid_y += 0.08
            elif (v, u) in self.bidirectional_edges:
                mid_y -= 0.08
                
            label_pos[(u, v)] = (mid_x, mid_y)
        
        nx.draw_networkx_edge_labels(self.graph, label_pos, edge_labels, font_size=9, ax=ax)
        
        ax.set_title(title, fontsize=16, pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_link_performance(self, link_times: Dict[Tuple, float], save_path: str = None, title: str = "链路通行时间分布"):
        """
        可视化链路通行时间（优化双向边显示）
        """
        fig, ax = plt.subplots(figsize=(12, 9))
        
        # 准备数据
        times = [link_times[(u, v)] for u, v in self.graph.edges()]
        max_time = max(times) if times else 1
        
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8, ax=ax)
        
        # 计算边颜色和宽度
        edge_colors = [plt.cm.Oranges(time/max_time) for time in times]
        edge_widths = [2 + 8 * (time / max_time) for time in times]
        
        # 绘制带偏移的边
        self._draw_edges_with_offset(ax, edge_colors, edge_widths, alpha=0.8)
        
        # 添加颜色条
        sm = plt.cm.ScalarMappable(cmap=plt.cm.Oranges, norm=plt.Normalize(vmin=0, vmax=max_time))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label='通行时间 (分钟)')
        
        # 添加节点标签
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold', ax=ax)
        
        # 添加边通行时间标签（调整位置）
        edge_labels = {(u, v): f"{link_times[(u, v)]:.1f}" for u, v in self.graph.edges()}
        label_pos = {}
        
        for (u, v), label in edge_labels.items():
            (u_x, u_y), (v_x, v_y) = self.offset_pos[(u, v)]
            mid_x = (u_x + v_x) / 2
            mid_y = (u_y + v_y) / 2
            
            # 双向边标签位置调整
            if (u, v) in self.bidirectional_edges:
                mid_y += 0.08
            elif (v, u) in self.bidirectional_edges:
                mid_y -= 0.08
                
            label_pos[(u, v)] = (mid_x, mid_y)
            print(label_pos)
        
        # nx.draw_networkx_edge_labels(self.graph, label_pos, edge_labels, font_size=9, ax=ax)
        
        ax.set_title(title, fontsize=16, pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def visualize_comparison(self, edge_flows: Dict[Tuple, float], link_times: Dict[Tuple, float], 
                             save_path: str = None, main_title: str = "分配结果对比"):
        """
        可视化流量和通行时间对比（优化双向边显示）
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
        
        # 准备数据
        flows = [edge_flows[(u, v)] for u, v in self.graph.edges()]
        times = [link_times[(u, v)] for u, v in self.graph.edges()]
        max_flow = max(flows) if flows else 1
        max_time = max(times) if times else 1
        
        # 子图1：流量分布
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8, ax=ax1)
        # 计算边样式
        edge_colors1 = [plt.cm.Reds(flow/max_flow) for flow in flows]
        edge_widths1 = [2 + 8 * (flow / max_flow) for flow in flows]
        # 绘制边
        self._draw_edges_with_offset(ax1, edge_colors1, edge_widths1, alpha=0.8)
        # 添加标签
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold', ax=ax1)
        ax1.set_title('边流量分布', fontsize=14, pad=20)
        ax1.axis('off')
        
        # 子图2：通行时间分布
        # 绘制节点
        nx.draw_networkx_nodes(self.graph, self.pos, node_size=800, node_color='lightblue', 
                               edgecolors='black', alpha=0.8, ax=ax2)
        # 计算边样式
        edge_colors2 = [plt.cm.Oranges(time/max_time) for time in times]
        edge_widths2 = [2 + 8 * (time / max_time) for time in times]
        # 绘制边
        self._draw_edges_with_offset(ax2, edge_colors2, edge_widths2, alpha=0.8)
        # 添加标签
        nx.draw_networkx_labels(self.graph, self.pos, font_size=12, font_weight='bold', ax=ax2)

        ax2.set_title('链路通行时间分布', fontsize=14, pad=20)
        ax2.axis('off')
        
        # 添加总标题
        fig.suptitle(main_title, fontsize=18, y=0.95)
        
        # 添加颜色条
        fig.subplots_adjust(right=0.85)
        # 流量颜色条
        cbar_ax1 = fig.add_axes([0.87, 0.55, 0.02, 0.3])
        sm1 = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=0, vmax=max_flow))
        sm1.set_array([])
        cbar1 = fig.colorbar(sm1, cax=cbar_ax1, label='流量 (辆/小时)')
        
        # 时间颜色条
        cbar_ax2 = fig.add_axes([0.87, 0.15, 0.02, 0.3])
        sm2 = plt.cm.ScalarMappable(cmap=plt.cm.Oranges, norm=plt.Normalize(vmin=0, vmax=max_time))
        sm2.set_array([])
        cbar2 = fig.colorbar(sm2, cax=cbar_ax2, label='通行时间 (分钟)')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

# 便捷函数：直接从算法对象创建可视化器
def create_visualizer_from_aon(aon_assignment):
    return NetworkVisualizer(aon_assignment.graph, aon_assignment.nodes)

def create_visualizer_from_ia(ia_assignment):
    return NetworkVisualizer(ia_assignment.graph, ia_assignment.nodes)