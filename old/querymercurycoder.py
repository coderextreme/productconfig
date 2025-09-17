import sqlite3
import tkinter as tk
from tkinter import messagebox


def get_db_connection():
    conn = sqlite3.connect("EntityRelationship.sqlite3")
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

# Function to create the main window
def create_main_window():
    root = tk.Tk()
    root.title("Entity-Relationship Database")

    # Create frames for different sections
    entity_frame = tk.Frame(root)
    entity_frame.pack(pady=10)

    relationship_frame = tk.Frame(root)
    relationship_frame.pack(pady=10)

    # Entity frame
    tk.Label(entity_frame, text="Entity ID").grid(row=0, column=0, padx=5, pady=5)
    entity_id_entry = tk.Entry(entity_frame)
    entity_id_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(entity_frame, text="Integer Value").grid(row=1, column=0, padx=5, pady=5)
    integer_value_entry = tk.Entry(entity_frame)
    integer_value_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(entity_frame, text="Text Value").grid(row=2, column=0, padx=5, pady=5)
    text_value_entry = tk.Entry(entity_frame)
    text_value_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(entity_frame, text="Boolean Value").grid(row=3, column=0, padx=5, pady=5)
    boolean_value_entry = tk.Entry(entity_frame)
    boolean_value_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Label(entity_frame, text="Blob Value").grid(row=4, column=0, padx=5, pady=5)
    blob_value_entry = tk.Entry(entity_frame)
    blob_value_entry.grid(row=4, column=1, padx=5, pady=5)

    tk.Label(entity_frame, text="Real Value").grid(row=5, column=0, padx=5, pady=5)
    real_value_entry = tk.Entry(entity_frame)
    real_value_entry.grid(row=5, column=1, padx=5, pady=5)

    tk.Label(entity_frame, text="Numeric Value").grid(row=6, column=0, padx=5, pady=5)
    numeric_value_entry = tk.Entry(entity_frame)
    numeric_value_entry.grid(row=6, column=1, padx=5, pady=5)

    # Buttons for Entity operations
    tk.Button(entity_frame, text="Add Entity", command=lambda: add_entity(entity_id_entry, integer_value_entry, text_value_entry, boolean_value_entry, blob_value_entry, real_value_entry, numeric_value_entry)).grid(row=7, column=0, padx=5, pady=5)
    tk.Button(entity_frame, text="Update Entity", command=lambda: update_entity(entity_id_entry, integer_value_entry, text_value_entry, boolean_value_entry, blob_value_entry, real_value_entry, numeric_value_entry)).grid(row=7, column=1, padx=5, pady=5)
    tk.Button(entity_frame, text="Delete Entity", command=lambda: delete_entity(entity_id_entry)).grid(row=8, column=0, padx=5, pady=5)
    tk.Button(entity_frame, text="View Entities", command=view_entities).grid(row=8, column=1, padx=5, pady=5)

    # Relationship frame
    tk.Label(relationship_frame, text="Relationship ID").grid(row=0, column=0, padx=5, pady=5)
    relationship_id_entry = tk.Entry(relationship_frame)
    relationship_id_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(relationship_frame, text="Property ID").grid(row=1, column=0, padx=5, pady=5)
    property_id_entry = tk.Entry(relationship_frame)
    property_id_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(relationship_frame, text="Related ID").grid(row=2, column=0, padx=5, pady=5)
    related_id_entry = tk.Entry(relationship_frame)
    related_id_entry.grid(row=2, column=1, padx=5, pady=5)

    # Buttons for Relationship operations
    tk.Button(relationship_frame, text="Add Relationship", command=lambda: add_relationship(relationship_id_entry, property_id_entry, related_id_entry)).grid(row=3, column=0, padx=5, pady=5)
    tk.Button(relationship_frame, text="Update Relationship", command=lambda: update_relationship(relationship_id_entry, property_id_entry, related_id_entry)).grid(row=3, column=1, padx=5, pady=5)
    tk.Button(relationship_frame, text="Delete Relationship", command=lambda: delete_relationship(relationship_id_entry)).grid(row=4, column=0, padx=5, pady=5)
    tk.Button(relationship_frame, text="View Relationships", command=view_relationships).grid(row=4, column=1, padx=5, pady=5)

    root.mainloop()

# Functions to interact with the database
def add_entity(entity_id, integer_value, text_value, boolean_value, blob_value, real_value, numeric_value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Entity (ID, INTEGER_VALUE, TEXT_VALUE, BOOLEAN_VALUE, BLOB_VALUE, REAL_VALUE, NUMERIC_VALUE)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (entity_id.get(), integer_value.get(), text_value.get(), boolean_value.get(), blob_value.get(), real_value.get(), numeric_value.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Entity added successfully")

def update_entity(entity_id, integer_value, text_value, boolean_value, blob_value, real_value, numeric_value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE Entity SET INTEGER_VALUE = ?, TEXT_VALUE = ?, BOOLEAN_VALUE = ?, BLOB_VALUE = ?, REAL_VALUE = ?, NUMERIC_VALUE = ?
                       WHERE ID = ?''',
                   (integer_value.get(), text_value.get(), boolean_value.get(), blob_value.get(), real_value.get(), numeric_value.get(), entity_id.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Entity updated successfully")

def delete_entity(entity_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Entity WHERE ID = ?', (entity_id.get(),))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Entity deleted successfully")

def view_entities():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Entity')
    rows = cursor.fetchall()
    conn.close()
    print(rows)  # You can replace this with a more sophisticated display method

def add_relationship(relationship_id, property_id, related_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Relationship (ID, PROPERTY_ID, RELATED_ID)
                       VALUES (?, ?, ?)''',
                   (relationship_id.get(), property_id.get(), related_id.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Relationship added successfully")

def update_relationship(relationship_id, property_id, related_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE Relationship SET PROPERTY_ID = ?, RELATED_ID = ?
                       WHERE ID = ?''',
                   (property_id.get(), related_id.get(), relationship_id.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Relationship updated successfully")

def delete_relationship(relationship_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Relationship WHERE ID = ?', (relationship_id.get(),))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Relationship deleted successfully")

def view_relationships():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Relationship')
    rows = cursor.fetchall()
    conn.close()
    print(rows)  # You can replace this with a more sophisticated display method

# Start the application
if __name__ == "__main__":
    create_main_window()
