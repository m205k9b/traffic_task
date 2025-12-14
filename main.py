from AON import AON_get_network
from visualization import create_visualizer_from_aon

if (__name__ == '__main__'):
    assigner, flows, link_times = AON_get_network()
    aonVisualizer = create_visualizer_from_aon(assigner)
    aonVisualizer.visualize_network_topology()
    aonVisualizer.visualize_edge_flows(flows)
    aonVisualizer.visualize_link_performance(link_times)
    
    