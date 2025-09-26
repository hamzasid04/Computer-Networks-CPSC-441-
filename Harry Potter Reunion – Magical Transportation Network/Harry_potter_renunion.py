#Assignment 4
#Hamza Siddiqui
#UCID: 30183881
"""
1. Builds a graph of provinces (nodes) and magical paths (edges).
2. Calculates 4 optimal paths (SHP, SDP, STP, FDP) for EACH alumni's from their
   starting province to Ottawa.
3. Prints each alumnus' path in the console.
4. Visualizes the network in 4 subplots (one per metric) showing:
   - The full network with nodes and bold edge labels (distance).
   - Each alumnus's optimal path in a distinct color, drawn with a unique arc offset so we ensure that ther is no 
     overlapping edges and the edges do not hide each other.
   - Small table with it's appropriate values placed to the right of each subplot, with the alumnus’s name, starting province
     (with NL instead of "Newfoundland and Labrador"), and cost (with appropriate units).
"""

import heapq
from collections import deque
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.lines as mlines

###############################################################################
#                          GRAPH & PATHFINDING CLASS
###############################################################################
class MagicalGraph:
    def __init__(self):
        self.nodes = set() # Set of provinces or nodes
        self.edges = {}

    def add_edge(self, start, end, hops, distance, time, dementors):
        # Add nodes (using abbreviations if needed)
        self.nodes.add(start)
        self.nodes.add(end)
         # Create an edge with its necessary attributes

        edge = {
            "destination": end,
            "hops": hops,
            "distance": distance,
            "time": time,
            "dementors": dementors
        }
        # Add the edge to the dictionary

        if start not in self.edges:
            self.edges[start] = []
        self.edges[start].append(edge)
    
    def build_graph(self, data):
                # Build graph from list of dictionaries (one per edge)

        for entry in data:
            self.add_edge(
                entry['start'],
                entry['end'],
                entry['hops'],
                entry['distance'],
                entry['time'],
                entry['dementors']
            )
    
    def display_graph(self):
                # Print all nodes and edges in terminal (for debugging)

        print("Nodes (Provinces):")
        for node in sorted(self.nodes):
            print(" -", node)
        print("\nEdges (Magical Paths):")
        for start, edge_list in self.edges.items():
            for edge in edge_list:
                print(f"{start} -> {edge['destination']} | Hops: {edge['hops']}, "
                      f"Distance: {edge['distance']} km, Time: {edge['time']} hrs, "
                      f"Dementors: {edge['dementors']}")

    ###########################################################################
    #                         PATHFINDING ALGORITHMS
    ###########################################################################
    # BFS for Shortest Hop Path (SHP) and unweighted paths

    def shortest_hop_path(self, start, goal):
        queue = deque([(start, [start])])
        visited = set()
        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path
            visited.add(current)
            for edge in self.edges.get(current, []):
                neighbor = edge['destination']
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        return None
    
    # Generic Dijkstra's algorithm for weighted paths
    def dijkstra(self, start, goal, cost_function):
        heap = [(0, start, [start])]
        visited = {}
        while heap:
            cost, current, path = heapq.heappop(heap)
            if current == goal:
                return path, cost
            if current in visited and visited[current] <= cost:
                continue
            visited[current] = cost
            for edge in self.edges.get(current, []):
                neighbor = edge['destination']
                new_cost = cost + cost_function(edge)
                heapq.heappush(heap, (new_cost, neighbor, path + [neighbor]))
        return None, float('inf')

    def shortest_distance_path(self, start, goal):
        return self.dijkstra(start, goal, lambda edge: edge['distance'])
    
    def shortest_time_path(self, start, goal):
        return self.dijkstra(start, goal, lambda edge: edge['time'])
    
    def fewest_dementors_path(self, start, goal):
        return self.dijkstra(start, goal, lambda edge: edge['dementors'])


###############################################################################
#               VISUALIZATION: ALL ALUMNI PATHS ON 4 SUBPLOTS
###############################################################################
    # Convert custom graph to NetworkX DiGraph

