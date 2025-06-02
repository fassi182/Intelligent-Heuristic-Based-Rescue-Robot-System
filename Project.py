import tkinter as tk
from tkinter import messagebox
from typing import  Tuple

class Node:
    def __init__(self, state: Tuple[int, int], parent, actions, totalcost: int, heuristic: int):
        self.state = state
        self.parent = parent
        self.actions = actions
        self.totalcost = totalcost
        self.heuristic = heuristic

def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def A_star(start, goal, grid):
    rows = len(grid)
    cols = len(grid[0])
    graph = {}

    # Build graph with valid nodes
    for x in range(rows):
        for y in range(cols):
            if grid[x][y] == '#':
                continue

            actions = []
            for direction in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                dx = direction[0]
                dy = direction[1]
                nx = x + dx
                ny = y + dy

                if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != '#':
                    actions.append(((nx, ny), 1))

            node = Node(
                state=(x, y),
                parent=None,
                actions=actions,
                totalcost=float('inf'),
                heuristic=manhattan_distance((x, y), goal)
            )
            graph[(x, y)] = node

    if start not in graph or goal not in graph:
        return []

    graph[start].totalcost = 0
    frontier = [(start, 0)]
    explored = []

    while frontier:
        # Find node with lowest cost + heuristic
        best_index = 0
        best_node = frontier[0]
        for i in range(1, len(frontier)):
            pos, cost = frontier[i]
            score = cost + graph[pos].heuristic
            best_score = best_node[1] + graph[best_node[0]].heuristic
            if score < best_score:
                best_node = frontier[i]
                best_index = i

        current_node, current_cost = frontier.pop(best_index)
        explored.append(current_node)

        if current_node == goal:
            path = [goal]
            while graph[path[-1]].parent is not None:
                path.append(graph[path[-1]].parent)
            return path[::-1]

        for child, cost in graph[current_node].actions:
            new_cost = current_cost + cost
            if child not in explored and new_cost < graph[child].totalcost:
                graph[child].totalcost = new_cost
                graph[child].parent = current_node
                frontier.append((child, new_cost))

    return []

