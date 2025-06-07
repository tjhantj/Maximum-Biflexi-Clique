import argparse
import networkx as nx
import time
import os
import csv

import biflexi

def read_bipartite_edgelist(path):
    G = nx.Graph()
    U = []
    V = []
    edge_list = []
    
    U_Num = 0     # Number of node in Group U
    V_Num = 0     # Number of node in Group V
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            u, v = map(int, line.split())
            if(u > U_Num):
                U_Num = u
            if(v > V_Num):
                V_Num = v
            edge_list.append((u, v))

    for u, v in edge_list:
        G.add_edge(u, v + U_Num)

    for i in range(1, U_Num + 1):
        U.append(i)

    for i in range(U_Num + 1, U_Num + V_Num + 1):
        V.append(i)
    
    for node in U:
        G.nodes[node]['bipartite'] = 0
    for node in V:
        G.nodes[node]['bipartite'] = 1
    
    return G, U, V

def read_bipartite_simple_edgelist(path):
    G = nx.Graph()
    U = []
    V = []
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            u, v = map(int, line.split())
            G.add_edge(u, v)
            U.append(u)
            V.append(v)
    
    for node in U:
        G.nodes[node]['bipartite'] = 0
    for node in V:
        G.nodes[node]['bipartite'] = 1
    
    return G, U, V

parser = argparse.ArgumentParser()
parser.add_argument('--t', type=float, default=0.7, help='tau threshold')
parser.add_argument('--algorithm', default='biflexi', help='specify algorithm name')
parser.add_argument('--network', default='../dataset/real/CL.dat', help='a folder name containing network.dat')
parser.add_argument('--filetype', type=int, default=1, help='type of txtfile, 0 means u,vside different, 1means u,vside same')
parser.add_argument('--output', default='none', help='result csv file path')
parser.add_argument('--noderesult', default='none', help='result node txt file path')

args = parser.parse_args()

if args.filetype == 1:
    G, U, V = read_bipartite_edgelist(args.network)
elif args.filetype == 0:
    G, U, V = read_bipartite_simple_edgelist(args.network)

if args.algorithm == "biflexi":
    start_time = time.time()
    G, E = biflexi.run(G, args.t, len(U), len(V), U, V)
    end_time = time.time()
    exec_time = end_time - start_time
    
    dataset = args.network.split('/')[-1]
    
    uside_count = sum(1 for n in G.nodes if G.nodes[n].get('bipartite') == 0)
    vside_count = sum(1 for n in G.nodes if G.nodes[n].get('bipartite') == 1)


    record = {
        'timestamp' : time.strftime('%Y-%m-%d %H:%M:%S'),
        'dataset' : dataset,
        'algorithm' : args.algorithm,
        'tau' : args.t,
        '#node' : len(G.nodes),
        '#Uside_node' : uside_count,
        '#Vside_node' : vside_count,
        '#edge' : E,
        'runtime_sec' : round(exec_time, 4),
    }
    
    if args.output != 'none':
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        file_exists = os.path.isfile(args.output)

        with open(args.output, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=record.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

        print(f"Result appended to {args.output}")
    else:
        print(f"{exec_time}_sec")
        print(f"#edges : {E}")
    
    if args.noderesult != 'none':
        os.makedirs(os.path.dirname(args.noderesult), exist_ok=True)

        with open(args.noderesult, 'w') as f:
            f.write("Uside\n")
            for node in G.nodes:
                if G.nodes[node]['bipartite'] == 0:
                    f.write(f"{node}\n")

            f.write("\nVside\n")
            for node in G.nodes:
                if G.nodes[node]['bipartite'] == 1:
                    f.write(f"{node}\n")
        
        print(f"Node list written to {args.noderesult}")