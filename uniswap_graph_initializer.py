import json
from graph import graph
from eth_abi.packed import encode_abi_packed
from web3 import Web3, HTTPProvider


def create_uniswap_pool_contract(pool_address, w3):
    swap_abi = json.loads(open('abi.json').read())['liquidityPool']
    return w3.eth.contract(address=pool_address, abi=swap_abi)


def calculate_liquidity_pool_address(token1, token2):
    token1.lower()
    token2.lower()
    factory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
    hexadem_ = '0x96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f'
    abiEncoded_1 = encode_abi_packed(['address', 'address'], (token1,
                                                              token2))
    salt_ = Web3.solidityKeccak(['bytes'], ['0x' + abiEncoded_1.hex()])
    abiEncoded_2 = encode_abi_packed(['address', 'bytes32'], (factory, salt_))
    resPair = Web3.solidityKeccak(['bytes', 'bytes'], ['0xff' + abiEncoded_2.hex(), hexadem_])[12:]
    return Web3.toChecksumAddress(resPair.hex())


def initialize_uniswap_graph() -> graph:
    w3 = Web3(HTTPProvider("https://mainnet.infura.io/v3/6b7111b98069498cb9a37339d4aa492a"))
    tokens = [Web3.toChecksumAddress(x) for x in json.loads(open('tokens.json').read()).values()]
    uniswap_graph = graph()
    for index, token0 in enumerate(tokens):
        for token1 in tokens[index+1:]:
            print(f"Getting liquidity pool for {token0}, {token1}")
            (token_A, token_B) = sorted((token0, token1))
            pool_address = calculate_liquidity_pool_address(token_A, token_B)
            print(pool_address)
            try:
                pool_contract = create_uniswap_pool_contract(pool_address, w3)
                [reserves0, reserves1, _] = pool_contract.functions.getReserves().call()
                uniswap_graph.add_edge(token0, token1, reserves0, reserves1)
                print(f"edge between {token0} and {token1} added.")
            except:
                print("pool doesn't exist")
    return uniswap_graph


def save_graph_as_json(gr, path_file):
    changed = {node: list(map(lambda x: {"node": x[0], "reserves0": x[1][0], "reserves1": x[1][1]}, adj_list if adj_list is not None else [])) for node, adj_list in gr.adjacency_list.items()}
    json_graph = json.dumps(changed)
    open(path_file, 'w').write(json_graph)


def load_graph_from_json(path_file) -> graph:
    uniswap_graph = graph()
    dictionary = json.loads(open(path_file).read())
    for node in dictionary.keys():
        uniswap_graph.add_node(node)
    for node, edges in dictionary.items():
        for edge in edges:
            node1 = edge['node']
            reserves0 = edge['reserves0']
            reserves1 = edge['reserves1']
            uniswap_graph.add_single_edge(node, node1, reserves0, reserves1)
    uniswap_graph.liquidity_pools_count = int(uniswap_graph.liquidity_pools_count)
    return uniswap_graph
