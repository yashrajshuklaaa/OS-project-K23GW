import os
import tkinter as tk
from tkinter import messagebox, ttk
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import time
import threading

class RAGSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("RESOURCE ALLOCATION GRAPH")
        self.root.geometry("1000x700")
        
        # Set background
        self.set_background()
        self.create_widgets()

    def set_background(self):
        try:
            # Try to load background image
            image_path = os.path.expanduser("~/Downloads/A_futuristic_digital-style_background_featuring_a_.png")
            self.bg_image = Image.open(image_path)
            self.bg_image = self.bg_image.resize((1500, 1000), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            # Fallback to solid color if image not found
            self.root.configure(bg="#2c3e50")

    def create_widgets(self):
        # Semi-transparent frame for better readability
        frame = tk.Frame(self.root, bg="white", bd=2, relief="solid")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=400)

        # Title
        tk.Label(frame, text="RESOURCE ALLOCATION GRAPH", 
                font=("Arial", 28, "bold"), fg="black", bg="white").pack(pady=10)
        tk.Label(frame, text=' "A tool to visualize resource allocation and detect deadlocks" ', 
                font=("Arial", 15), fg="black", bg="white").pack()

        tk.Label(frame, text="Choose a Simulation Method: ", 
                font=("Arial", 14, "bold"), fg="black", bg="white").pack(pady=10)

        # Buttons with better styling
        btn_style = {"font": ("Arial", 12), "fg": "black", "padx": 15, "pady": 8, "bd": 0}
        
        btn_single = tk.Button(frame, text="Single Instance (Banker's Algorithm)", 
                             bg="#3498db", activebackground="#2980b9",
                             command=self.open_bankers_algorithm, **btn_style)
        btn_single.pack(pady=10, ipadx=10)

        btn_multi = tk.Button(frame, text="Multiple Instances (Circular Wait)", 
                            bg="#e74c3c", activebackground="#c0392b",
                            command=self.open_circular_wait, **btn_style)
        btn_multi.pack(pady=10, ipadx=10)

    def open_bankers_algorithm(self):
        self.root.destroy()
        root = tk.Tk()
        BankersAlgorithmGUI(root)
        root.mainloop()
        
    def open_circular_wait(self):
        self.root.destroy()
        root = tk.Tk()
        CircularWaitGUI(root)
        root.mainloop()

class BankersAlgorithmGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Banker's Algorithm")
        self.root.geometry("1200x800")
        self.root.configure(bg="#ecf0f1")
        
        # Create main container
        self.container = tk.Frame(self.root, bg="#ecf0f1")
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input frame
        self.input_frame = tk.Frame(self.container, bg="#ecf0f1", bd=2, relief="solid", padx=20, pady=20)
        self.input_frame.pack(fill=tk.X, pady=10)
        
        # Visualization frame
        self.viz_frame = tk.Frame(self.container, bg="white")
        self.viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.create_input_widgets()
        self.figure, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize empty graph
        self.G = nx.DiGraph()
        self.draw_empty_graph("Enter process and resource counts to begin")
        
    def create_input_widgets(self):
        tk.Label(self.input_frame, text="Banker's Algorithm", font=("Arial", 20, "bold"), 
                bg="#ecf0f1", fg="black").pack(side=tk.TOP, pady=5)
                
        # Process/Resource input
        input_row = tk.Frame(self.input_frame, bg="#ecf0f1")
        input_row.pack(pady=10)
        
        tk.Label(input_row, text="Processes:", bg="#ecf0f1", fg="black").pack(side=tk.LEFT, padx=5)
        self.processes_entry = tk.Entry(input_row, width=5)
        self.processes_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(input_row, text="Resources:", bg="#ecf0f1", fg="black").pack(side=tk.LEFT, padx=5)
        self.resources_entry = tk.Entry(input_row, width=5)
        self.resources_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(input_row, text="Set", command=self.set_process_resources, 
                bg="#2ecc71", fg="black").pack(side=tk.LEFT, padx=10)
                
        # Matrix frame (will be populated after setting counts)
        self.matrix_frame = tk.Frame(self.input_frame, bg="#ecf0f1")
        self.matrix_frame.pack(fill=tk.X, pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(self.input_frame, bg="#ecf0f1")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Run Algorithm", command=self.run_bankers_algorithm,
                bg="#3498db", fg="black").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reset", command=self.reset,
                bg="#e74c3c", fg="black").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Main Menu", command=self.exit_to_main,
                bg="#34495e", fg="black").pack(side=tk.LEFT, padx=5)
    
    def set_process_resources(self):
        try:
            self.num_processes = int(self.processes_entry.get())
            self.num_resources = int(self.resources_entry.get())
            
            if self.num_processes <= 0 or self.num_resources <= 0:
                raise ValueError("Counts must be positive")
                
            self.create_matrix_inputs()
            self.initialize_graph()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive integers")
    
    def create_matrix_inputs(self):
        # Clear previous inputs
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
            
        # Create a frame for both matrices side by side
        matrices_frame = tk.Frame(self.matrix_frame, bg="#ecf0f1")
        matrices_frame.pack(fill=tk.X, pady=5)
            
        # Allocation matrix frame (left side)
        alloc_frame = tk.Frame(matrices_frame, bg="#ecf0f1")
        alloc_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(alloc_frame, text="Allocation Matrix:", 
                bg="#ecf0f1", fg="black").pack(anchor=tk.W)
        self.allocation_entries = self.create_matrix(alloc_frame, self.num_processes, self.num_resources)
        
        # Max matrix frame (right side)
        max_frame = tk.Frame(matrices_frame, bg="#ecf0f1")
        max_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(max_frame, text="Max Need Matrix:", 
                bg="#ecf0f1", fg="black").pack(anchor=tk.W)
        self.max_entries = self.create_matrix(max_frame, self.num_processes, self.num_resources)
        
        # Available resources (below the matrices)
        avail_frame = tk.Frame(self.matrix_frame, bg="#ecf0f1")
        avail_frame.pack(fill=tk.X, pady=(10,0))
        tk.Label(avail_frame, text="Available Resources (space separated):", 
                bg="#ecf0f1", fg="black").pack(anchor=tk.W)
        self.available_entry = tk.Entry(avail_frame, width=30)
        self.available_entry.pack(anchor=tk.W)
    
    def create_matrix(self, parent, rows, cols):
        entries = []
        for i in range(rows):
            row_frame = tk.Frame(parent, bg="#ecf0f1")
            row_frame.pack(anchor=tk.W)
            tk.Label(row_frame, text=f"P{i}:", bg="#ecf0f1", fg="black").pack(side=tk.LEFT)
            row_entries = []
            for j in range(cols):
                entry = tk.Entry(row_frame, width=5)
                entry.pack(side=tk.LEFT, padx=2)
                row_entries.append(entry)
            entries.append(row_entries)
        return entries
    
    def initialize_graph(self):
        self.G = nx.DiGraph()
        
        # Add nodes (processes in blue, resources in red)
        for i in range(self.num_processes):
            self.G.add_node(f"P{i}", color="blue", shape="circle")
            
        for j in range(self.num_resources):
            self.G.add_node(f"R{j}", color="red", shape="square")
        
        self.update_graph_visualization("Initialized graph with processes and resources")
    
    def update_graph_visualization(self, title=""):
        self.ax.clear()
        
        if len(self.G.nodes()) == 0:
            self.ax.text(0.5, 0.5, "No graph data to display", 
                        ha="center", va="center", fontsize=12)
            self.ax.set_axis_off()
        else:
            pos = nx.spring_layout(self.G)
            
            # Draw nodes with different shapes
            process_nodes = [n for n in self.G.nodes if n.startswith('P')]
            resource_nodes = [n for n in self.G.nodes if n.startswith('R')]
            
            nx.draw_networkx_nodes(self.G, pos, nodelist=process_nodes, 
                                 node_color='lightblue', node_shape='o', node_size=800)
            nx.draw_networkx_nodes(self.G, pos, nodelist=resource_nodes, 
                                 node_color='lightcoral', node_shape='s', node_size=800)
            
            # Draw edges with different styles
            edge_colors = []
            edge_styles = []
            
            for u, v, data in self.G.edges(data=True):
                if u.startswith('P') and v.startswith('R'):
                    edge_colors.append('red')  # Request edges
                    edge_styles.append('dashed')
                else:
                    edge_colors.append('black')  # Allocation edges
                    edge_styles.append('solid')
            
            nx.draw_networkx_edges(self.G, pos, edge_color=edge_colors, style=edge_styles,
                                 width=2, arrowstyle='-|>', arrowsize=20)
            
            # Draw labels
            nx.draw_networkx_labels(self.G, pos, font_size=10, font_weight='bold')
            
            # Add edge labels for weights
            edge_labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels)
            
            self.ax.set_title(title, fontsize=12)
            self.ax.set_axis_off()
        
        self.canvas.draw()
    
    def draw_empty_graph(self, message):
        self.ax.clear()
        self.ax.text(0.5, 0.5, message, 
                    ha="center", va="center", fontsize=12)
        self.ax.set_axis_off()
        self.canvas.draw()
    
    def run_bankers_algorithm(self):
        try:
            # Get input values
            self.allocation = [[int(entry.get()) for entry in row] for row in self.allocation_entries]
            self.max_need = [[int(entry.get()) for entry in row] for row in self.max_entries]
            self.available = [int(x) for x in self.available_entry.get().split()]
            
            if len(self.available) != self.num_resources:
                raise ValueError("Available resources count doesn't match")
                
            # Update graph with allocation and request edges
            self.update_graph_with_matrices()
            
            # Run Banker's algorithm
            safe_sequence = self.bankers_algorithm()
            
            if safe_sequence:
                messagebox.showinfo("Safe Sequence", f"System is in a safe state.\nSafe sequence: {safe_sequence}")
                self.highlight_safe_sequence(safe_sequence)
            else:
                messagebox.showerror("Deadlock", "System is in an unsafe state. Deadlock detected!")
                self.highlight_deadlock()
                
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
    
    def update_graph_with_matrices(self):
        # Clear existing edges
        self.G.remove_edges_from(list(self.G.edges()))
        
        # Add edges based on allocation and request matrices
        for i in range(self.num_processes):
            for j in range(self.num_resources):
                if self.allocation[i][j] > 0:
                    self.G.add_edge(f"R{j}", f"P{i}", weight=self.allocation[i][j], 
                                  label=f"Alloc: {self.allocation[i][j]}")
                
                if self.max_need[i][j] - self.allocation[i][j] > 0:
                    self.G.add_edge(f"P{i}", f"R{j}", weight=self.max_need[i][j] - self.allocation[i][j], 
                                  label=f"Req: {self.max_need[i][j] - self.allocation[i][j]}")
        
        self.update_graph_visualization("Updated with allocation and request edges")
    
    def bankers_algorithm(self):
        work = self.available[:]
        finish = [False] * self.num_processes
        safe_sequence = []
        
        need = [[self.max_need[i][j] - self.allocation[i][j] 
                for j in range(self.num_resources)] 
                for i in range(self.num_processes)]
        
        while len(safe_sequence) < self.num_processes:
            found = False
            for i in range(self.num_processes):
                if not finish[i] and all(need[i][j] <= work[j] for j in range(self.num_resources)):
                    # Add to safe sequence
                    safe_sequence.append(f"P{i}")
                    
                    # Update animation to show this process can proceed
                    self.highlight_process(i, "green")
                    self.root.update()
                    time.sleep(1)
                    
                    # Release resources
                    for j in range(self.num_resources):
                        work[j] += self.allocation[i][j]
                    
                    finish[i] = True
                    found = True
                    
                    # Update visualization
                    self.highlight_process(i, "lightblue")  # Reset color
                    self.update_graph_visualization(f"Process P{i} completed - Work: {work}")
                    time.sleep(1)
                    break
            
            if not found:
                return None  # Unsafe state
        
        return " → ".join(safe_sequence)
    
    def highlight_process(self, process_idx, color):
        node = f"P{process_idx}"
        if node in self.G.nodes():
            self.G.nodes[node]['color'] = color
            self.update_graph_visualization(f"Highlighting process P{process_idx}")
    
    def highlight_safe_sequence(self, sequence):
        process_order = [s.strip() for s in sequence.split("→")]
        
        def animate_sequence():
            for i, process in enumerate(process_order):
                self.highlight_process(int(process[1:]), "green")
                self.root.update()
                time.sleep(1)
                if i < len(process_order) - 1:
                    self.highlight_process(int(process[1:]), "lightgray")  # Completed processes
                self.root.update()
        
        threading.Thread(target=animate_sequence).start()
    
    def highlight_deadlock(self):
        # Try to find a cycle in the graph
        try:
            cycle = nx.find_cycle(self.G)
            for u, v in cycle:
                self.G.edges[u, v]['color'] = 'red'
            self.update_graph_visualization("Deadlock Detected - Cycle Highlighted")
        except nx.NetworkXNoCycle:
            self.update_graph_visualization("No cycle found (but unsafe state)")
    
    def reset(self):
        self.processes_entry.delete(0, tk.END)
        self.resources_entry.delete(0, tk.END)
        self.matrix_frame.destroy()
        self.matrix_frame = tk.Frame(self.input_frame, bg="#ecf0f1")
        self.matrix_frame.pack(fill=tk.X, pady=10)
        self.draw_empty_graph("Enter process and resource counts to begin")
    
    def exit_to_main(self):
        self.root.destroy()
        root = tk.Tk()
        RAGSimulator(root)
        root.mainloop()

class CircularWaitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Circular Wait - Multiple Instances")
        self.root.geometry("1200x800")
        self.root.configure(bg="#ecf0f1")
        
        # Create main container
        self.container = tk.Frame(self.root, bg="#ecf0f1")
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input frame
        self.input_frame = tk.Frame(self.container, bg="#ecf0f1", bd=2, relief="solid", padx=20, pady=20)
        self.input_frame.pack(fill=tk.X, pady=10)
        
        # Visualization frame
        self.viz_frame = tk.Frame(self.container, bg="white")
        self.viz_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.create_input_widgets()
        self.figure, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize empty graph
        self.G = nx.DiGraph()
        self.draw_empty_graph("Enter process and resource counts to begin")
    
    def create_input_widgets(self):
        tk.Label(self.input_frame, text="Circular Wait Detection", font=("Arial", 20, "bold"), 
                bg="#ecf0f1", fg="black").pack(side=tk.TOP, pady=5)
                
        # Process/Resource input
        input_row = tk.Frame(self.input_frame, bg="#ecf0f1")
        input_row.pack(pady=10)
        
        tk.Label(input_row, text="Processes:", bg="#ecf0f1", fg="black").pack(side=tk.LEFT, padx=5)
        self.processes_entry = tk.Entry(input_row, width=5)
        self.processes_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(input_row, text="Resources:", bg="#ecf0f1", fg="black").pack(side=tk.LEFT, padx=5)
        self.resources_entry = tk.Entry(input_row, width=5)
        self.resources_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(input_row, text="Set", command=self.set_process_resources, 
                bg="#2ecc71", fg="black").pack(side=tk.LEFT, padx=10)
                
        # Matrix frame (will be populated after setting counts)
        self.matrix_frame = tk.Frame(self.input_frame, bg="#ecf0f1")
        self.matrix_frame.pack(fill=tk.X, pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(self.input_frame, bg="#ecf0f1")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Check Deadlock", command=self.check_deadlock,
                bg="#e74c3c", fg="black").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reset", command=self.reset,
                bg="#e74c3c", fg="black").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Main Menu", command=self.exit_to_main,
                bg="#34495e", fg="black").pack(side=tk.LEFT, padx=5)
    
    def set_process_resources(self):
        try:
            self.num_processes = int(self.processes_entry.get())
            self.num_resources = int(self.resources_entry.get())
            
            if self.num_processes <= 0 or self.num_resources <= 0:
                raise ValueError("Counts must be positive")
                
            self.create_matrix_inputs()
            self.initialize_graph()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive integers")
    
    def create_matrix_inputs(self):
        # Clear previous inputs
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
            
        # Create a frame for both matrices side by side
        matrices_frame = tk.Frame(self.matrix_frame, bg="#ecf0f1")
        matrices_frame.pack(fill=tk.X, pady=5)
            
        # Allocation matrix frame (left side)
        alloc_frame = tk.Frame(matrices_frame, bg="#ecf0f1")
        alloc_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(alloc_frame, text="Allocation Matrix (1 if process holds resource):", 
                bg="#ecf0f1", fg="black").pack(anchor=tk.W)
        self.allocation_entries = self.create_matrix(alloc_frame, self.num_processes, self.num_resources)
        
        # Request matrix frame (right side)
        request_frame = tk.Frame(matrices_frame, bg="#ecf0f1")
        request_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(request_frame, text="Request Matrix (1 if process requests resource):", 
                bg="#ecf0f1", fg="black").pack(anchor=tk.W)
        self.request_entries = self.create_matrix(request_frame, self.num_processes, self.num_resources)
        
        # Available resources frame (below matrices)
        avail_frame = tk.Frame(self.matrix_frame, bg="#ecf0f1")
        avail_frame.pack(fill=tk.X, pady=(10,0))
        tk.Label(avail_frame, text="Available Resources (space separated):", 
                bg="#ecf0f1", fg="black").pack(anchor=tk.W)
        self.available_entry = tk.Entry(avail_frame, width=30)
        self.available_entry.pack(anchor=tk.W)
    
    def create_matrix(self, parent, rows, cols):
        entries = []
        for i in range(rows):
            row_frame = tk.Frame(parent, bg="#ecf0f1")
            row_frame.pack(anchor=tk.W)
            tk.Label(row_frame, text=f"P{i}:", bg="#ecf0f1", fg="black").pack(side=tk.LEFT)
            row_entries = []
            for j in range(cols):
                entry = tk.Entry(row_frame, width=5)
                entry.insert(0, "0")  # Default to 0
                entry.pack(side=tk.LEFT, padx=2)
                row_entries.append(entry)
            entries.append(row_entries)
        return entries
    
    def initialize_graph(self):
        self.G = nx.DiGraph()
        
        # Add nodes (processes in blue, resources in red)
        for i in range(self.num_processes):
            self.G.add_node(f"P{i}", color="blue", shape="circle")
            
        for j in range(self.num_resources):
            self.G.add_node(f"R{j}", color="red", shape="square")
        
        self.update_graph_visualization("Initialized graph with processes and resources")
    
    def update_graph_visualization(self, title=""):
        self.ax.clear()
        
        if len(self.G.nodes()) == 0:
            self.ax.text(0.5, 0.5, "No graph data to display", 
                        ha="center", va="center", fontsize=12)
            self.ax.set_axis_off()
        else:
            pos = nx.spring_layout(self.G)
            
            # Draw nodes with different shapes
            process_nodes = [n for n in self.G.nodes if n.startswith('P')]
            resource_nodes = [n for n in self.G.nodes if n.startswith('R')]
            
            nx.draw_networkx_nodes(self.G, pos, nodelist=process_nodes, 
                                 node_color='lightblue', node_shape='o', node_size=800)
            nx.draw_networkx_nodes(self.G, pos, nodelist=resource_nodes, 
                                 node_color='lightcoral', node_shape='s', node_size=800)
            
            # Draw edges with different styles and labels
            edge_colors = []
            edge_styles = []
            edge_labels = {}
            
            for u, v, data in self.G.edges(data=True):
                if u.startswith('P') and v.startswith('R'):
                    edge_colors.append('red')  # Request edges
                    edge_styles.append('dashed')
                    edge_labels[(u, v)] = "Requested"
                else:
                    edge_colors.append('black')  # Allocation edges
                    edge_styles.append('solid')
                    edge_labels[(u, v)] = "Allocated"
            
            nx.draw_networkx_edges(self.G, pos, edge_color=edge_colors, style=edge_styles,
                                 width=2, arrowstyle='-|>', arrowsize=20)
            
            # Draw edge labels
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=10)
            
            # Draw node labels
            nx.draw_networkx_labels(self.G, pos, font_size=10, font_weight='bold')
            
            self.ax.set_title(title, fontsize=12)
            self.ax.set_axis_off()
        
        self.canvas.draw()
    
    def draw_empty_graph(self, message):
        self.ax.clear()
        self.ax.text(0.5, 0.5, message, 
                    ha="center", va="center", fontsize=12)
        self.ax.set_axis_off()
        self.canvas.draw()
    
    def check_deadlock(self):
        try:
            # Get input values (1 if relationship exists, 0 otherwise)
            self.allocation = [[int(entry.get()) for entry in row] for row in self.allocation_entries]
            self.request = [[int(entry.get()) for entry in row] for row in self.request_entries]
            
            # Update graph with edges
            self.update_graph_with_matrices()
            
            # Check for deadlock
            has_deadlock, cycle = self.detect_deadlock()
            
            if has_deadlock:
                messagebox.showerror("Deadlock Detected", f"Cycle found: {cycle}")
                self.highlight_cycle(cycle)
            else:
                messagebox.showinfo("No Deadlock", "No circular wait detected")
                self.update_graph_visualization("No deadlock detected")
                
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid values (0 or 1)")
    
    def update_graph_with_matrices(self):
        # Clear existing edges
        self.G.remove_edges_from(list(self.G.edges()))
        
        # Add edges based on allocation and request matrices
        for i in range(self.num_processes):
            for j in range(self.num_resources):
                if self.allocation[i][j] == 1:
                    self.G.add_edge(f"R{j}", f"P{i}", type="allocation")
                
                if self.request[i][j] == 1:
                    self.G.add_edge(f"P{i}", f"R{j}", type="request")
        
        self.update_graph_visualization("Updated with allocation and request edges")
    
    def detect_deadlock(self):
        try:
            cycle = nx.find_cycle(self.G)
            return True, [(u, v) for u, v in cycle]
        except nx.NetworkXNoCycle:
            return False, None
    
    def highlight_cycle(self, cycle):
        # Highlight nodes and edges in the cycle
        for u, v in cycle:
            if (u, v) in self.G.edges():
                self.G.edges[u, v]['color'] = 'red'
                self.G.edges[u, v]['width'] = 3
        
        # Also highlight the nodes
        nodes_in_cycle = set()
        for u, v in cycle:
            nodes_in_cycle.add(u)
            nodes_in_cycle.add(v)
        
        for node in nodes_in_cycle:
            if node in self.G.nodes():
                self.G.nodes[node]['color'] = 'yellow'
        
        self.update_graph_visualization("Deadlock Detected - Cycle Highlighted")
    
    def reset(self):
        self.processes_entry.delete(0, tk.END)
        self.resources_entry.delete(0, tk.END)
        self.matrix_frame.destroy()
        self.matrix_frame = tk.Frame(self.input_frame, bg="#ecf0f1")
        self.matrix_frame.pack(fill=tk.X, pady=10)
        self.draw_empty_graph("Enter process and resource counts to begin")
    
    def exit_to_main(self):
        self.root.destroy()
        root = tk.Tk()
        RAGSimulator(root)
        root.mainloop()
if __name__ == "__main__":
    root = tk.Tk()
    app = RAGSimulator(root)
    root.mainloop()