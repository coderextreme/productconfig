import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import numpy as np
import matplotlib.patches as mpatches
import random

class EntityRelationshipGraphGUI:
    def __init__(self, root, db_path):
        self.root = root
        self.db_path = db_path
        self.root.title("Entity Relationship Graph Viewer")
        self.root.geometry("1200x800")

        # Initialize database connection
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

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

        # Setup controls
        self.setup_controls()

        # Create graph visualization
        self.setup_graph()

        # Entity and Relationship data
        self.entities = {}
        self.relationships = []

        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Load data and visualize
        self.load_data()
        self.visualize_graph()

    def setup_controls(self):
        control_inner = ttk.Frame(self.control_frame)
        control_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        
        # Buttons
        button_frame = ttk.Frame(control_inner)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Refresh Data", command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Redraw Graph", command=self.visualize_graph).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Center on Selection", command=self.center_on_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Graph Image", command=self.save_graph_image).pack(side=tk.LEFT, padx=5)
    
    def setup_graph(self):
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create network graph
        self.G = nx.DiGraph()
        
        # Interaction
        self.selected_node = None
        self.selected_edge = None
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)
        
    def load_data(self):
        try:
            # Clear existing data
            for item in self.entity_tree.get_children():
                self.entity_tree.delete(item)
            
            for item in self.rel_tree.get_children():
                self.rel_tree.delete(item)
            
            # Get entity data from database
            self.cursor.execute("""
                SELECT ID, 
                       COALESCE(TEXT_VALUE, 
                              COALESCE(CAST(INTEGER_VALUE AS TEXT), 
                                     COALESCE(BOOLEAN_VALUE, 
                                            COALESCE(CAST(REAL_VALUE AS TEXT), 
                                                   COALESCE(CAST(NUMERIC_VALUE AS TEXT), 
                                                          'Entity ' || ID))))) AS DISPLAY_VALUE
                FROM Entity
                ORDER BY ID
            """)
            
            self.entities = {}
            for row in self.cursor.fetchall():
                entity_id, display_value = row
                self.entities[entity_id] = display_value
                self.entity_tree.insert("", tk.END, values=(entity_id, display_value))
            
            # Get relationship data from database
            self.cursor.execute("""
                SELECT r.ID, r.PROPERTY_ID, r.RELATED_ID
                FROM Relationship r
                ORDER BY r.ID
            """)
            
            self.relationships = []
            for row in self.cursor.fetchall():
                rel_id, property_id, related_id = row
                self.relationships.append({
                    'id': rel_id,
                    'property_id': property_id,
                    'related_id': related_id
                })
                
                # Get display values for the related entities
                property_value = self.entities.get(property_id, f"Entity {property_id}")
                related_value = self.entities.get(related_id, "None") if related_id else "None"
                
                self.rel_tree.insert("", tk.END, values=(rel_id, property_value, related_value))
            
            self.status_bar.config(text=f"Loaded {len(self.entities)} entities and {len(self.relationships)} relationships")
            
            # Update graph
            self.build_graph()
            self.visualize_graph()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading data: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")
    
    def build_graph(self):
        # Clear existing graph
        self.G.clear()
        
        # Add nodes for all entities
        for entity_id, display_value in self.entities.items():
            # Truncate display value if too long
            if display_value and len(display_value) > 20:
                display_value = display_value[:17] + "..."
            
            self.G.add_node(entity_id, label=display_value or f"Entity {entity_id}")
        
        # Add edges for relationships
        for rel in self.relationships:
            if rel['related_id'] is not None:  # Only add if there's a related entity
                self.G.add_edge(rel['property_id'], rel['related_id'], id=rel['id'])
    
    def visualize_graph(self):
        # Clear the axes
        self.ax.clear()
        
        if not self.G.nodes:
            self.ax.text(0.5, 0.5, "No data to display", 
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
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
        
        # Draw nodes
        node_colors = {}
        for node in self.G.nodes:
            # Generate consistent colors based on node ID
            random.seed(node)
            color = (random.random(), random.random(), random.random())
            node_colors[node] = color
        
        nx.draw_networkx_nodes(
            self.G, pos,
            node_size=node_size,
            node_color=[node_colors[node] for node in self.G.nodes],
            alpha=0.8,
            linewidths=2,
            edgecolors='black',
            picker=5  # Enable picking
        )
        
        # Draw edges with arrows
        nx.draw_networkx_edges(
            self.G, pos,
            width=edge_width,
            alpha=0.7,
            edge_color='gray',
            arrowsize=15,
            connectionstyle='arc3,rad=0.1',
            arrowstyle='-|>',
            picker=5  # Enable picking
        )
        
        # Draw labels
        labels = nx.get_node_attributes(self.G, 'label')
        nx.draw_networkx_labels(
            self.G, pos,
            labels=labels,
            font_size=label_size,
            font_weight='bold',
            font_color='black'
        )
        
        # Highlight selected node/edge if any
        if self.selected_node is not None and self.selected_node in self.G.nodes:
            nx.draw_networkx_nodes(
                self.G, pos,
                nodelist=[self.selected_node],
                node_size=node_size * 1.2,
                node_color='yellow',
                edgecolors='red',
                linewidths=3
            )
        
        if self.selected_edge is not None:
            if self.selected_edge in self.G.edges:
                nx.draw_networkx_edges(
                    self.G, pos,
                    edgelist=[self.selected_edge],
                    width=edge_width * 2,
                    edge_color='red',
                    arrowsize=20,
                    connectionstyle='arc3,rad=0.1',
                    arrowstyle='-|>'
                )
        
        # Add legend
        legend_patches = []
        legend_patches.append(mpatches.Patch(color='yellow', label='Selected Node'))
        legend_patches.append(mpatches.Patch(color='red', label='Selected Edge'))
        self.ax.legend(handles=legend_patches, loc='upper right')
        
        # Remove axes and set title
        self.ax.set_axis_off()
        self.ax.set_title("Entity Relationship Graph")
        
        # Update canvas
        self.canvas.draw()
    
    def on_pick(self, event):
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
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    root = tk.Tk()
    app = EntityRelationshipGraphGUI(root, "EntityRelationship.sqlite3")
    root.mainloop()


if __name__ == "__main__":
    main()
