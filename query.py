import sqlite3
import tkinter as tk
from tkinter import ttk

def add_filters():
    # Fetch distinct property names from the database
    cursor.execute("SELECT DISTINCT PROPERTY_NAME FROM Objects")
    property_names = [record[0] for record in cursor.fetchall()]

    # Create a dictionary to store the state of each checkbox for each property name
    checkbox_vars = {prop: [] for prop in property_names}

    # Create checkboxes for each property name and its top 20 unique values
    for prop in property_names:
        # Create a frame for each property group
        prop_frame = ttk.LabelFrame(checkbox_inner_frame, text=prop)
        prop_frame.pack(fill=tk.X, padx=5, pady=5, anchor=tk.W)

        # Query and create checkboxes for unique values
        cursor.execute(f"""
            SELECT RELATED_ID, INTEGER_VALUE, TEXT_VALUE, BOOLEAN_VALUE, BLOB_VALUE, REAL_VALUE, NUMERIC_VALUE
            FROM Objects
            WHERE PROPERTY_NAME = ?
            GROUP BY RELATED_ID, INTEGER_VALUE, TEXT_VALUE, BOOLEAN_VALUE, BLOB_VALUE, REAL_VALUE, NUMERIC_VALUE
            ORDER BY COUNT(*) DESC
            LIMIT 20
        """, (prop,))

        values = cursor.fetchall()
        unique_values = set()

        for value in values:
            for val in value:
                if val is not None and val not in unique_values:
                    unique_values.add(val)
                    var = tk.BooleanVar()
                    checkbox_vars[prop].append((val, var))
                    checkbox = ttk.Checkbutton(
                        prop_frame,
                        text=str(val),
                        variable=var,
                        onvalue=True,
                        offvalue=False
                    )
                    checkbox.pack(anchor=tk.W)

    # Function to execute the query based on selected properties
    def execute_query():
        selected_values = []
        for prop, vals in checkbox_vars.items():
            for val, var in vals:
                if var.get():
                    selected_values.append((prop, val))
        if not selected_values:
            # Clear previous results
            for row in tree.get_children():
                tree.delete(row)
            tree.insert("", "end", values=("No properties selected.", "", ""))
            return

        query = f"SELECT ID, PROPERTY_NAME, RELATED_ID, INTEGER_VALUE, TEXT_VALUE, BOOLEAN_VALUE, BLOB_VALUE, REAL_VALUE, NUMERIC_VALUE FROM Objects WHERE {' OR '.join([f'(PROPERTY_NAME = ? AND (RELATED_ID = ? OR INTEGER_VALUE = ? OR TEXT_VALUE = ? OR BOOLEAN_VALUE = ? OR BLOB_VALUE = ? OR REAL_VALUE = ? OR NUMERIC_VALUE = ?))' for _ in selected_values])}"
        params = []
        for prop, val in selected_values:
            params.extend([prop, val, val, val, val, val, val, val])
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        # Clear previous results
        for row in tree.get_children():
            tree.delete(row)

        # Insert new results into the treeview
        for row in results:
            id_value = row[0]
            property_name = row[1]
            non_none_values = [value for value in row[2:] if value is not None]
            value_str = ", ".join(map(str, non_none_values))
            tree.insert("", "end", values=(id_value, property_name, value_str))

    # Update the command for the query button
    query_button.config(command=execute_query)

# Connect to the database
connection = sqlite3.connect("ThreeDimAssets.sqlite3")
cursor = connection.cursor()

# Create the main application window
root = tk.Tk()
root.title("Database Query GUI")

# Create a frame for the checkboxes with a scrollbar
checkbox_frame = ttk.Frame(root)
checkbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

checkbox_canvas = tk.Canvas(checkbox_frame)
checkbox_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

checkbox_scrollbar = ttk.Scrollbar(checkbox_frame, orient="vertical", command=checkbox_canvas.yview)
checkbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

checkbox_canvas.configure(yscrollcommand=checkbox_scrollbar.set)
checkbox_canvas.bind('<Configure>', lambda e: checkbox_canvas.configure(scrollregion=checkbox_canvas.bbox("all")))

checkbox_inner_frame = ttk.Frame(checkbox_canvas)
checkbox_canvas.create_window((0, 0), window=checkbox_inner_frame, anchor="nw")

# Create a frame for the results with a scrollbar
result_frame = ttk.Frame(root)
result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

result_canvas = tk.Canvas(result_frame)
result_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_canvas.yview)
result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

result_canvas.configure(yscrollcommand=result_scrollbar.set)
result_canvas.bind('<Configure>', lambda e: result_canvas.configure(scrollregion=result_canvas.bbox("all")))

result_inner_frame = ttk.Frame(result_canvas)
result_canvas.create_window((0, 0), window=result_inner_frame, anchor="nw")

# Create a Treeview widget to display the query results
tree = ttk.Treeview(result_inner_frame, columns=("ID", "PROPERTY_NAME", "VALUE"), show="headings")
tree.heading("ID", text="ID")
tree.heading("PROPERTY_NAME", text="PROPERTY_NAME")
tree.heading("VALUE", text="VALUE")
tree.pack(fill=tk.BOTH, expand=True)

# Create a frame for the filename search
filename_frame = ttk.Frame(root)
filename_frame.pack(side=tk.TOP, fill=tk.X)

filename_label = ttk.Label(filename_frame, text="Search Filename:")
filename_label.pack(side=tk.LEFT)

filename_entry = ttk.Entry(filename_frame)
filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Function to execute the filename search
def search_filename():
    filename = filename_entry.get()
    if not filename:
        # Clear previous results
        for row in tree.get_children():
            tree.delete(row)
        tree.insert("", "end", values=("No filename entered.", "", ""))
        return

    query = """
    SELECT ID, PROPERTY_NAME, RELATED_ID, INTEGER_VALUE, TEXT_VALUE, BOOLEAN_VALUE, BLOB_VALUE, REAL_VALUE, NUMERIC_VALUE
    FROM Objects
    WHERE TEXT_VALUE LIKE ? COLLATE NOCASE
    """
    cursor.execute(query, (f"%{filename}%",))
    results = cursor.fetchall()

    # Clear previous results
    for row in tree.get_children():
        tree.delete(row)

    # Insert new results into the Treeview
    for row in results:
        id_value = row[0]
        property_name = row[1]
        non_none_values = [value for value in row[2:] if value is not None]
        value_str = ", ".join(map(str, non_none_values))
        tree.insert("", "end", values=(id_value, property_name, value_str))

# Create a button to execute the filename search
search_button = ttk.Button(filename_frame, text="Search", command=search_filename)
search_button.pack(side=tk.RIGHT)

# Create a button to add filters
add_filters_button = ttk.Button(root, text="Add Filters", command=add_filters)
add_filters_button.pack()

# Create a button to execute the query
query_button = ttk.Button(root, text="Execute Query")
query_button.pack()

# Run the application
root.mainloop()

# Commit changes and close the connection
connection.commit()
connection.close()
