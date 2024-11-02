from pathlib import Path
import numpy as np
import json
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
#from matplotlib.offsetbox import OffsetImage, AnnotationBbox
#import networkx as nx
#import matplotlib.patheffects as PathEffects
#import base64
#from io import BytesIO
#from lxml import etree
#from matplotlib.patches import Rectangle

def get_next_world_folder():
    base_dir = Path("generated_VNs")
    base_dir.mkdir(parents=True, exist_ok=True)

    n = 1
    while True:
        folder_name = base_dir / f"world_{n}"
        if not folder_name.exists():
            return folder_name
        n += 1

def minutes_from_time(time_str):
    hours, minutes = map(int, time_str.split(':'))
    total_minutes = hours * 60 + minutes
    return total_minutes

def time_from_minutes(minutes):
    hours = (minutes // 60) % 24
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}"

def split_char_generations(x, y):
    result = []

    while x > 0 or y > 0:
        if x >= 4:
            result.append([4, 0])
            x -= 4
        elif y >= 4:
            result.append([0, 4])
            y -= 4
        elif x >= 2 and y >= 2:
            result.append([2, 2])
            x -= 2
            y -= 2
        else:
            result.append([x, y])
            break

    return result

def createAdjacencyMatrix(locationArray):
    N = len(locationArray)
    locationIndex = {location['locationName']: idx for idx, location in enumerate(locationArray)}
    adjacencyMatrix = np.zeros((N, N), dtype=bool)
    for idx, location in enumerate(locationArray):
        for adjacent in location['adjacentLocations']:
            if adjacent in locationIndex:
                adjacencyMatrix[idx, locationIndex[adjacent]] = True
    adjacencyMatrix = np.logical_or(adjacencyMatrix, adjacencyMatrix.T)
    return adjacencyMatrix.tolist()

def find_connected_components(adjacencyMatrix):
    """Helper function to find all connected components in the graph"""
    N = len(adjacencyMatrix)
    visited = [False] * N
    components = []

    def dfs(v, component):
        stack = [v]
        while stack:
            node = stack.pop()
            if not visited[node]:
                visited[node] = True
                component.append(node)
                for neighbor, connected in enumerate(adjacencyMatrix[node]):
                    if connected and not visited[neighbor]:
                        stack.append(neighbor)

    for v in range(N):
        if not visited[v]:
            component = []
            dfs(v, component)
            components.append(component)

    return components

def add_edge(adjacencyMatrix, u, v):
    """Helper function to add an edge to the adjacency matrix"""
    adjacencyMatrix[u][v] = True
    adjacencyMatrix[v][u] = True

def find_vertex_with_least_connections(adjacencyMatrix, vertices):
    """Helper function to find the vertex with the least connections"""
    min_connections = float('inf')
    min_vertex = -1
    for v in vertices:
        connections = sum(adjacencyMatrix[v])
        if connections < min_connections:
            min_connections = connections
            min_vertex = v
    return min_vertex

def find_vertex_with_most_connections(adjacencyMatrix, vertices):
    """Helper function to find the vertex with the most connections"""
    max_connections = -1
    max_vertex = -1
    for v in vertices:
        connections = sum(adjacencyMatrix[v])
        if connections > max_connections:
            max_connections = connections
            max_vertex = v
    return max_vertex

def connect_components(adjacencyMatrix, isHubArea):
    N = len(adjacencyMatrix)
    components = find_connected_components(adjacencyMatrix)

    if len(components) == 1:
        return adjacencyMatrix  # Already connected

    # Check for the first condition: two distinct connected components each with a hub area
    hub_components = []
    for component in components:
        if any(isHubArea[v] for v in component):
            hub_components.append(component)
    
    if len(hub_components) >= 2:
        # Find the least connected hub area in each hub component and connect them
        hub_area_pairs = []
        for component in hub_components:
            hub_areas = [v for v in component if isHubArea[v]]
            if hub_areas:
                least_connected_hub = find_vertex_with_least_connections(adjacencyMatrix, hub_areas)
                hub_area_pairs.append((least_connected_hub, component))
        
        if len(hub_area_pairs) >= 2:
            u, comp_u = hub_area_pairs[0]
            v, comp_v = hub_area_pairs[1]
            add_edge(adjacencyMatrix, u, v)
            return adjacencyMatrix

    # Check for the second condition: all hub areas in the same component
    main_hub_component = hub_components[0]
    other_component = components[1]
    if len(hub_components) == 1 and len(components) > 1:
        main_hub_areas = [v for v in main_hub_component if isHubArea[v]]
        other_vertices = [v for v in other_component]

        if main_hub_areas and other_vertices:
            least_connected_hub = find_vertex_with_least_connections(adjacencyMatrix, main_hub_areas)
            most_connected_other = find_vertex_with_most_connections(adjacencyMatrix, other_vertices)
            add_edge(adjacencyMatrix, least_connected_hub, most_connected_other)
            return adjacencyMatrix

    return adjacencyMatrix

