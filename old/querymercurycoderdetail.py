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

# Fetch relationships from the database
def fetch_relationships():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Relationship")
    relationships = cursor.fetchall()
    conn.close()
    return relationships

# Fetch an entity by ID
def fetch_entity_by_id(entity_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Entity WHERE ID = ?", (entity_id,))
    entity = cursor.fetchone()
    conn.close()
    return entity

# Update the relationships table when an entity is selected
def update_relationships_table(entity_id):
    relationships = fetch_relationships()
    for row in relationships_table.get_children():
        relationships_table.delete(row)
    for relationship in relationships:
        relationships_table.insert("", "end", values=relationship)

# Update the entities table when a relationship is selected
def update_entities_table(event):
    selected_item = relationships_table.selection()
    if selected_item:
        relationship_id = relationships_table.item(selected_item[0], "values")[0]
        relationship = fetch_relationships()
        for rel in relationship:
            if rel[0] == relationship_id:
                property_id = rel[1]
                related_id = rel[2]
                property_entity = fetch_entity_by_id(property_id)
                related_entity = fetch_entity_by_id(related_id)
                
                # Clear the entities table
                for row in entities_tree.get_children():
                    entities_tree.delete(row)
                
                # Insert the selected entities
                if property_entity:
                    entities_tree.insert("", "end", values=property_entity)
                if related_entity:
                    entities_tree.insert("", "end", values=related_entity)
                break

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

# Populate the relationships tree
relationships = fetch_relationships()
for relationship in relationships:
    relationships_table.insert("", "end", values=relationship)

# Bind the selection event to update the relationships table
entities_tree.bind("<<TreeviewSelect>>", lambda event: update_relationships_table(entities_tree.selection()[0]))

# Bind the selection event to update the entities table
relationships_table.bind("<<TreeviewSelect>>", update_entities_table)

# Start the Tkinter event loop
root.mainloop()
