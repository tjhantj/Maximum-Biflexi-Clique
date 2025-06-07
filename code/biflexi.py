import networkx as nx
import dynamic_connectivity
import abcore
import heapq
import itertools
import math

def remove_nodes_and_largest_component(G, s):

    core = G
    core.remove_nodes_from(s)
    if core is None:
        return nx.Graph()

    components = list(nx.connected_components(core))
    if len(components) == 0:
        return nx.Graph()
    
    largest_component = max(components, key = len)

    return G.subgraph(largest_component).copy()

def is_biflexi(G, tau):
    U = []
    V = []
    
    for node in G.nodes:
        if G.nodes[node]['bipartite'] == 0:
            U.append(node)
        else:
            V.append(node)

    U_cond = math.floor(len(V) ** tau)
    V_cond = math.floor(len(U) ** tau)

    U_satisfy = all(G.degree[node] >= U_cond for node in U)
    V_satisfy = all(G.degree[node] >= V_cond for node in V)

    return U_satisfy and V_satisfy

def print_graph(G, k):
    print("Nodes:")
    for node in G.nodes:
        if G.nodes[node]['bipartite'] == 0:
            print(f"uside:  {node}")
        else:
            print(f"vside:  {node-k}")
    
    print("\nEdges:")
    for u, v in G.edges:
        if G.nodes[u]['bipartite'] == 0:
            print(f"  {u} -- {v - k}")
        else:
            print(f"  {v} -- {u - k}")

def run(G, tau, U_Num, V_Num, U_nodes, V_nodes):
    max_alpha = G.degree[max(U_nodes, key=lambda n: G.degree[n])]
    max_beta = G.degree[max(V_nodes, key=lambda n: G.degree[n])]

    data, stop_alpha_for_b = abcore.optimized_alpha_beta_core_layers(G, max_alpha, max_beta, U_nodes, V_nodes)

    pq = []
    before = max_alpha + 1

    for b in range(1, max_beta + 1):

        New_G = abcore.find_alpha_beta_core(G, data, 1, b, max_alpha, stop_alpha_for_b)

        for a in range(1, before):
            # print(a, b)
            if a != 1:
                New_G = remove_nodes_and_largest_component(New_G, data[a - 1][b][0] | data[a - 1][b][1])

            if len(New_G.edges) == 0:
                before = a
                break

            if is_biflexi(New_G, tau):
                Num_edge = len(New_G.edges)
                pq.append((Num_edge * (-1), (a, b)))
                before = a
                break
            
        if before == 1:
            break

    heapq.heapify(pq)
    max_value = pq[0][0] * (-1) #for max pq
    Answer_G = abcore.find_alpha_beta_core(G, data, pq[0][1][0], pq[0][1][1], max_alpha, stop_alpha_for_b)

    while pq:
        top = heapq.heappop(pq)

        List = [(1, 1), (1, 0), (0, 1)]

        for n, m in List:
            if top[1][0] - n == 0 or top[1][1] - m == 0:
                continue
            Now_G = abcore.find_alpha_beta_core(G, data, top[1][0] - n, top[1][1] - m, max_alpha, stop_alpha_for_b)
            Num_edge = len(Now_G.edges)

            if(Num_edge <= max_value):
                continue
            
            FDC = dynamic_connectivity.FullyDynamicConnectivity(n = U_Num + V_Num + 1)
            for edge in Now_G.edges:
                FDC.insert_edge(edge[0], edge[1])

            degree = {node: Now_G.degree[node] for node in Now_G.nodes}
            heap = [(deg, node) for node, deg in degree.items()]
            heapq.heapify(heap)

            biflexi = False

            while heap:
                deg, u = heapq.heappop(heap)
                if deg == 0:
                    continue
                if degree[u] != deg:
                    continue

                node_list = []
                flag = True
                for v in list(Now_G.neighbors(u)):
                    FDC.delete_edge(u, v)
                    node_list.append(v)

                for p, q in itertools.combinations(node_list, 2):
                    connect = FDC.connected(p, q)
                    if not connect:
                        flag = False
                        break

                if flag:
                    for v in list(Now_G.neighbors(u)):
                        Now_G.remove_edge(u, v)
                        Num_edge -= 1
                        degree[v] -= 1
                        heapq.heappush(heap, (degree[v], v))
                    Now_G.remove_node(u)
                    if(len(Now_G.edges) == 0):
                        break
                    if(is_biflexi(Now_G, tau)):
                        biflexi = True
                    break

                else:
                    for v in node_list:
                        FDC.insert_edge(u, v)

                if Num_edge <= max_value:
                    break
                
                if biflexi:
                    max_value = Num_edge
                    Answer_G = Now_G

    return Answer_G, max_value
    print_graph(Answer_G, U_Num)