def find_adjacent_locations(locationArray, currentLocation, adjacencyMatrix):
    current_index = next((index for (index, d) in enumerate(locationArray) if d["locationName"] == currentLocation), None)
    adjacent_indices = [i for i, adjacent in enumerate(adjacencyMatrix[current_index]) if adjacent]
    adjacent_location_names = [locationArray[i]["locationName"] for i in adjacent_indices]
    return adjacent_location_names

def getBackgroundFilePath(output_dir, currentLocationDict, currentTimeMins):
        if 420 <= currentTimeMins < 1260:
            return output_dir.as_posix() + "/locationImages/location_" + f"{str(currentLocationDict.get('locationNumber'))}_day"
        else:
            return output_dir.as_posix() + "/locationImages/location_" + f"{str(currentLocationDict.get('locationNumber'))}_night"

def get_location_text_description(locationArray, locationName):
    for location in locationArray:
        if location['locationName'] == locationName:
            return location['locationTextDescription']
    return None

def trimContext(maxContext, storySoFar):
    total_length = sum(len(item['content']) for item in storySoFar)

    if total_length <= maxContext:
        return storySoFar

    trimmed_length = 0
    trimmed_array = []

    for item in reversed(storySoFar):
        content_length = len(item['content'])
        if trimmed_length + content_length <= maxContext:
            trimmed_array.insert(0, item)  # Insert at the beginning to maintain original order
            trimmed_length += content_length
        else:
            break

    return trimmed_array

def process_json_array(json_array):
    # Step 1: Change "system" roles to "user" with content encapsulated
    for item in json_array:
        if item['role'] == 'system':
            item['role'] = 'user'
            item['content'] = f"[System message: {item['content']}]"
    
    # Step 2: Merge adjacent dictionaries with the same role
    processed_array = []
    current_role = None
    current_content = []

    for item in json_array:
        if item['role'] == current_role:
            current_content.append(item['content'])
        else:
            if current_role is not None:
                processed_array.append({
                    'role': current_role,
                    'content': '\n'.join(current_content)
                })
            current_role = item['role']
            current_content = [item['content']]

    if current_role is not None:
        processed_array.append({
            'role': current_role,
            'content': '\n'.join(current_content)
        })

    return processed_array

