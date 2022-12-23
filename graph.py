from __future__ import annotations

import math


class graph:

    def __init__(self):
        self.adjacency_list: dict[str, list[tuple[str, tuple[int, int]]] | None] = {}
        self.liquidity_pools_count = 0
        self.tokens_count = 0

    def add_node(self, node):
        self.adjacency_list[node] = None
        self.tokens_count += 1

    def add_edge(self, node0, node1, reserves0, reserves1):
        if self.adjacency_list[node0] is None:
            self.adjacency_list[node0] = [(node1, (reserves0, reserves1))]
        else:
            self.adjacency_list[node0].append((node1, (reserves0, reserves1)))
        if self.adjacency_list[node1] is None:
            self.adjacency_list[node1] = [(node0, (reserves1, reserves0))]
        else:
            self.adjacency_list[node1].append((node0, (reserves1, reserves0)))
        self.liquidity_pools_count += 1

    def add_single_edge(self, node0, node1, reserves0, reserves1):
        if self.adjacency_list[node0] is None:
            self.adjacency_list[node0] = [(node1, (reserves0, reserves1))]
        else:
            self.adjacency_list[node0].append((node1, (reserves0, reserves1)))
        self.liquidity_pools_count += 0.5

    def get_adjacent(self, node):
        return self.adjacency_list[node]

    def calculate_updated_constants(self, l, m, n, A, B):
        max_constant_size = None
        pool_fee = 0.997
        n_out = A * n
        m_out = int(B * m * pool_fee)
        l_out = (A * l) + m
        if max_constant_size is not None and n_out > max_constant_size:
            divide_by = n_out // max_constant_size
            n_out = n_out // divide_by
            m_out = m_out // divide_by
            l_out = l_out // divide_by
        if max_constant_size is not None and m_out > max_constant_size:
            divide_by = m_out // max_constant_size
            n_out = n_out // divide_by
            m_out = m_out // divide_by
            l_out = l_out // divide_by
        if max_constant_size is not None and l_out > max_constant_size:
            divide_by = l_out // max_constant_size
            n_out = n_out // divide_by
            m_out = m_out // divide_by
            l_out = l_out // divide_by
        return l_out, m_out, n_out

    def calculate_max_profit(self, l, m, n):
        return (m*l)/(n*math.sqrt(m*n) - n**2 + l**2) if (n*math.sqrt(m*n) - n**2 + l**2) != 0.0 else 0.0

    def should_update_best_constants(self, l_0, m_0, n_0, l_1, m_1, n_1):
        val1 = self.calculate_max_profit(l_0, m_0, n_0)
        val2 = self.calculate_max_profit(l_1, m_1, n_1)
        print(val1, val2)
        return val2 > val1

    def calculate_profit_and_optimum_from_cycle(self, derivative, tokenOut, TokenIn):
        pass

    def find_arb_opportunities(self, starting_tokens: set):
        arb_opportunities = []
        for starting_token in starting_tokens:
            # Need to store best path and the 3 constants l, m, n
            best_values = {node: (0, 1, 1) for node in self.adjacency_list.keys()}
            paths = [[starting_token]]
            for path_length in range(self.liquidity_pools_count):
                new_paths = []
                print(paths)
                for path in paths:
                    last_node = path[-1]
                    l, m, n = best_values[last_node]
                    for node, (reserves_A, reserves_B) in self.get_adjacent(last_node):
                        new_path = path.copy()
                        print(last_node, node)
                        if (last_node, node) in zip(paths, paths[1:]) or (node, last_node) in zip(paths, paths[1:]):
                            print("bad")
                            if node == starting_token:
                                l_1, m_1, n_1 = self.calculate_updated_constants(l, m, n, reserves_A, reserves_B)
                                arb_opportunities.append((path, l_1, m_1, n_1))
                        else:
                            l_1, m_1, n_1 = self.calculate_updated_constants(l, m, n, reserves_A, reserves_B)
                            if l == 0 and n == 1 and m == 1:
                                best_values[node] = (l_1, m_1, n_1)
                                new_path.append(node)
                                new_paths.append(new_path)
                            elif self.should_update_best_constants(l, m, n, l_1, m_1, n_1):
                                best_values[node] = (l_1, m_1, n_1)
                                new_path.append(node)
                                new_paths.append(new_path)
                paths = new_paths
        return arb_opportunities