def visualize_all_alumni_paths(magical_graph, alumni_paths, alumni_locations):
    """
    Creates a 2x2 grid of subplots (one per metric: SHP, SDP, STP, FDP).
    Each subplot shows:
      - The full network with nodes and bold edge labels (distance).
      - Each alumnus's optimal path in a distinct color, drawn with a unique arc offset.
      - A taable placed outside the plot, showing the alumnus's name, starting province,
        and cost with appropriate units.
    """
    # Convert our custom graph into a NetworkX DiGraph.
    G = nx.DiGraph()
    for node in magical_graph.nodes:
        G.add_node(node)
    for start, edges in magical_graph.edges.items():
        for edge in edges:
            G.add_edge(
                start, edge["destination"],
                hops=edge["hops"],
                distance=edge["distance"],
                time=edge["time"],
                dementors=edge["dementors"]
            )
    
    # Use Kamada-Kawai layout for better graph representation
    try:
        pos = nx.kamada_kawai_layout(G)
    except ImportError:
        pos = nx.spring_layout(G, seed=42, k=2, iterations=50)

    # Create 2x2 subplots with increased width for legends.
    fig, axes = plt.subplots(2, 2, figsize=(18, 10))
    axes = axes.flatten()

    metrics_order = ["SHP", "SDP", "STP", "FDP"]
    metric_titles = {
        "SHP": "Shortest Hop Path",
        "SDP": "Shortest Distance Path",
        "STP": "Shortest Time Path",
        "FDP": "Fewest Dementors Path"
    }

    # Appropriate units for each metric.
    units_for_metric = {
        "SHP": "Hops",
        "SDP": "km",
        "STP": "hrs",
        "FDP": ""  # No unit.
    }

    # Define arc offsets for each alumnus to offset overlapping edges so no edges are hidden.
    alumnus_arc = {
        "Harry Potter": 0.00,
        "Hermione Granger": 0.15,
        "Ron Weasley": -0.15,
        "Luna Lovegood": 0.30,
        "Neville Longbottom": -0.30,
        "Ginny Weasley": 0.45
    }

    # Color map for alumni.
    alumni_colors = {
        "Harry Potter": "red",
        "Hermione Granger": "green",
        "Ron Weasley": "blue",
        "Luna Lovegood": "magenta",
        "Neville Longbottom": "orange",
        "Ginny Weasley": "cyan"
    }

    for i, metric in enumerate(metrics_order):
        ax = axes[i]
        ax.set_title(metric_titles[metric], fontsize=13)

        # Draw the base network.
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color="#A0CBE2", node_size=400)
        nx.draw_networkx_edges(
            G, pos, ax=ax, edge_color="gray", width=1, arrows=True,
            arrowstyle='-|>', arrowsize=15
        )
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_color="black")

        # Prepare edge labels (distance).
        edge_labels = {(u, v): f"{d['distance']} km" for u, v, d in G.edges(data=True)}

        # Collect legend lines.
        legend_lines = []
        for alumnus, (path, cost) in alumni_paths[metric].items():
            if not path or cost is None:
                continue
            color = alumni_colors.get(alumnus, "black")
            path_edges = list(zip(path, path[1:]))
            # Get arc offset for this alumnus.
            rad = alumnus_arc.get(alumnus, 0.0)
            nx.draw_networkx_edges(
                G, pos, ax=ax, edgelist=path_edges,
                edge_color=color, width=3, arrows=True,
                arrowstyle='-|>', arrowsize=15,
                connectionstyle=f"arc3,rad={rad}"
            )
            start_province = alumni_locations.get(alumnus, "Unknown")
            metric_unit = units_for_metric[metric]
            if metric_unit:
                legend_label = f"{alumnus} ({start_province}) ({cost} {metric_unit})"
            else:
                legend_label = f"{alumnus} ({start_province}) ({cost})"
            legend_line = mlines.Line2D([], [], color=color, label=legend_label, linewidth=3)
            legend_lines.append(legend_line)

        if legend_lines:
            ax.legend(
                handles=legend_lines, fontsize=8,
                loc="upper left", bbox_to_anchor=(1.05, 1),
                borderaxespad=0.0, framealpha=0.8
            )

        # Draw edge labels last with bold font weight.
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax, edge_labels=edge_labels,
            font_size=7, font_weight="bold",
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none"),
            label_pos=0.5
        )

        ax.axis("off")

    plt.tight_layout()
    plt.show()


