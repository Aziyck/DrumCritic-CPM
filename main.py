from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt


# definirea activitatilor
activities = {
    'A': {'duration': 2, 'pred': []},
    'B': {'duration': 2, 'pred': ['A']},
    'C': {'duration': 4, 'pred': ['A']},
    'D': {'duration': 3, 'pred': ['C']},
    'E': {'duration': 6, 'pred': ['B']},
    'F': {'duration': 2, 'pred': ['D', 'E']},
    'G': {'duration': 3, 'pred': ['F']},
    'H': {'duration': 1, 'pred': ['G']},
    'I': {'duration': 2, 'pred': ['F']}
}

# construire graf (lista succesorilor)
# graful o sa-l pastram ca lista succesorilor unui nod
# graph = {
#     'A': ['B', 'C'],
#     'B': ['E'],
#     'C': ['D'],
#     ...
# }
graph = defaultdict(list)
# numarul de dependente de intrari in acest nod
# in_degree = {
#     'A': 0,
#     'B': 1,
#     'C': 1,
#     'F': 2
#     ...
# }
in_degree = defaultdict(int)

# initializam in_degree
for act in activities:
    in_degree[act] = 0

# poulam in_degree si graph
for act, data in activities.items():
    for pred in data['pred']:
        graph[pred].append(act)
        in_degree[act] += 1


# graph	    - cine vine după mine
# in_degree	- de câte lucruri depind

# sortare topologica
queue = deque()
# topo_order - topological order - ordinea corecta de procesare a activitatilor
topo_order = []

# punem nodurile fără dependențe intr-o coada - acestea pot incepe imediat
for node in in_degree:
    if in_degree[node] == 0:
        queue.append(node)

# procesal coada (cum ar fi am executa activitatea)
while queue:
    node = queue.popleft()
    topo_order.append(node)
    
    # actualizam vecinii (daca am executat un predecesor sadem dependenta)
    for neigh in graph[node]:
        in_degree[neigh] -= 1
        # daca un nod ajunge la 0 il consideram il adaugam in coada ca sa-l executam la pasul urmator
        if in_degree[neigh] == 0:
            queue.append(neigh)

# FORWARD PASS (TE)
# Timpul cel mai devreme de incepere
# 👉 TE = „cât de devreme pot începe”
TE = {}
# Pentru o activitate X:
# TE(X) = max(TE(predecesor) + durata(X))

# parcurgem in ordine topologica (garantat: predecesorii sunt calculați deja)
for node in topo_order:
    if not activities[node]['pred']:
        # Daca activitatea nu are predecesori activitatea incepe de la 0 
        TE[node] = 0
    else:
        # pentru toti predecesorii nodului in cauza
        # Calculam maximul dintre
        # Timpului lui cel mai devreme + durata lui
        # max {Timin + tij}
        TE[node] = max(TE[p] + activities[p]['duration'] for p in activities[node]['pred'])

# calcul durata totala proiect
# proiectul se termina cand se termina cea mai tarzie activitate
# asa ca pentru toate activitatile calculam
# max {Timin + tij}
project_duration = max(TE[node] + activities[node]['duration'] for node in activities)

# BACKWARD PASS (TT)
# Timpul cel mai târziu de incepere
# 👉 TT = „cât de târziu pot începe fără probleme”
TT = {}
# Pentru o activitate X:
# TT(X) = min(TT(succesor) - durata(X))

# parcurgem in ordine invers topologoca 
for node in reversed(topo_order):
    # Daca e ultimul nod din graf (adica nu are succesori)
    if node not in graph or len(graph[node]) == 0:
        # atunci trbuie sa termine fix la finalul proiectului 
        TT[node] = project_duration - activities[node]['duration']
    else:
        # pentru toti succesorii nodului in cauze
        # calculam minumul dintre 
        # timpul cel mai tarziu - durata lui
        # min {Timax - tij}
        TT[node] = min(TT[s] - activities[node]['duration'] for s in graph[node])

