import tkinter as tk
from tkinter import messagebox
from typing import List, Tuple

class Node:
    def __init__(self, state: Tuple[int, int], parent, actions, totalcost: int, heuristic: int):
        self.state = state
        self.parent = parent
        self.actions = actions
        self.totalcost = totalcost
        self.heuristic = heuristic

def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def A_star(start: Tuple[int, int], goal: Tuple[int, int], grid: List[List[str]]) -> List[Tuple[int, int]]:
    graph = {}
    rows, cols = len(grid), len(grid[0])

    for x in range(rows):
        for y in range(cols):
            if grid[x][y] == '#':
                continue
            actions = [((nx, ny), 1) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)] 
                      if 0 <= (nx := x + dx) < rows and 0 <= (ny := y + dy) < cols and grid[nx][ny] != '#']
            graph[(x, y)] = Node((x, y), None, actions, float('inf'), manhattan_distance((x, y), goal))

    if start not in graph or goal not in graph:
        return []

    graph[start].totalcost = 0
    frontier = [(start, 0)]
    explored = []

    while frontier:
        currentnode, currentcost = min(frontier, key=lambda f: f[1] + graph[f[0]].heuristic)
        frontier.remove((currentnode, currentcost))
        explored.append(currentnode)

        if currentnode == goal:
            path = [goal]
            while graph[path[-1]].parent:
                path.append(graph[path[-1]].parent)
            return path[::-1]

        for child, cost in graph[currentnode].actions:
            new_cost = currentcost + cost
            if child not in explored and new_cost < graph[child].totalcost:
                graph[child].parent = currentnode
                graph[child].totalcost = new_cost
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
        self.cell_size = 60
        
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
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, text="R")
                elif (x, y) == self.hospital:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, text="H")
                elif self.grid[x][y] == '#':
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, text="#")
                elif (x, y) in self.victims_info and (x, y) not in self.treated_victims:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, 
                                          text=self.victims_info[(x, y)]['label'], fill="white")

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
        path_log, event_log = [start], ["Starting at base"]
        current_position = start

        while victims_info:
            # Find victim with highest criticality, then closest
            target = min(victims_info.keys(), 
                        key=lambda pos: (-victims_info[pos]['criticality'], 
                                       manhattan_distance(current_position, pos)))
            label = victims_info[target]['label']
            
            path = A_star(current_position, target, grid)
            path_log.extend(path[1:])
            event_log.extend([f"Moving to {label}"] * (len(path)-1))
            
            current_position = target
            if victims_info[target]['treat_on_spot']:
                event_log[-1] = f"Treating {label} (criticality: {victims_info[target]['criticality']}) on spot"
            else:
                event_log[-1] = f"Picked up {label} (criticality: {victims_info[target]['criticality']})"
                path = A_star(current_position, hospital, grid)
                path_log.extend(path[1:])
                event_log.extend([f"Delivering {label} to hospital"] * (len(path)-1))
                current_position = hospital
                event_log[-1] = f"Delivered {label}"

            del victims_info[target]

        path = A_star(current_position, start, grid)
        path_log.extend(path[1:])
        event_log.extend(["Returning to base"] * (len(path)-1))
        
        return path_log, event_log

if __name__ == "__main__":
    grid = [
        ['R', '_', '_', '_', 'V1'],
        ['#', '#', '_', '#', '_'],
        ['_', '_', '_', '_', 'V2'],
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