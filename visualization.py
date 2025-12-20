import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from typing import Dict, List, Tuple
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False    

class NetworkVisualizer:
    """网络可视化工具类（修复标签显示+双向边优化）"""
    
    def __init__(self, graph: nx.DiGraph, nodes: Dict):
        """
        初始化可视化工具
        :param graph: 网络图（nx.DiGraph）
        :param nodes: 节点字典 {节点名: [x坐标, y坐标]}
        """
        self.graph = graph
        self.nodes = nodes
        
        # 1. 初始化节点坐标（确保所有图节点都有坐标）
        self.pos = {}
        for node in self.graph.nodes():
            if node in self.nodes and len(self.nodes[node]) == 2:
                self.pos[node] = (self.nodes[node][0], self.nodes[node][1])
            else:
                # 缺失坐标的节点分配默认位置（避免KeyError）
                self.pos[node] = (np.random.uniform(0, 10), np.random.uniform(0, 10))
                print(f"警告：节点[{node}]无坐标，分配默认位置{self.pos[node]}")
        
        # 2. 检测双向边
        self.bidirectional_edges = self._find_bidirectional_edges()
        
        # 3. 预计算边的偏移位置（解决双向边重叠）
        self.edge_offset = self._calc_edge_offset(offset=0.08)

    def _find_bidirectional_edges(self) -> set:
        """找出所有双向边对"""
        bidirectional = set()
        for u, v in self.graph.edges():
            if (v, u) in self.graph.edges() and (v, u) not in bidirectional:
                bidirectional.add((u, v))
        return bidirectional

    def _calc_edge_offset(self, offset: float = 0.1) -> Dict[Tuple, Tuple[Tuple, Tuple]]:
        """计算每条边的偏移起点和终点"""
        edge_offset = {}
        for u, v in self.graph.edges():
            # 原始坐标
            u_x, u_y = self.pos[u]
            v_x, v_y = self.pos[v]
            
            # 计算边的方向向量和法向量
            dx = v_x - u_x
            dy = v_y - u_y
            length = np.sqrt(dx**2 + dy**2) if dx**2 + dy**2 > 0 else 1
            
            # 单位法向量（垂直于边）
            nx = -dy / length
            ny = dx / length
            
            # 双向边偏移（正向/反向相反方向）
            if (u, v) in self.bidirectional_edges:
                # 正向边：上/右偏移
                new_u = (u_x + nx * offset, u_y + ny * offset)
                new_v = (v_x + nx * offset, v_y + ny * offset)
            elif (v, u) in self.bidirectional_edges:
                # 反向边：下/左偏移
                new_u = (u_x - nx * offset, u_y - ny * offset)
                new_v = (v_x - nx * offset, v_y - ny * offset)
            else:
                # 单向边：不偏移
                new_u = (u_x, u_y)
                new_v = (v_x, v_y)
            
            edge_offset[(u, v)] = (new_u, new_v)
        return edge_offset

    def _draw_edges(self, ax, edge_colors='gray', edge_widths=2, alpha=0.8):
        """绘制带偏移/曲率的边（核心方法）"""
        # 统一处理颜色/宽度为列表
        if not isinstance(edge_colors, list):
            edge_colors = [edge_colors] * len(self.graph.edges())
        if not isinstance(edge_widths, list):
            edge_widths = [edge_widths] * len(self.graph.edges())
        
        # 逐个绘制边
        for idx, (u, v) in enumerate(self.graph.edges()):
            (u_x, u_y), (v_x, v_y) = self.edge_offset[(u, v)]
            
            # 双向边添加曲率，单向边直线
            curvature = 0.2 if (u, v) in self.bidirectional_edges or (v, u) in self.bidirectional_edges else 0.0
            
            # 绘制弯曲箭头
            arrow = patches.FancyArrowPatch(
                (u_x, u_y), (v_x, v_y),
                connectionstyle=f"arc3,rad={curvature}",
                arrowstyle='->',
                mutation_scale=18,  # 箭头大小
                color=edge_colors[idx],
                linewidth=edge_widths[idx],
                alpha=alpha,
                zorder=1  # 边在节点下方
            )
            ax.add_patch(arrow)

    def visualize_network_topology(self, save_path=None, title="交通网络拓扑结构"):
        """可视化拓扑（带标签，无KeyError）"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 1. 绘制节点
        nx.draw_networkx_nodes(
            self.graph, self.pos, ax=ax,
            node_size=800, node_color='lightblue',
            edgecolors='black', alpha=0.9
        )
        
        # 2. 绘制边
        self._draw_edges(ax, edge_colors='gray', edge_widths=2, alpha=0.7)
        
        # 3. 绘制节点标签
        nx.draw_networkx_labels(self.graph, self.pos, ax=ax, font_size=12, font_weight='bold')
        
        # 4. 手动绘制边标签（核心修复：不用nx的edge_labels）
        for (u, v) in self.graph.edges():
            # 获取偏移后的边中点
            (u_x, u_y), (v_x, v_y) = self.edge_offset[(u, v)]
            mid_x = (u_x + v_x) / 2
            mid_y = (u_y + v_y) / 2
            
            # 双向边标签额外偏移（避免重叠）
            if (u, v) in self.bidirectional_edges:
                mid_y += 3.6
            elif (v, u) in self.bidirectional_edges:
                mid_y -= 3.6
            
            # 绘制标签（带白色背景，提升可读性）
            ax.text(
                mid_x, mid_y, f"{u}→{v}",
                fontsize=9, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8),
                zorder=5  # 标签在最上层
            )
        
        # 图表样式
        ax.set_title(title, fontsize=16, pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        # 保存/显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()

    def visualize_edge_flows(self, edge_flows: Dict[str, Dict[str, str]],
                             link_travel_time: Dict[str, Dict[str, str]], 
                             save_path=None, title="边流量分布"):
        """可视化边流量（带标签）"""
        fig, ax = plt.subplots(figsize=(12, 9))
        
        # 1. 数据预处理
        flows = []
        for u, v in self.graph.edges():
            if u not in edge_flows or v not in edge_flows[u]:
                flows.append(0)
            else:
                flows.append(edge_flows[u][v])
        max_flow = max(flows) if flows and max(flows) > 0 else 1
        
        # 2. 计算边颜色/宽度（按流量缩放）
        edge_colors = [plt.cm.Reds(flow/max_flow) for flow in flows]
        edge_widths = [2 + 8 * (flow/max_flow) for flow in flows]
        
        # 3. 绘制节点
        nx.draw_networkx_nodes(
            self.graph, self.pos, ax=ax,
            node_size=800, node_color='lightblue',
            edgecolors='black', alpha=0.9
        )
        
        # 4. 绘制带流量样式的边
        self._draw_edges(ax, edge_colors=edge_colors, edge_widths=edge_widths, alpha=0.8)
        
        # 5. 绘制节点标签
        nx.draw_networkx_labels(self.graph, self.pos, ax=ax, font_size=12, font_weight='bold')
        
        # 6. 手动绘制流量标签
        for (u, v) in self.graph.edges(): 
            link_time = link_travel_time[u][v]
            if u not in edge_flows or v not in edge_flows[u]:  # 忽略无流量的边
                continue
            flow = edge_flows[u][v]
                
            # 边中点位置
            (u_x, u_y), (v_x, v_y) = self.edge_offset[(u, v)]
            mid_x = (u_x + v_x) / 2
            mid_y = (u_y + v_y) / 2

            a1 = u_x - v_x
            a2 = u_y - v_y
            
            # 双向边标签偏移
            if a2 == 0:
                if a1 > 0:  # 顺向边
                    mid_y += 1.00
                else:  # 逆向边
                    mid_y -= 1.00
            elif a1 == 0:
                if a2 > 0:  # 顺向边
                    mid_x -= 1.00
                else:  # 逆向边
                    mid_x += 1.00
            else:
                k = a2 / a1
                if (u, v) in self.bidirectional_edges:
                    mid_y -= np.sqrt(1.00 / (k ** 2 + 1))
                    mid_x += np.sqrt(1.00 * (k ** 2) / (k ** 2 + 1))
                elif (v, u) in self.bidirectional_edges:
                    mid_y += np.sqrt(1.00 / (k ** 2 + 1))
                    mid_x -= np.sqrt(1.00 * (k ** 2) / (k ** 2 + 1))
                
            
            # 绘制流量标签
            ax.text(
                mid_x, mid_y, f"{u} -> {v}\nflow={flow:.0f}\ntime={link_time:.2f}",
                fontsize=9, ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9),
                zorder=5
            )
        
        # 7. 添加颜色条
        sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(vmin=0, vmax=max_flow))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label='流量 (辆/小时)', shrink=0.8)
        
        # 图表样式
        ax.set_title(title, fontsize=16, pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


# 便捷创建函数
def create_visualizer_from_aon(aon_assignment):
    return NetworkVisualizer(aon_assignment.graph, aon_assignment.nodes)

def create_visualizer_from_ia(ia_assignment):
    return NetworkVisualizer(ia_assignment.graph, ia_assignment.nodes)