# calcul rezerva totala (RT)
# 👉 RT = cât poate fi întârziată o activitate fără să întârzie proiectul
RT = {}
for node in activities:
    #   TE → când poate începe cel mai devreme
    #   TT → când poate începe cel mai târziu
    #   diferența dintre ele = „spațiul de manevră”
    RT[node] = TT[node] - TE[node]

# calcul rezerva libera (RL)
# 👉 RL (rezerva liberă) = cât poate fi întârziată o activitate fără să afecteze începutul activităților următoare
# TE - timpul cel mai devreme ed incepere
# RL = min(TE succesor) - (TE activitate + durata)
RL = {}
# pentru fiecare nod
for node in activities:
    # daca nu are succesori - nu afectează pe nimeni → RL = RT
    if node not in graph or len(graph[node]) == 0:
        RL[node] = RT[node]  # ultima activitate
    else:
        # Pentru fiecare activitate
        # Calculăm când se termină:                 finish = TE + durata
        # Vedem când încep succesorii:              TE(s)
        # Alegem cel mai devreme (strict) succesor: min(TE[s])
        # Calculam diferenta min(TE[s]) - finish
        RL[node] = min(TE[s] for s in graph[node]) - (TE[node] + activities[node]['duration'])

# identificare drum critic
# Daca rezerva totata la vre-o activitate este 0 inseapna ca face parte din drumul critic
critical_path = [node for node in topo_order if RT[node] == 0]

# afisare rezultate
# culori ANSI
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"
print()
print(BOLD + GREEN +" TE " + RESET  + "→ " + YELLOW + "Timpul cel mai devreme de incepere " + RESET + "→ Cât de devreme pot începe.")
print(BOLD + GREEN +" TT " + RESET  + "→ " + YELLOW + "Timpul cel mai târziu de incepere  " + RESET + "→ Cât de târziu pot începe fără probleme.")
print(BOLD + GREEN +" RT " + RESET  + "→ " + YELLOW + "Rezerva totala                     " + RESET + "→ Cât poate fi întârziată o activitate fără să întârzie proiectul.")
print(BOLD + GREEN +" RL " + RESET  + "→ " + YELLOW + "Rezerva libera                     " + RESET + "→ Cât poate fi întârziată o activitate fără să afecteze începutul activităților următoare.")

print(BOLD + "\nActivitati:" + RESET)

# header
print(BOLD + f"{'Act':^5}{'Dur':^7}{'TE(St)':^7}{'(End)':^7}{'TT':^7}{'RT':^7}{'RL':^7}" + RESET)
print("-" * 47)

for node in topo_order:
    dur = activities[node]['duration']
    
    # colorare in functie de RT
    if RT[node] == 0:
        node_str = RED + f"{node:^5}" + RESET
    elif RT[node] <= 1:
        node_str = YELLOW + f"{node:^5}" + RESET
    else:
        node_str = GREEN + f"{node:^5}" + RESET
    
    print(f"{node_str}{dur:^7}{TE[node]:^7}{(TE[node] + dur):^7}{TT[node]:^7}{RT[node]:^7}{RL[node]:^7}")

print("\n" + BOLD + "Drum critic:" + RESET)
print(RED + (RESET + " → " + RED).join(critical_path) + RESET)

print(BOLD + f"\nDurata proiect: {GREEN}{project_duration}\n" + RESET)



# creare graf orientat
G = nx.DiGraph()

# adaugare noduri cu info
for act in activities:
    label = f"{act}\n{activities[act]['duration']}"
    G.add_node(act, label=label)

# adaugare muchii (dependente)
for act, data in activities.items():
    for pred in data['pred']:
        G.add_edge(pred, act)

# pozitionare noduri
pos = nx.spring_layout(G, seed=1, k=3.0)

# etichete noduri
labels = nx.get_node_attributes(G, 'label')

critical_edges = []
for u, v in G.edges():
    if RT[u] == 0 and RT[v] == 0:
        critical_edges.append((u, v))

# noduri
nx.draw(G, pos, with_labels=False, node_size=3000)

# etichete
nx.draw_networkx_labels(G, pos, labels)

# muchii critice (rosu)
nx.draw_networkx_edges(G, pos, edgelist=critical_edges, edge_color='red', width=2)

plt.show()