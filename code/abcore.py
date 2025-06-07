import networkx as nx
from collections import defaultdict

def optimized_alpha_beta_core_layers(G, max_alpha, max_beta, U_nodes, V_nodes):
    data = defaultdict(lambda: defaultdict(lambda: (set(), set())))
    core = defaultdict(lambda: defaultdict(lambda: (set(), set())))
    stop_alpha_for_b = {} 

    # initialization: foe each, (1, b)-core computation
    for b in range(1, max_beta + 1):
        curr_U = set(U_nodes)
        curr_V = set(V_nodes)

        changed = True
        while changed:
            changed = False

            remove_U = {u for u in curr_U if sum(1 for v in G[u] if v in curr_V) < 1}
            if remove_U:
                curr_U -= remove_U
                changed = True

            remove_V = {v for v in curr_V if sum(1 for u in G[v] if u in curr_U) < b}
            if remove_V:
                curr_V -= remove_V
                changed = True

        core[1][b] = (curr_U.copy(), curr_V.copy())

        if not curr_U and not curr_V:
            stop_alpha_for_b[b] = 1
            continue

        for a in range(2, max_alpha + 2):  # for a ∈ [2, max_alpha + 1] → core[a+1]
            prev_U, prev_V = core[a - 1][b]
            curr_U = prev_U.copy()
            curr_V = prev_V.copy()

            changed = True
            while changed:
                changed = False

                remove_U = {u for u in curr_U if sum(1 for v in G[u] if v in curr_V) < a}
                if remove_U:
                    curr_U -= remove_U
                    changed = True

                remove_V = {v for v in curr_V if sum(1 for u in G[v] if u in curr_U) < b}
                if remove_V:
                    curr_V -= remove_V
                    changed = True

            core[a][b] = (curr_U.copy(), curr_V.copy())

            if not curr_U and not curr_V:
                stop_alpha_for_b[b] = a
                break

    # data[a][b] = core[a][b] - core[a+1][b]
    for b in range(1, max_beta + 1):
        max_a = stop_alpha_for_b.get(b, max_alpha + 1)
        for a in range(1, max_a):
            this_U, this_V = core[a][b]
            next_U, next_V = core[a + 1][b]

            diff_U = this_U - next_U
            diff_V = this_V - next_V

            data[a][b] = (diff_U, diff_V)

    return data, stop_alpha_for_b
def find_alpha_beta_core(G, data, a, b, max_alpha, stop_alpha_for_b):

    result_U = set()
    result_V = set()

    max_a = stop_alpha_for_b.get(b, max_alpha + 1)

    for alpha in range(a, max_a):
        if b in data[alpha]:
            u_part, v_part = data[alpha][b]
            result_U.update(u_part)
            result_V.update(v_part)

    result = result_U | result_V

    core = G.subgraph(result)
    

    components = list(nx.connected_components(core))
    if len(components) == 0:
        return nx.Graph()

    largest_component = max(components, key = len)

    return G.subgraph(largest_component).copy()