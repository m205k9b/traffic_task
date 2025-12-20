from typing import Dict, List, Tuple

def get_link_travel_time(flow: Dict[str, Dict[str, float]], edge, begin, end):
    """路阻函数/行程时间函数：t = t0 * (1 + (Q/C))^2"""
    t0 = edge['free_flow_time']
    C = edge['capacity']
    if begin not in flow or end not in flow[begin]: 
        return t0
    Q = flow[begin][end]
    return t0 * (1 + (Q / C) ) ** 2