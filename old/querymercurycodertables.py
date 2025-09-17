import tkinter as tk
from tkinter import ttk
import sqlite3

# Database connection
def get_db_connection():
    conn = sqlite3.connect("EntityRelationship.sqlite3")
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# Fetch entities from the database
def fetch_entities():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Entity")
    entities = cursor.fetchall()
    conn.close()
    return entities

# Fetch relationships for a given entity ID
def fetch_relationships(entity_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Relationship WHERE PROPERTY_ID = ? OR RELATED_ID = ?", (entity_id, entity_id))
    relationships = cursor.fetchall()
    conn.close()
    return relationships

# Update the relationships table when an entity is selected
def update_relationships_table(entity_id):
    relationships = fetch_relationships(entity_id)
    for row in relationships_table.get_children():
        relationships_table.delete(row)
    for relationship in relationships:
        relationships_table.insert("", "end", values=relationship)

# Create the main window
root = tk.Tk()
root.title("Entity-Relationship Database")

# Create a treeview for entities
entities_tree = ttk.Treeview(root, columns=("ID", "INTEGER_VALUE", "TEXT_VALUE", "BOOLEAN_VALUE", "BLOB_VALUE", "REAL_VALUE", "NUMERIC_VALUE"), show="headings")
entities_tree.heading("ID", text="ID")
entities_tree.heading("INTEGER_VALUE", text="INTEGER_VALUE")
entities_tree.heading("TEXT_VALUE", text="TEXT_VALUE")
entities_tree.heading("BOOLEAN_VALUE", text="BOOLEAN_VALUE")
entities_tree.heading("BLOB_VALUE", text="BLOB_VALUE")
entities_tree.heading("REAL_VALUE", text="REAL_VALUE")
entities_tree.heading("NUMERIC_VALUE", text="NUMERIC_VALUE")
entities_tree.pack(side=tk.LEFT, fill=tk.BOTH)

# Create a treeview for relationships
relationships_table = ttk.Treeview(root, columns=("ID", "PROPERTY_ID", "RELATED_ID"), show="headings")
relationships_table.heading("ID", text="ID")
relationships_table.heading("PROPERTY_ID", text="PROPERTY_ID")
relationships_table.heading("RELATED_ID", text="RELATED_ID")
relationships_table.pack(side=tk.RIGHT, fill=tk.BOTH)

# Populate the entities tree
entities = fetch_entities()
for entity in entities:
    entities_tree.insert("", "end", values=entity)

# Bind the selection event to update the relationships table
entities_tree.bind("<<TreeviewSelect>>", lambda event: update_relationships_table(entities_tree.selection()[0]))

# Start the Tkinter event loop
root.mainloop()