class SearchAndRescueGUI:
    def __init__(self, master, grid, start, hospital, victims_info):
        self.master = master
        self.master.title("Search and Rescue Simulation")
        self.grid = grid
        self.start = self.current_position = start
        self.hospital = hospital
        self.victims_info = victims_info.copy()
        self.treated_victims = set()
        self.cell_size = 100
        # Color mapping for different criticality levels
        self.criticality_colors = {
            1: "#FFCC00",  # Light yellow for low criticality
            2: "#FF9900",  # Orange
            3: "#FF6600",  # Dark orange
            4: "#FF3300",  # Red-orange
            5: "#FF0000"   # Bright red for highest criticality
        }
        
        self.canvas = tk.Canvas(master, width=len(grid[0])*self.cell_size, height=len(grid)*self.cell_size)
        self.canvas.pack()
        
        self.controls = tk.Frame(master)
        self.controls.pack()
        
        tk.Button(self.controls, text="Start Simulation", command=self.start_simulation).pack(side=tk.LEFT)
        tk.Button(self.controls, text="Next Step", command=self.next_step).pack(side=tk.LEFT)
        tk.Button(self.controls, text="Reset", command=self.reset_simulation).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(master, text="Ready to start simulation")
        self.status_label.pack()
        
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for x in range(len(self.grid)):
            for y in range(len(self.grid[0])):
                x1, y1 = y * self.cell_size, x * self.cell_size
                color = "white"
                
                if (x, y) == self.start:
                    color = "lightblue"
                elif (x, y) == self.hospital:
                    color = "pink"
                elif self.grid[x][y] == '#':
                    color = "gray"
                elif (x, y) in self.victims_info and (x, y) not in self.treated_victims:
                    crit = self.victims_info[(x, y)]['criticality']
                    color = self.criticality_colors.get(min(max(crit, 1), 5), "#FF0000")  # Default to red if out of range
                
                self.canvas.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size, 
                                           fill=color, outline="black")
                
                # Add text labels
                if (x, y) == self.start:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, text="R",font=("Arial", 16))
                elif (x, y) == self.hospital:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, text="H",font=("Arial", 16))
                elif self.grid[x][y] == '#':
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, text="#",font=("Arial", 16))
                elif (x, y) in self.victims_info and (x, y) not in self.treated_victims:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, 
                                          text=self.victims_info[(x, y)]['label'], fill="white",font=("Arial", 16))

        # Draw robot position
        if self.current_position:
            x, y = self.current_position[1]*self.cell_size + self.cell_size/2, self.current_position[0]*self.cell_size + self.cell_size/2
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="blue")

    def start_simulation(self):
        self.current_position = self.start
        self.treated_victims = set()
        self.victims_info = victims_info.copy()
        self.full_path, self.movement_events = self.search_and_rescue(self.grid.copy(), self.start, self.hospital, self.victims_info.copy())
        self.step_index = 0
        self.status_label.config(text="Simulation started - press Next Step")
        self.draw_grid()

    def next_step(self):
        if not hasattr(self, 'full_path') or self.step_index >= len(self.full_path):
            self.status_label.config(text="Simulation complete!")
            messagebox.showinfo("Done", "All victims rescued and robot returned!")
            return

        self.current_position = self.full_path[self.step_index]
        action_message = self.movement_events[self.step_index]
        
        if "Treating" in action_message or "Picked up" in action_message:
            for pos, info in self.victims_info.items():
                if info['label'] in action_message:
                    self.treated_victims.add(pos)
                    break

        self.status_label.config(text=action_message)
        self.step_index += 1
        self.draw_grid()

    def reset_simulation(self):
        self.current_position = self.start
        self.treated_victims = set()
        self.step_index = 0
        if hasattr(self, 'full_path'):
            del self.full_path
        self.status_label.config(text="Simulation reset")
        self.draw_grid()

    def search_and_rescue(self, grid, start, hospital, victims_info):
        path_log = [start]
        event_log = ["Starting at base"]
        current_position = start

        while len(victims_info) > 0:
            # Step 1: Choose highest criticality victim, break ties by distance
            best_victim = None
            best_criticality = -1
            best_distance = float('inf')

            for pos in victims_info:
                crit = victims_info[pos]['criticality']
                dist = manhattan_distance(current_position, pos)

                if crit > best_criticality:
                    best_victim = pos
                    best_criticality = crit
                    best_distance = dist
                elif crit == best_criticality and dist < best_distance:
                    best_victim = pos
                    best_distance = dist

            label = victims_info[best_victim]['label']

            # Step 2: Move to victim
            path_to_victim = A_star(current_position, best_victim, grid)
            for i in range(1, len(path_to_victim)):
                path_log.append(path_to_victim[i])
                event_log.append("Moving to " + label)

            current_position = best_victim

            # Step 3: Treat or Pick Up
            if victims_info[best_victim]['treat_on_spot']:
                event_log[-1] = "Treating " + label + " (criticality: " + str(best_criticality) + ") on spot"
            else:
                event_log[-1] = "Picked up " + label + " (criticality: " + str(best_criticality) + ")"

            # Step 4: Transport to hospital
                path_to_hospital = A_star(current_position, hospital, grid)
                for i in range(1, len(path_to_hospital)):
                    path_log.append(path_to_hospital[i])
                    event_log.append("Delivering " + label + " to hospital")

                current_position = hospital
                event_log[-1] = "Delivered " + label

        # Step 5: Remove treated victim
            del victims_info[best_victim]

    # Step 6: Return to base
        path_home = A_star(current_position, start, grid)
        for i in range(1, len(path_home)):
            path_log.append(path_home[i])
            event_log.append("Returning to base")

        return path_log, event_log

if __name__ == "__main__":
    grid = [
        ['R', '_', '_', '_', 'V1'],
        ['#', '#', '_', '#', '_'],
        ['_', 'v5', '_', 'V4', 'V2'],
        ['_', '#', '_', '#', '_'],
        ['_', 'V3', '_', '_', 'H']
    ]
    start = (0, 0)
    hospital = (4, 4)
    victims_info = {
        (0, 4): {'criticality': 2, 'treat_on_spot': True,  'label': 'V1'},
        (2, 4): {'criticality': 5, 'treat_on_spot': False, 'label': 'V2'},
        (4, 1): {'criticality': 3, 'treat_on_spot': False, 'label': 'V3'},
        (2, 1): {'criticality': 9, 'treat_on_spot': False, 'label': 'V5'},

        (2, 3): {'criticality': 6, 'treat_on_spot': True, 'label': 'V4'},
        

    }

    root = tk.Tk()
    SearchAndRescueGUI(root, grid, start, hospital, victims_info)
    root.mainloop()


