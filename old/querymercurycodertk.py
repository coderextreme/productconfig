import tkinter as tk
from tkinter import ttk
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Connect to the SQLite database
connection = sqlite3.connect("EntityRelationship.sqlite3")
connection.execute('PRAGMA foreign_keys = ON')

def get_entities():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Entity")
    return cursor.fetchall()

def get_relationships():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Relationship")
    return cursor.fetchall()

def build_graph():
    G = nx.DiGraph()
    entities = get_entities()
    relationships = get_relationships()

    # Add nodes (entities)
    for entity in entities:
        G.add_node(entity[0], data=entity)

    # Add edges (relationships)
    for relationship in relationships:
        G.add_edge(relationship[1], relationship[2])

    return G

def plot_graph(G):
    pos = nx.spring_layout(G)  # positions for all nodes
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10, font_weight='bold', arrows=True, ax=ax)
    return fig

class GraphApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Entity-Relationship Graph")
        self.geometry("800x600")

        self.G = build_graph()
        self.fig = plot_graph(self.G)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

if __name__ == '__main__':
    app = GraphApp()
    app.mainloop()
