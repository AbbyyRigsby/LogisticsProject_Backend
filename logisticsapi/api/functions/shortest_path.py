import pandas as pd
import networkx as nx

def find_shortest_path(graph, start_point, end_point):
    path_nodes = nx.dijkstra_path(graph, start_point, end_point, weight='weight')
    distance = nx.dijkstra_path_length(graph, start_point, end_point, weight='weight')

    detailed_path = []
    # This will be used by mapping libraries to draw the line (Polyline)
    map_coordinates = [] 

    for node in path_nodes:
        attrs = graph.nodes[node]
        
        # Add to detailed path
        node_details = {
            "name": node,
            "latitude": attrs.get("latitude"),
            "longitude": attrs.get("longitude"),
            "country_code": attrs.get("country_code"),
            "category": attrs.get("category")
        }
        detailed_path.append(node_details)
        
        # Add to coordinate list for the map
        map_coordinates.append([attrs.get("latitude"), attrs.get("longitude")])

    return {
        "start_point": start_point,
        "end_point": end_point,
        "distance_miles": int(round(distance)),
        "map_polyline": map_coordinates,  # New map-ready field
        "path_details": detailed_path
    }