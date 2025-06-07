import math

class Node:
    __slots__ = ['id', 'left', 'right', 'parent', 'rev']
    def __init__(self, id):
        self.id = id
        self.left = None
        self.right = None
        self.parent = None
        self.rev = False
def is_root(x):
    return (x.parent is None) or (x.parent.left != x and x.parent.right != x)
def push(x):
    if x and x.rev:
        x.left, x.right = x.right, x.left
        if x.left:
            x.left.rev ^= True
        if x.right:
            x.right.rev ^= True
        x.rev = False
def update(x):
    pass
def rotate(x):
    p = x.parent
    g = p.parent
    push(p)
    push(x)
    if p.left == x:
        p.left = x.right
        if x.right:
            x.right.parent = p
        x.right = p
    else:
        p.right = x.left
        if x.left:
            x.left.parent = p
        x.left = p
    p.parent = x
    x.parent = g
    if g:
        if g.left == p:
            g.left = x
        elif g.right == p:
            g.right = x
    update(p)
    update(x)
def splay(x):
    while not is_root(x):
        p = x.parent
        g = p.parent
        if not is_root(p):
            if (g.left == p) == (p.left == x):
                rotate(p)  # zig-zig
            else:
                rotate(x)  # zig-zag
        rotate(x)
    push(x)
    update(x)
def access(x):
    last = None
    y = x
    while y:
        splay(y)
        y.right = last
        update(y)
        last = y
        y = y.parent
    splay(x)
    return last
def make_root(x):
    access(x)
    x.rev ^= True
    push(x)
def find_root(x):
    access(x)
    while x.left:
        push(x)
        x = x.left
    splay(x)
    return x
def connected_lct(x, y):
    return find_root(x) == find_root(y)
def link_lct(x, y):
    make_root(x)
    if find_root(y) != x:
        x.parent = y
def cut_lct(x, y):
    make_root(x)
    access(y)
    if y.left == x:
        y.left.parent = None
        y.left = None
    update(y)
class LinkCutTree:
    def __init__(self, n):
        self.n = n
        self.nodes = [Node(i) for i in range(n)]
    def connected(self, u, v):
        return connected_lct(self.nodes[u], self.nodes[v])
    def link(self, u, v):
        if not self.connected(u, v):
            link_lct(self.nodes[u], self.nodes[v])
    def cut(self, u, v):
        # try in bidirection
        make_root(self.nodes[u])
        access(self.nodes[v])
        if self.nodes[v].left == self.nodes[u]:
            self.nodes[v].left.parent = None
            self.nodes[v].left = None
            update(self.nodes[v])
        else:
            make_root(self.nodes[v])
            access(self.nodes[u])
            if self.nodes[u].left == self.nodes[v]:
                self.nodes[u].left.parent = None
                self.nodes[u].left = None
                update(self.nodes[u])
class FullyDynamicConnectivity:
    def __init__(self, n):
        self.n = n
        self.comp_count = n
        self.L = math.ceil(math.log2(n)) if n > 1 else 1  # maximum level
        self.forests = [LinkCutTree(n) for _ in range(self.L + 1)]
        self.non_tree_edges = [set() for _ in range(self.L + 1)]
        self.edge_level = {}
        self.is_tree_edge = {}
    def insert_edge(self, u, v):
        if u > v:
            u, v = v, u
        if (u, v) in self.edge_level:
            return
        level = 0
        self.edge_level[(u, v)] = 0
        if not self.forests[0].connected(u, v):
            for i in range(0, self.L + 1):
                self.forests[i].link(u, v)
            self.is_tree_edge[(u, v)] = True
            self.comp_count -= 1  # combine in two component
        else:
            self.non_tree_edges[0].add((u, v))
            self.is_tree_edge[(u, v)] = False
    def delete_edge(self, u, v):
        if u > v:
            u, v = v, u
        if (u, v) not in self.edge_level:
            return
        level = self.edge_level[(u, v)]
        del self.edge_level[(u, v)]
        if not self.is_tree_edge[(u, v)]:
            self.non_tree_edges[level].discard((u, v))
            del self.is_tree_edge[(u, v)]
        else:
            for i in range(level, self.L + 1):
                if self.forests[i].connected(u, v):
                    self.forests[i].cut(u, v)
            del self.is_tree_edge[(u, v)]
            replacement = None
            rep_level = None
            for l in range(level, -1, -1):
                for e in list(self.non_tree_edges[l]):
                    x, y = e
                    if not self.forests[l].connected(x, y):
                        replacement = e
                        rep_level = l
                        break
                if replacement is not None:
                    break
            if replacement is not None:
                self.non_tree_edges[rep_level].remove(replacement)
                self.is_tree_edge[replacement] = True
                for i in range(rep_level, self.L + 1):
                    if not self.forests[i].connected(replacement[0], replacement[1]):
                        self.forests[i].link(replacement[0], replacement[1])
            else:
                self.comp_count += 1
            for l in range(level + 1):
                to_promote = []
                for e in list(self.non_tree_edges[l]):
                    x, y = e
                    if self.forests[l].connected(x, y):
                        to_promote.append(e)
                for e in to_promote:
                    self.non_tree_edges[l].remove(e)
                    new_level = l + 1
                    if new_level <= self.L:
                        self.non_tree_edges[new_level].add(e)
                        self.edge_level[e] = new_level
                    else:
                        if e in self.edge_level:
                            del self.edge_level[e]
    def connected(self, u, v):
        return self.forests[0].connected(u, v)
    def get_component_count(self):
        return self.comp_count