def scheduleMerge(initialSchedule, insertSchedule):
    def minutes_from_time(time_str):
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def time_from_minutes(minutes):
        hours = (minutes // 60) % 24
        minutes = minutes % 60
        return f"{hours:02}:{minutes:02}"

    # Add "firstEntry": "Yes" to the first entry in insertSchedule
    if insertSchedule:
        insertSchedule[0]["firstEntry"] = "Yes"

    # Capture the endTime from the insertSchedule
    insert_end_time = insertSchedule[-1].get('endTime')
    if insert_end_time is None:
        raise ValueError("End time missing from insertSchedule")

    insert_end_minutes = minutes_from_time(insert_end_time)
    
    # Find the event in the initial schedule that should resume
    resume_event = None
    for event in initialSchedule:
        event_start_time = minutes_from_time(event['startTime'])
        if event_start_time < insert_end_minutes:
            resume_event = event

    # Merge schedules
    mergedSchedule = []
    i, j = 0, 0
    initial_len = len(initialSchedule)
    insert_len = len(insertSchedule)

    while i < initial_len and j < insert_len:
        initial_start = minutes_from_time(initialSchedule[i]['startTime'])
        insert_start = minutes_from_time(insertSchedule[j]['startTime'])

        if initial_start < insert_start:
            mergedSchedule.append(initialSchedule[i])
            i += 1
        else:
            mergedSchedule.append(insertSchedule[j])
            j += 1

    # Append any remaining events from both schedules
    while i < initial_len:
        mergedSchedule.append(initialSchedule[i])
        i += 1

    while j < insert_len:
        mergedSchedule.append(insertSchedule[j])
        j += 1

    # Ensure the event resumes at the insert_end_time
    if resume_event:
        resumed_event = {k: v for k, v in resume_event.items()}  # Create a new dictionary manually
        resumed_event['startTime'] = insert_end_time
        mergedSchedule.append(resumed_event)

    # Sort the merged schedule by startTime
    mergedSchedule.sort(key=lambda event: minutes_from_time(event['startTime']))

    # Update the entry before the firstEntry
    for index, event in enumerate(mergedSchedule):
        if "firstEntry" in event:
            if index > 0:
                prev_event = mergedSchedule[index - 1]
                prev_event["future_plans"] = f"At {event['startTime']}, at {event['location']}: planning on {event['activity']}, medium priority"
            break

    # Update the entry with endTime
    for index, event in enumerate(mergedSchedule):
        if "endTime" in event:
            if index < len(mergedSchedule) - 1:
                next_event = mergedSchedule[index + 1]
                event["future_plans"] = f"At {next_event['startTime']}, at {next_event['location']}: planning on {next_event['activity']}, medium priority"

    # Remove "firstEntry" and "endTime" attributes
    for event in mergedSchedule:
        event.pop("firstEntry", None)
        event.pop("endTime", None)

    return mergedSchedule

#def add_image_at_node(ax, pos, node_label, image_file, zoom, rect_id, rectangles_by_coords):
#    """Function to add image corresponding to a node at the node's position."""
#    image = mpimg.imread(image_file)
#    imagebox = OffsetImage(image, zoom=zoom, interpolation='bicubic')  # Adjust zoom to scale image size
#    ab = AnnotationBbox(imagebox, pos, frameon=False)
#    ax.add_artist(ab)

#    image_height, image_width, _ = image.shape
#    image_width *= zoom
#    image_height *= zoom
    
#    rect = Rectangle(
#        (pos[0] - image_width / 2, pos[1] - image_height / 2),  # Bottom-left corner position
#        image_width,  # Width
#        image_height,  # Height
#        linewidth=1, edgecolor='black', facecolor='none'
#    )

#    ax.add_patch(rect)
#    rectangles_by_coords[rect_id] = [rect.get_x(), rect.get_y()]

#def add_outlined_text(ax, x, y, text, fontsize=12):
#    """Function to add white text with a black outline."""
#    txt = ax.text(x, y, text, fontsize=fontsize, color='white', ha='center', va='center')
#    # Add the black outline using PathEffects
#    txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='black')])

#def create_map(output_dir, locationArray, adjacencyMatrix, rectangles_by_coords):
#    adjacencyMatrix = np.array(adjacencyMatrix, dtype=int)
#    G = nx.from_numpy_array(adjacencyMatrix)
#  
#    pos = nx.kamada_kawai_layout(G, scale=20.0)
#
#    n = 1.5*len(adjacencyMatrix)
#    fig, ax = plt.subplots(figsize=(n, n))

#    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', width=3.0)
    
#    for node in G.nodes():
#        node_image_file = Path(output_dir).as_posix() + f"/locationImages/location_{node + 1}_day.png"
#        add_image_at_node(ax, pos[node], node, node_image_file, 0.15, str(node), rectangles_by_coords)
#        locationName = locationArray[node].get('locationName')
#        add_outlined_text(ax, pos[node][0], pos[node][1], locationName, fontsize=12)

#    ax.set_xlim(min([x for x, y in pos.values()]) - 0.5, max([x for x, y in pos.values()]) + 0.5)
#    ax.set_ylim(min([y for x, y in pos.values()]) - 0.5, max([y for x, y in pos.values()]) + 0.5)

#    plt.axis('off')
#    plt.savefig(Path(output_dir).as_posix() + '/map_day.svg', format='svg')