###############################################################################
#                             MAIN PROGRAM
###############################################################################
if __name__ == "__main__":
    # 1) Build the Graph from the table of values given in assignment
    magical_paths_data = [
        {"start": "British Columbia", "end": "Saskatchewan", "hops": 13, "distance": 1800, "time": 19, "dementors": 6},
        {"start": "Alberta", "end": "Quebec", "hops": 3, "distance": 2000, "time": 21, "dementors": 7},
        {"start": "Ontario", "end": "Nova Scotia", "hops": 2, "distance": 1300, "time": 13, "dementors": 4},
        {"start": "Quebec", "end": "NL", "hops": 13, "distance": 1900, "time": 20, "dementors": 26},
        {"start": "Nova Scotia", "end": "Saskatchewan", "hops": 2, "distance": 1800, "time": 18, "dementors": 5},
        {"start": "Alberta", "end": "Saskatchewan", "hops": 6, "distance": 1600, "time": 8, "dementors": 3},
        {"start": "NL", "end": "Alberta", "hops": 4, "distance": 2400, "time": 24, "dementors": 9},
        {"start": "Ontario", "end": "Quebec", "hops": 10, "distance": 500, "time": 5, "dementors": 1},
        {"start": "Nova Scotia", "end": "Ontario", "hops": 3, "distance": 2000, "time": 21, "dementors": 7},
        {"start": "Saskatchewan", "end": "Nova Scotia", "hops": 3, "distance": 2000, "time": 20, "dementors": 37},
        {"start": "Quebec", "end": "Saskatchewan", "hops": 4, "distance": 200, "time": 2, "dementors": 0},
        {"start": "Alberta", "end": "Ottawa", "hops": 3, "distance": 2400, "time": 24, "dementors": 9},
        {"start": "Saskatchewan", "end": "Quebec", "hops": 2, "distance": 2000, "time": 20, "dementors": 6},
        {"start": "Ontario", "end": "Alberta", "hops": 2, "distance": 1500, "time": 16, "dementors": 4},
        {"start": "British Columbia", "end": "Saskatchewan", "hops": 2, "distance": 1200, "time": 14, "dementors": 3},
        {"start": "NL", "end": "Quebec", "hops": 3, "distance": 2200, "time": 22, "dementors": 7},
        {"start": "Nova Scotia", "end": "NL", "hops": 10, "distance": 1200, "time": 12, "dementors": 6},
        {"start": "Quebec", "end": "Ottawa", "hops": 29, "distance": 1800, "time": 19, "dementors": 17},
        {"start": "Alberta", "end": "British Columbia", "hops": 2, "distance": 1800, "time": 18, "dementors": 27},
        {"start": "British Columbia", "end": "Quebec", "hops": 2, "distance": 1900, "time": 19, "dementors": 7},
        {"start": "Ontario", "end": "NL", "hops": 3, "distance": 2300, "time": 23, "dementors": 8},
        {"start": "Nova Scotia", "end": "Alberta", "hops": 3, "distance": 2200, "time": 22, "dementors": 8},
        {"start": "NL", "end": "Alberta", "hops": 3, "distance": 2300, "time": 23, "dementors": 8},
        {"start": "Alberta", "end": "NL", "hops": 3, "distance": 2400, "time": 24, "dementors": 9},
        {"start": "Saskatchewan", "end": "British Columbia", "hops": 3, "distance": 2000, "time": 21, "dementors": 8},
        {"start": "Ontario", "end": "Saskatchewan", "hops": 2, "distance": 1600, "time": 16, "dementors": 5},
        {"start": "Quebec", "end": "Nova Scotia", "hops": 2, "distance": 1000, "time": 10, "dementors": 2},
        {"start": "NL", "end": "Saskatchewan", "hops": 4, "distance": 2200, "time": 23, "dementors": 19},
        {"start": "Nova Scotia", "end": "Quebec", "hops": 2, "distance": 1100, "time": 11, "dementors": 2},
        {"start": "British Columbia", "end": "NL", "hops": 4, "distance": 2500, "time": 26, "dementors": 10},
        {"start": "Ontario", "end": "Ottawa", "hops": 7, "distance": 1450, "time": 4, "dementors": 12},
        {"start": "Alberta", "end": "Saskatchewan", "hops": 5, "distance": 600, "time": 8, "dementors": 3},
        {"start": "Quebec", "end": "Alberta", "hops": 2, "distance": 1700, "time": 17, "dementors": 6},
        {"start": "Saskatchewan", "end": "Nova Scotia", "hops": 9, "distance": 1800, "time": 18, "dementors": 5},
        {"start": "Alberta", "end": "Quebec", "hops": 6, "distance": 2000, "time": 21, "dementors": 6},
        {"start": "Nova Scotia", "end": "British Columbia", "hops": 4, "distance": 2500, "time": 26, "dementors": 10},
        {"start": "Ontario", "end": "Nova Scotia", "hops": 12, "distance": 1300, "time": 13, "dementors": 4},
        {"start": "British Columbia", "end": "Saskatchewan", "hops": 13, "distance": 1800, "time": 19, "dementors": 6}
    ]

    graph = MagicalGraph()
    graph.build_graph(magical_paths_data)

    # 2) Alumni Starting Points (using "NL" abbreviation)
    alumni_locations = {
        "Harry Potter": "British Columbia",
        "Hermione Granger": "Ontario",
        "Ron Weasley": "Quebec",
        "Luna Lovegood": "NL",
        "Neville Longbottom": "Saskatchewan",
        "Ginny Weasley": "Nova Scotia"
    }

    destination = "Ottawa"

    # 3) Calculate 4 Optimal Paths for EACH Alumnus
    alumni_paths = {
        "SHP": {},
        "SDP": {},
        "STP": {},
        "FDP": {}
    }

    for alumnus, start_province in alumni_locations.items():
        print("=" * 60)
        print(f"Optimal Paths for {alumnus} (Starting from {start_province}) to {destination}")
        print("-" * 60)

        # SHP: BFS for fewest hops
        shp_path = graph.shortest_hop_path(start_province, destination)
        shp_cost = (len(shp_path) - 1) if shp_path else None
        alumni_paths["SHP"][alumnus] = (shp_path, shp_cost)
        if shp_path:
            print("Shortest Hop Path (SHP):")
            print("  " + " -> ".join(shp_path) + f"  (Hops: {shp_cost})")
        else:
            print("Shortest Hop Path (SHP): No path found.")

        # SDP: Dijkstra for distance
        sdp_path, sdp_cost = graph.shortest_distance_path(start_province, destination)
        alumni_paths["SDP"][alumnus] = (sdp_path, sdp_cost if sdp_path else None)
        if sdp_path:
            print("Shortest Distance Path (SDP):")
            print("  " + " -> ".join(sdp_path) + f"  (Total Distance: {sdp_cost} km)")
        else:
            print("Shortest Distance Path (SDP): No path found.")

        # STP: Dijkstra for time
        stp_path, stp_cost = graph.shortest_time_path(start_province, destination)
        alumni_paths["STP"][alumnus] = (stp_path, stp_cost if stp_path else None)
        if stp_path:
            print("Shortest Time Path (STP):")
            print("  " + " -> ".join(stp_path) + f"  (Total Time: {stp_cost} hrs)")
        else:
            print("Shortest Time Path (STP): No path found.")

        # FDP: Dijkstra for dementors
        fdp_path, fdp_cost = graph.fewest_dementors_path(start_province, destination)
        alumni_paths["FDP"][alumnus] = (fdp_path, fdp_cost if fdp_path else None)
        if fdp_path:
            print("Fewest Dementors Path (FDP):")
            print("  " + " -> ".join(fdp_path) + f"  (Total Dementors: {fdp_cost})")
        else:
            print("Fewest Dementors Path (FDP): No path found.")

        print("=" * 60 + "\n")

    # 4) Visualize All Alumni Paths
    visualize_all_alumni_paths(graph, alumni_paths, alumni_locations)
