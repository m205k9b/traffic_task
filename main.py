from AON import AON_get_network
from IA import example_ia_network

if (__name__ == '__main__'):
    assigner, flows, link_times = AON_get_network()
    ia_assigner, flows, records = example_ia_network()
    