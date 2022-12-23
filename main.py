from uniswap_graph_initializer import initialize_uniswap_graph, save_graph_as_json, load_graph_from_json


if __name__ == '__main__':
    uniswap_graph = load_graph_from_json('graph_23_12_2022.json')
    arb = uniswap_graph.find_arb_opportunities({'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'})
    print(arb)
