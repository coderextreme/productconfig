import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np
import matplotlib.patches as mpatches
import random
import threading

class EntityRelationshipGraphGUI:
    def __init__(self, root, db_path):
        self.root = root
        self.db_path = db_path
        self.root.title("Entity Relationship Graph Viewer")
        self.root.geometry("1200x800")
        
        # Initialize variables
        self.entities = {}
        self.relationships = []
        self.G = nx.DiGraph()
        self.is_data_loaded = False
        self.is_loading = False
        
        # Create main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Split view - left for controls, right for graph
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for controls
        self.control_frame = ttk.LabelFrame(self.paned_window, text="Controls")
        
        # Right frame for graph
        self.graph_frame = ttk.LabelFrame(self.paned_window, text="Entity Relationship Graph")
        
        self.paned_window.add(self.control_frame, weight=1)
        self.paned_window.add(self.graph_frame, weight=3)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready - Click 'Load Data' to begin", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Setup controls
        self.setup_controls()
        
        # Setup graph with placeholder
        self.setup_graph()
        
        # Show initial placeholder in graph area
        self.show_placeholder()
        
    def setup_controls(self):
        control_inner = ttk.Frame(self.control_frame)
        control_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load data button at the top
        load_frame = ttk.Frame(control_inner)
        load_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.load_btn = ttk.Button(load_frame, text="Load Data", command=self.load_data_threaded)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(load_frame, mode='indeterminate', length=100)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Entity list
        ttk.Label(control_inner, text="Entities:").pack(anchor=tk.W, pady=(0, 5))
        
        # Treeview for entities with scrollbar
        entity_frame = ttk.Frame(control_inner)
        entity_frame.pack(fill=tk.BOTH, expand=True)
        
        self.entity_tree = ttk.Treeview(entity_frame, columns=("id", "value"), show="headings", height=10)
        self.entity_tree.heading("id", text="ID")
        self.entity_tree.heading("value", text="Value")
        self.entity_tree.column("id", width=50)
        self.entity_tree.column("value", width=150)
        
        scrollbar = ttk.Scrollbar(entity_frame, orient=tk.VERTICAL, command=self.entity_tree.yview)
        self.entity_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Entity selection event
        self.entity_tree.bind("<<TreeviewSelect>>", self.on_entity_select)
        
        # Relationship list
        ttk.Label(control_inner, text="Relationships:").pack(anchor=tk.W, pady=(15, 5))
        
        # Treeview for relationships with scrollbar
        rel_frame = ttk.Frame(control_inner)
        rel_frame.pack(fill=tk.BOTH, expand=True)
        
        self.rel_tree = ttk.Treeview(rel_frame, 
                                     columns=("id", "property", "related"), 
                                     show="headings", 
                                     height=10)
        self.rel_tree.heading("id", text="ID")
        self.rel_tree.heading("property", text="Property")
        self.rel_tree.heading("related", text="Related")
        self.rel_tree.column("id", width=50)
        self.rel_tree.column("property", width=100)
        self.rel_tree.column("related", width=100)
        
        rel_scrollbar = ttk.Scrollbar(rel_frame, orient=tk.VERTICAL, command=self.rel_tree.yview)
        self.rel_tree.configure(yscroll=rel_scrollbar.set)
        rel_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rel_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Relationship selection event
        self.rel_tree.bind("<<TreeviewSelect>>", self.on_relationship_select)
        
        # Visualization options
        options_frame = ttk.LabelFrame(control_inner, text="Graph Options")
        options_frame.pack(fill=tk.X, pady=10)
        
        # Layout algorithm options
        ttk.Label(options_frame, text="Layout Algorithm:").pack(anchor=tk.W, padx=5, pady=5)
        self.layout_var = tk.StringVar(value="spring")
        layout_combo = ttk.Combobox(options_frame, textvariable=self.layout_var)
        layout_combo['values'] = ("spring", "circular", "random", "kamada_kawai", "spectral")
        layout_combo.pack(fill=tk.X, padx=5, pady=5)
        layout_combo.bind("<<ComboboxSelected>>", lambda e: self.visualize_graph())
        
        # Node size
        ttk.Label(options_frame, text="Node Size:").pack(anchor=tk.W, padx=5, pady=5)
        self.node_size_var = tk.IntVar(value=300)
        node_size_slider = ttk.Scale(options_frame, from_=100, to=1000, variable=self.node_size_var, orient=tk.HORIZONTAL)
        node_size_slider.pack(fill=tk.X, padx=5, pady=5)
        node_size_slider.bind("<ButtonRelease-1>", lambda e: self.visualize_graph())
        
        # Edge width
        ttk.Label(options_frame, text="Edge Width:").pack(anchor=tk.W, padx=5, pady=5)
        self.edge_width_var = tk.DoubleVar(value=1.5)
        edge_width_slider = ttk.Scale(options_frame, from_=0.5, to=5.0, variable=self.edge_width_var, orient=tk.HORIZONTAL)
        edge_width_slider.pack(fill=tk.X, padx=5, pady=5)
        edge_width_slider.bind("<ButtonRelease-1>", lambda e: self.visualize_graph())
        
        # Label size
        ttk.Label(options_frame, text="Label Size:").pack(anchor=tk.W, padx=5, pady=5)
        self.label_size_var = tk.IntVar(value=10)
        label_size_slider = ttk.Scale(options_frame, from_=6, to=20, variable=self.label_size_var, orient=tk.HORIZONTAL)
        label_size_slider.pack(fill=tk.X, padx=5, pady=5)
        label_size_slider.bind("<ButtonRelease-1>", lambda e: self.visualize_graph())
        
        # Batch size for loading
        ttk.Label(options_frame, text="Batch Size:").pack(anchor=tk.W, padx=5, pady=5)
        self.batch_size_var = tk.IntVar(value=100)
        batch_size_slider = ttk.Scale(options_frame, from_=10, to=500, variable=self.batch_size_var, orient=tk.HORIZONTAL)
        batch_size_slider.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(control_inner)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Redraw Graph", command=self.visualize_graph).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Center on Selection", command=self.center_on_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Graph Image", command=self.save_graph_image).pack(side=tk.LEFT, padx=5)
    
    def setup_graph(self):
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Variables for selection
        self.selected_node = None
        self.selected_edge = None
        
        # Connect pick event
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)
    
    def show_placeholder(self):
        # Clear the axes
        self.ax.clear()
        
        # Show a placeholder message
        self.ax.text(0.5, 0.5, "No data loaded\nClick 'Load Data' to begin", 
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform=self.ax.transAxes,
                     fontsize=14)
        
        self.ax.set_axis_off()
        self.canvas.draw()
    
    def load_data_threaded(self):
        if self.is_loading:
            return
        
        # Start loading in a separate thread
        self.is_loading = True
        self.load_btn.config(state=tk.DISABLED)
        self.progress.start()
        self.status_bar.config(text="Loading data...")
        
        # Create and start the thread
        threading.Thread(target=self.load_data, daemon=True).start()
    
    def load_data(self):
        try:
            # Establish database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data
            for item in self.entity_tree.get_children():
                self.entity_tree.delete(item)
            
            for item in self.rel_tree.get_children():
                self.rel_tree.delete(item)
            
            # Get entity counts for progress tracking
            cursor.execute("SELECT COUNT(*) FROM Entity")
            entity_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Relationship")
            relationship_count = cursor.fetchone()[0]
            
            batch_size = self.batch_size_var.get()
            
            # Load entities in batches
            offset = 0
            self.entities = {}
            
            while offset < entity_count:
                # Get entity data from database
                cursor.execute("""
                    SELECT ID, 
                           COALESCE(TEXT_VALUE, 
                                  COALESCE(CAST(INTEGER_VALUE AS TEXT), 
                                         COALESCE(BOOLEAN_VALUE, 
                                                COALESCE(CAST(REAL_VALUE AS TEXT), 
                                                       COALESCE(CAST(NUMERIC_VALUE AS TEXT), 
                                                              'Entity ' || ID))))) AS DISPLAY_VALUE
                    FROM Entity
                    ORDER BY ID
                    LIMIT ? OFFSET ?
                """, (batch_size, offset))
                
                batch_entities = cursor.fetchall()
                
                # Update our entity dictionary
                for row in batch_entities:
                    entity_id, display_value = row
                    self.entities[entity_id] = display_value
                    
                    # Update UI in the main thread
                    self.root.after(0, lambda id=entity_id, val=display_value: 
                                     self.entity_tree.insert("", tk.END, values=(id, val)))
                
                # Update status
                self.root.after(0, lambda: self.status_bar.config(
                    text=f"Loading entities... {min(offset + batch_size, entity_count)}/{entity_count}"))
                
                offset += batch_size
            
            # Now load relationships in batches
            offset = 0
            self.relationships = []
            
            while offset < relationship_count:
                # Get relationship data from database
                cursor.execute("""
                    SELECT r.ID, r.PROPERTY_ID, r.RELATED_ID
                    FROM Relationship r
                    ORDER BY r.ID
                    LIMIT ? OFFSET ?
                """, (batch_size, offset))
                
                batch_relationships = cursor.fetchall()
                
                # Process each relationship
                for row in batch_relationships:
                    rel_id, property_id, related_id = row
                    rel = {
                        'id': rel_id,
                        'property_id': property_id,
                        'related_id': related_id
                    }
                    self.relationships.append(rel)
                    
                    # Get display values for the related entities
                    property_value = self.entities.get(property_id, f"Entity {property_id}")
                    related_value = self.entities.get(related_id, "None") if related_id else "None"
                    
                    # Update UI in the main thread
                    self.root.after(0, lambda id=rel_id, prop=property_value, rel=related_value: 
                                    self.rel_tree.insert("", tk.END, values=(id, prop, rel)))
                
                # Update status
                self.root.after(0, lambda: self.status_bar.config(
                    text=f"Loading relationships... {min(offset + batch_size, relationship_count)}/{relationship_count}"))
                
                offset += batch_size
            
            # Close the database connection
            conn.close()
            
            # Update status and UI in main thread
            self.root.after(0, self.finish_loading)
            
        except sqlite3.Error as e:
            # Handle errors in main thread
            self.root.after(0, lambda: self.show_error(f"Database Error: {str(e)}"))
    
    def finish_loading(self):
        # Stop the progress bar
        self.progress.stop()
        
        # Update UI
        self.is_loading = False
        self.is_data_loaded = True
        self.load_btn.config(state=tk.NORMAL, text="Reload Data")
        
        # Update status
        self.status_bar.config(text=f"Loaded {len(self.entities)} entities and {len(self.relationships)} relationships")
        
        # Build graph (this could be lazy-loaded too if needed)
        self.build_graph()
        
        # Visualize the graph
        self.visualize_graph()
    
    def show_error(self, message):
        # Display error in UI
        messagebox.showerror("Error", message)
        self.status_bar.config(text=f"Error: {message}")
        
        # Reset loading state
        self.progress.stop()
        self.is_loading = False
        self.load_btn.config(state=tk.NORMAL)
    
    def build_graph(self):
        if not self.is_data_loaded:
            return
        
        # Clear existing graph
        self.G.clear()
        
        # Update status
        self.status_bar.config(text="Building graph structure...")
        
        # Process in batches to avoid UI freezing
        self.add_nodes_to_graph()
        self.add_edges_to_graph()
    
    def add_nodes_to_graph(self):
        # Add nodes for all entities
        for entity_id, display_value in self.entities.items():
            # Truncate display value if too long
            if display_value and len(display_value) > 20:
                display_value = display_value[:17] + "..."
            
            self.G.add_node(entity_id, label=display_value or f"Entity {entity_id}")
    
    def add_edges_to_graph(self):
        # Add edges for relationships
        for rel in self.relationships:
            if rel['related_id'] is not None:  # Only add if there's a related entity
                self.G.add_edge(rel['property_id'], rel['related_id'], id=rel['id'])
    
    def visualize_graph(self):
        if not self.is_data_loaded:
            self.show_placeholder()
            return
        
        # Clear the axes
        self.ax.clear()
        
        if not self.G.nodes:
            self.ax.text(0.5, 0.5, "No data to display", 
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Update status
        self.status_bar.config(text="Generating graph layout...")
        
        # Get the layout algorithm
        layout_algo = self.layout_var.get()
        
        # Calculate positions based on selected layout
        if layout_algo == "spring":
            pos = nx.spring_layout(self.G, seed=42)
        elif layout_algo == "circular":
            pos = nx.circular_layout(self.G)
        elif layout_algo == "random":
            pos = nx.random_layout(self.G)
        elif layout_algo == "kamada_kawai":
            try:
                pos = nx.kamada_kawai_layout(self.G)
            except:
                # Fallback if the graph is not connected
                pos = nx.spring_layout(self.G, seed=42)
        elif layout_algo == "spectral":
            try:
                pos = nx.spectral_layout(self.G)
            except:
                # Fallback if spectral layout fails
                pos = nx.spring_layout(self.G, seed=42)
        else:
            pos = nx.spring_layout(self.G, seed=42)
        
        # Get visualization parameters
        node_size = self.node_size_var.get()
        edge_width = self.edge_width_var.get()
        label_size = self.label_size_var.get()
        
        # Update status
        self.status_bar.config(text="Drawing graph...")
        
        # Limit number of nodes for performance
        max_nodes_to_draw = 1000
        max_edges_to_draw = 2000
        
        # Create subset of nodes to visualize if there are too many
        nodes_to_draw = list(self.G.nodes())
        if len(nodes_to_draw) > max_nodes_to_draw:
            # Prioritize selected node and its neighbors
            if self.selected_node and self.selected_node in self.G.nodes():
                # Include the selected node and its neighbors first
                priority_nodes = [self.selected_node] + list(self.G.neighbors(self.selected_node))
                other_nodes = [n for n in nodes_to_draw if n not in priority_nodes]
                
                # Randomly select remaining nodes to reach the limit
                remaining_slots = max_nodes_to_draw - len(priority_nodes)
                if remaining_slots > 0:
                    other_nodes_sample = random.sample(other_nodes, min(remaining_slots, len(other_nodes)))
                    nodes_to_draw = priority_nodes + other_nodes_sample
                else:
                    nodes_to_draw = priority_nodes[:max_nodes_to_draw]
                
                # Update the user
                self.status_bar.config(text=f"Drawing partial graph ({len(nodes_to_draw)} of {len(self.G.nodes())} nodes)...")
            else:
                # Random sampling if no node is selected
                nodes_to_draw = random.sample(nodes_to_draw, max_nodes_to_draw)
                self.status_bar.config(text=f"Drawing partial graph (random {max_nodes_to_draw} of {len(self.G.nodes())} nodes)...")
        
        # Create subgraph for visualization
        subgraph = self.G.subgraph(nodes_to_draw)
        
        # Limit edges if there are too many
        edges_to_draw = list(subgraph.edges())
        if len(edges_to_draw) > max_edges_to_draw:
            # Prioritize edges connected to the selected node
            if self.selected_node and self.selected_node in subgraph:
                priority_edges = []
                for u, v in edges_to_draw:
                    if u == self.selected_node or v == self.selected_node:
                        priority_edges.append((u, v))
                
                other_edges = [e for e in edges_to_draw if e not in priority_edges]
                remaining_slots = max_edges_to_draw - len(priority_edges)
                
                if remaining_slots > 0:
                    other_edges_sample = random.sample(other_edges, min(remaining_slots, len(other_edges)))
                    edges_to_draw = priority_edges + other_edges_sample
                else:
                    edges_to_draw = priority_edges[:max_edges_to_draw]
            else:
                # Random sampling if no edge is selected
                edges_to_draw = random.sample(edges_to_draw, max_edges_to_draw)
        
        # Draw nodes
        node_colors = {}
        for node in subgraph.nodes:
            # Generate consistent colors based on node ID
            random.seed(node)
            color = (random.random(), random.random(), random.random())
            node_colors[node] = color
        
        nx.draw_networkx_nodes(
            subgraph, pos,
            node_size=node_size,
            node_color=[node_colors[node] for node in subgraph.nodes],
            alpha=0.8,
            linewidths=2,
            edgecolors='black',
            picker=5  # Enable picking
        )
        
        # Draw edges with arrows
        nx.draw_networkx_edges(
            subgraph, pos,
            edgelist=edges_to_draw,
            width=edge_width,
            alpha=0.7,
            edge_color='gray',
            arrowsize=15,
            connectionstyle='arc3,rad=0.1',
            arrowstyle='-|>',
            picker=5  # Enable picking
        )
        
        # Draw labels only for a limited subset if there are too many nodes
        max_labels = 100  # Limit the number of labels to avoid clutter
        if len(subgraph.nodes) > max_labels:
            # Priority for selected node and neighbors
            if self.selected_node and self.selected_node in subgraph:
                # Include selected node and direct neighbors
                label_nodes = [self.selected_node] + list(subgraph.neighbors(self.selected_node))
                
                # Add more random nodes if needed
                remaining_slots = max_labels - len(label_nodes)
                other_nodes = [n for n in subgraph.nodes if n not in label_nodes]
                if remaining_slots > 0 and other_nodes:
                    label_nodes.extend(random.sample(other_nodes, min(remaining_slots, len(other_nodes))))
            else:
                # Random subset of nodes for labels
                label_nodes = random.sample(list(subgraph.nodes), max_labels)
                
            # Create labels dict for just these nodes
            labels = {node: subgraph.nodes[node]['label'] for node in label_nodes}
        else:
            # Use all node labels if we're under the limit
            labels = nx.get_node_attributes(subgraph, 'label')
        
        # Draw labels
        nx.draw_networkx_labels(
            subgraph, pos,
            labels=labels,
            font_size=label_size,
            font_weight='bold',
            font_color='black'
        )
        
        # Highlight selected node/edge if any
        if self.selected_node is not None and self.selected_node in subgraph.nodes:
            nx.draw_networkx_nodes(
                subgraph, pos,
                nodelist=[self.selected_node],
                node_size=node_size * 1.2,
                node_color='yellow',
                edgecolors='red',
                linewidths=3
            )
        
        if self.selected_edge is not None:
            if self.selected_edge in subgraph.edges:
                nx.draw_networkx_edges(
                    subgraph, pos,
                    edgelist=[self.selected_edge],
                    width=edge_width * 2,
                    edge_color='red',
                    arrowsize=20,
                    connectionstyle='arc3,rad=0.1',
                    arrowstyle='-|>'
                )
        
        # Add legend
        legend_patches = []
        if len(subgraph.nodes) > max_nodes_to_draw:
            legend_patches.append(mpatches.Patch(color='gray', label=f'Showing {len(subgraph.nodes)}/{len(self.G.nodes)} nodes'))
        legend_patches.append(mpatches.Patch(color='yellow', label='Selected Node'))
        legend_patches.append(mpatches.Patch(color='red', label='Selected Edge'))
        self.ax.legend(handles=legend_patches, loc='upper right')
        
        # Remove axes and set title
        self.ax.set_axis_off()
        self.ax.set_title("Entity Relationship Graph")
        
        # Update canvas
        self.canvas.draw()
        
        # Update status
        self.status_bar.config(text=f"Graph rendered with {len(subgraph.nodes)} nodes and {len(edges_to_draw)} edges")
    
    def on_pick(self, event):
        if not self.is_data_loaded:
            return
            
        # Reset selection
        self.selected_node = None
        self.selected_edge = None
        
        # Check if a node was picked
        if hasattr(event, 'ind') and hasattr(event, 'artist') and hasattr(event.artist, '_offsets3d'):
            # Node picked
            ind = event.ind[0]
            nodes = list(self.G.nodes())
            if ind < len(nodes):
                self.selected_node = nodes[ind]
                
                # Update entity tree selection
                for item in self.entity_tree.get_children():
                    if self.entity_tree.item(item, 'values')[0] == str(self.selected_node):
                        self.entity_tree.selection_set(item)
                        self.entity_tree.see(item)
                        break
                
                self.status_bar.config(text=f"Selected Entity {self.selected_node}: {self.entities.get(self.selected_node, '')}")
        
        # Check if an edge was picked
        elif hasattr(event, 'artist') and hasattr(event.artist, '_path'):
            # Edge picked - this is more complex due to how matplotlib handles edges
            # Get edge closest to the click (simplified approach)
            pos = nx.get_node_attributes(self.G, 'pos')
            if not pos:
                # If positions are not stored as attributes, recompute them
                layout_algo = self.layout_var.get()
                if layout_algo == "spring":
                    pos = nx.spring_layout(self.G, seed=42)
                elif layout_algo == "circular":
                    pos = nx.circular_layout(self.G)
                elif layout_algo == "random":
                    pos = nx.random_layout(self.G)
                elif layout_algo == "kamada_kawai":
                    try:
                        pos = nx.kamada_kawai_layout(self.G)
                    except:
                        pos = nx.spring_layout(self.G, seed=42)
                elif layout_algo == "spectral":
                    try:
                        pos = nx.spectral_layout(self.G)
                    except:
                        pos = nx.spring_layout(self.G, seed=42)
                else:
                    pos = nx.spring_layout(self.G, seed=42)
            
            # Get mouse position
            mouse_x, mouse_y = event.mouseevent.xdata, event.mouseevent.ydata
            
            # Find closest edge
            min_dist = float('inf')
            for u, v in self.G.edges():
                if u in pos and v in pos:
                    # Simple line distance
                    x1, y1 = pos[u]
                    x2, y2 = pos[v]
                    
                    # Calculate distance from point to line segment
                    # (this is a simplified approach)
                    line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    if line_length == 0:
                        continue
                        
                    # Distance from point to line
                    dist = abs((y2 - y1)*mouse_x - (x2 - x1)*mouse_y + x2*y1 - y2*x1) / line_length
                    
                    if dist < min_dist:
                        min_dist = dist
                        self.selected_edge = (u, v)
            
            if self.selected_edge and min_dist < 0.1:  # Threshold for selection
                # Find the relationship in the data
                for rel in self.relationships:
                    if (rel['property_id'] == self.selected_edge[0] and 
                        rel['related_id'] == self.selected_edge[1]):
                        # Update relationship tree selection
                        for item in self.rel_tree.get_children():
                            if self.rel_tree.item(item, 'values')[0] == str(rel['id']):
                                self.rel_tree.selection_set(item)
                                self.rel_tree.see(item)
                                break
                        
                        self.status_bar.config(text=f"Selected Relationship {rel['id']}: "
                                                  f"{self.entities.get(rel['property_id'], '')} → "
                                                  f"{self.entities.get(rel['related_id'], '')}")
                        break
        
        # Redraw to show selection
        self.visualize_graph()
    
    def on_entity_select(self, event):
        if not self.is_data_loaded:
            return

        selected_items = self.entity_tree.selection()
        if not selected_items:
            return

        # Get the entity ID from the selection
        entity_id = int(self.entity_tree.item(selected_items[0], 'values')[0])

        # Update selection
        self.selected_node = entity_id
        self.selected_edge = None

        # Highlight in graph
        self.visualize_graph()

        # Update status
        self.status_bar.config(text=f"Selected Entity {entity_id}: {self.entities.get(entity_id, '')}")

    def on_relationship_select(self, event):
        if not self.is_data_loaded:
            return

        selected_items = self.rel_tree.selection()
        if not selected_items:
            return

        # Get the relationship ID from the selection
        rel_id = int(self.rel_tree.item(selected_items[0], 'values')[0])

        # Find the relationship in our data
        for rel in self.relationships:
            if rel['id'] == rel_id:
                if rel['related_id'] is not None:
                    # Update selection
                    self.selected_node = None
                    self.selected_edge = (rel['property_id'], rel['related_id'])

                    # Highlight in graph
                    self.visualize_graph()

                    # Update status
                    self.status_bar.config(text=f"Selected Relationship {rel_id}: "
                                              f"{self.entities.get(rel['property_id'], '')} → "
                                              f"{self.entities.get(rel['related_id'], '')}")
                break

    def center_on_selection(self):
        if not self.is_data_loaded:
            messagebox.showinfo("No Data", "Please load data first.")
            return

        # Center the graph on the currently selected node
        if self.selected_node is not None and self.selected_node in self.G.nodes:
            # This is implemented by redrawing the graph, which is already centered
            self.visualize_graph()
            self.status_bar.config(text=f"Centered on Entity {self.selected_node}")
        elif self.selected_edge is not None:
            # Center on the edge's source and target
            self.visualize_graph()
            self.status_bar.config(text=f"Centered on Edge {self.selected_edge}")
        else:
            messagebox.showinfo("No Selection", "Please select a node or edge to center on.")

    def save_graph_image(self):
        if not self.is_data_loaded:
            messagebox.showinfo("No Data", "Please load data first.")
            return

        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if file_path:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
            self.status_bar.config(text=f"Graph saved to {file_path}")

    def __del__(self):
        # Close database connection when object is destroyed
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()


def main():
    root = tk.Tk()
    app = EntityRelationshipGraphGUI(root, "EntityRelationship.sqlite3")
    root.mainloop()


if __name__ == "__main__":
    main()
