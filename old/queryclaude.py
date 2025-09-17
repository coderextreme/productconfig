import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import pandas as pd
from tkinter import filedialog
import io

class EntityRelationshipGUI:
    def __init__(self, root, db_path):
        self.root = root
        self.db_path = db_path
        self.root.title("Entity Relationship Database Manager")
        self.root.geometry("1000x700")
        
        # Initialize database connection
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # Entity Tab
        self.entity_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.entity_tab, text="Entities")
        
        # Relationship Tab
        self.relationship_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.relationship_tab, text="Relationships")
        
        # Query Tab
        self.query_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.query_tab, text="Custom Query")
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Setup tabs
        self.setup_entity_tab()
        self.setup_relationship_tab()
        self.setup_query_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Menu Bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Export Data", command=self.export_data)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
        
        # Load initial data
        self.load_entity_data()
        self.load_relationship_data()
    
    def setup_entity_tab(self):
        # Left side - Entity list
        left_frame = ttk.Frame(self.entity_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Entity Treeview
        self.entity_tree = ttk.Treeview(left_frame, columns=("id", "integer", "text", "boolean", "blob", "real", "numeric"), show="headings")
        
        # Define headings
        self.entity_tree.heading("id", text="ID")
        self.entity_tree.heading("integer", text="INTEGER_VALUE")
        self.entity_tree.heading("text", text="TEXT_VALUE")
        self.entity_tree.heading("boolean", text="BOOLEAN_VALUE")
        self.entity_tree.heading("blob", text="BLOB_VALUE")
        self.entity_tree.heading("real", text="REAL_VALUE")
        self.entity_tree.heading("numeric", text="NUMERIC_VALUE")
        
        # Define columns
        self.entity_tree.column("id", width=50)
        self.entity_tree.column("integer", width=100)
        self.entity_tree.column("text", width=100)
        self.entity_tree.column("boolean", width=100)
        self.entity_tree.column("blob", width=100)
        self.entity_tree.column("real", width=100)
        self.entity_tree.column("numeric", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.entity_tree.yview)
        self.entity_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.entity_tree.pack(fill=tk.BOTH, expand=True)
        
        # Entity selection event
        self.entity_tree.bind("<<TreeviewSelect>>", self.on_entity_select)
        
        # Right side - Entity form
        right_frame = ttk.LabelFrame(self.entity_tab, text="Entity Details")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5, pady=5, ipadx=5, ipady=5)
        
        # Form fields
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Entity ID (read-only for existing records)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entity_id_var = tk.StringVar()
        self.entity_id_entry = ttk.Entry(form_frame, textvariable=self.entity_id_var, state="readonly")
        self.entity_id_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Integer Value
        ttk.Label(form_frame, text="Integer Value:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entity_integer_var = tk.StringVar()
        self.entity_integer_entry = ttk.Entry(form_frame, textvariable=self.entity_integer_var)
        self.entity_integer_entry.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Text Value
        ttk.Label(form_frame, text="Text Value:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entity_text_var = tk.StringVar()
        self.entity_text_entry = ttk.Entry(form_frame, textvariable=self.entity_text_var)
        self.entity_text_entry.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Boolean Value
        ttk.Label(form_frame, text="Boolean Value:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entity_boolean_var = tk.StringVar()
        self.entity_boolean_combo = ttk.Combobox(form_frame, textvariable=self.entity_boolean_var, values=["True", "False", ""])
        self.entity_boolean_combo.grid(row=3, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Real Value
        ttk.Label(form_frame, text="Real Value:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.entity_real_var = tk.StringVar()
        self.entity_real_entry = ttk.Entry(form_frame, textvariable=self.entity_real_var)
        self.entity_real_entry.grid(row=4, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Numeric Value
        ttk.Label(form_frame, text="Numeric Value:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.entity_numeric_var = tk.StringVar()
        self.entity_numeric_entry = ttk.Entry(form_frame, textvariable=self.entity_numeric_var)
        self.entity_numeric_entry.grid(row=5, column=1, sticky=tk.W+tk.E, pady=5)
        
        # BLOB placeholder (not directly editable)
        ttk.Label(form_frame, text="BLOB Value:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.entity_blob_var = tk.StringVar(value="[BLOB data]")
        self.entity_blob_entry = ttk.Entry(form_frame, textvariable=self.entity_blob_var, state="disabled")
        self.entity_blob_entry.grid(row=6, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="New", command=self.new_entity).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=self.save_entity).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_entity).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_entity_data).pack(side=tk.LEFT, padx=5)
    
    def setup_relationship_tab(self):
        # Top frame - Relationship list
        top_frame = ttk.Frame(self.relationship_tab)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Relationship Treeview
        self.relationship_tree = ttk.Treeview(top_frame, columns=("id", "property_id", "property_value", "related_id", "related_value"), show="headings")
        
        # Define headings
        self.relationship_tree.heading("id", text="ID")
        self.relationship_tree.heading("property_id", text="PROPERTY_ID")
        self.relationship_tree.heading("property_value", text="PROPERTY_VALUE")
        self.relationship_tree.heading("related_id", text="RELATED_ID")
        self.relationship_tree.heading("related_value", text="RELATED_VALUE")
        
        # Define columns
        self.relationship_tree.column("id", width=50)
        self.relationship_tree.column("property_id", width=100)
        self.relationship_tree.column("property_value", width=150)
        self.relationship_tree.column("related_id", width=100)
        self.relationship_tree.column("related_value", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=self.relationship_tree.yview)
        self.relationship_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.relationship_tree.pack(fill=tk.BOTH, expand=True)
        
        # Relationship selection event
        self.relationship_tree.bind("<<TreeviewSelect>>", self.on_relationship_select)
        
        # Bottom Frame - Relationship form
        bottom_frame = ttk.LabelFrame(self.relationship_tab, text="Relationship Details")
        bottom_frame.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)
        
        # Form fields
        form_frame = ttk.Frame(bottom_frame)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Relationship ID
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.relationship_id_var = tk.StringVar()
        self.relationship_id_entry = ttk.Entry(form_frame, textvariable=self.relationship_id_var, state="readonly")
        self.relationship_id_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Property Entity
        ttk.Label(form_frame, text="Property Entity:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.property_id_var = tk.StringVar()
        self.property_combo = ttk.Combobox(form_frame, textvariable=self.property_id_var)
        self.property_combo.grid(row=1, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Related Entity
        ttk.Label(form_frame, text="Related Entity:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.related_id_var = tk.StringVar()
        self.related_combo = ttk.Combobox(form_frame, textvariable=self.related_id_var)
        self.related_combo.grid(row=2, column=1, sticky=tk.W+tk.E, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="New", command=self.new_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save", command=self.save_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_relationship).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_relationship_data).pack(side=tk.LEFT, padx=5)
        
        # Load entity IDs for dropdowns
        self.update_entity_dropdowns()
    
    def setup_query_tab(self):
        query_frame = ttk.Frame(self.query_tab)
        query_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Query input
        ttk.Label(query_frame, text="Enter SQL Query:").pack(anchor=tk.W)
        self.query_text = tk.Text(query_frame, height=8)
        self.query_text.pack(fill=tk.X, pady=5)
        
        # Default queries for convenience
        sample_queries = [
            "SELECT * FROM Entity",
            "SELECT * FROM Relationship",
            "SELECT r.ID, r.PROPERTY_ID, e1.TEXT_VALUE as PROPERTY_VALUE, r.RELATED_ID, e2.TEXT_VALUE as RELATED_VALUE FROM Relationship r LEFT JOIN Entity e1 ON r.PROPERTY_ID = e1.ID LEFT JOIN Entity e2 ON r.RELATED_ID = e2.ID"
        ]
        
        # Query templates dropdown
        ttk.Label(query_frame, text="Choose a template:").pack(anchor=tk.W)
        self.query_template_var = tk.StringVar()
        self.query_template_combo = ttk.Combobox(query_frame, textvariable=self.query_template_var, values=sample_queries)
        self.query_template_combo.pack(fill=tk.X, pady=5)
        self.query_template_combo.bind("<<ComboboxSelected>>", self.load_query_template)
        
        # Execute button
        ttk.Button(query_frame, text="Execute Query", command=self.execute_query).pack(anchor=tk.W, pady=5)
        
        # Query results
        ttk.Label(query_frame, text="Query Results:").pack(anchor=tk.W, pady=5)
        
        # Results frame with scroll
        results_frame = ttk.Frame(query_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL)
        x_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL)
        
        # Results tree
        self.query_results = ttk.Treeview(results_frame, yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.query_results.yview)
        x_scrollbar.config(command=self.query_results.xview)
        
        # Pack scrollbars and treeview
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.query_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def load_query_template(self, event):
        selected_query = self.query_template_var.get()
        self.query_text.delete(1.0, tk.END)
        self.query_text.insert(tk.END, selected_query)
    
    def execute_query(self):
        query = self.query_text.get(1.0, tk.END).strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a SQL query.")
            return
        
        try:
            # Execute the query
            self.cursor.execute(query)
            
            # Clear existing results
            for item in self.query_results.get_children():
                self.query_results.delete(item)
            
            # Configure columns
            if self.cursor.description:
                # Get column names
                columns = [desc[0] for desc in self.cursor.description]
                
                # Configure treeview columns
                self.query_results['columns'] = columns
                self.query_results['show'] = 'headings'
                
                # Set up column headings
                for col in columns:
                    self.query_results.heading(col, text=col)
                    self.query_results.column(col, width=100)
                
                # Insert data
                for row in self.cursor.fetchall():
                    self.query_results.insert("", tk.END, values=row)
                
                self.status_bar.config(text=f"Query executed successfully. {len(self.query_results.get_children())} rows returned.")
            else:
                messagebox.showinfo("Query Result", "Query executed successfully. No data returned.")
                self.status_bar.config(text="Query executed successfully. No data returned.")
        
        except sqlite3.Error as e:
            messagebox.showerror("Query Error", f"Error executing query: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")
    
    def load_entity_data(self):
        try:
            # Clear existing data
            for item in self.entity_tree.get_children():
                self.entity_tree.delete(item)
            
            # Get data from database
            self.cursor.execute("SELECT * FROM Entity ORDER BY ID")
            for row in self.cursor.fetchall():
                self.entity_tree.insert("", tk.END, values=row)
            
            self.status_bar.config(text=f"Loaded {len(self.entity_tree.get_children())} entities")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading entity data: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")
    
    def load_relationship_data(self):
        try:
            # Clear existing data
            for item in self.relationship_tree.get_children():
                self.relationship_tree.delete(item)
            
            # Get data from database with descriptive text values
            self.cursor.execute("""
                SELECT r.ID, r.PROPERTY_ID, 
                       COALESCE(e1.TEXT_VALUE, '[Entity ' || r.PROPERTY_ID || ']') AS PROPERTY_VALUE, 
                       r.RELATED_ID, 
                       COALESCE(e2.TEXT_VALUE, '[Entity ' || r.RELATED_ID || ']') AS RELATED_VALUE
                FROM Relationship r
                LEFT JOIN Entity e1 ON r.PROPERTY_ID = e1.ID
                LEFT JOIN Entity e2 ON r.RELATED_ID = e2.ID
                ORDER BY r.ID
            """)
            
            for row in self.cursor.fetchall():
                self.relationship_tree.insert("", tk.END, values=row)
            
            self.status_bar.config(text=f"Loaded {len(self.relationship_tree.get_children())} relationships")
            
            # Update entity dropdowns
            self.update_entity_dropdowns()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading relationship data: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")
    
    def update_entity_dropdowns(self):
        try:
            # Get all entities with their text values for dropdown display
            self.cursor.execute("""
                SELECT ID, COALESCE(TEXT_VALUE, '[Entity ' || ID || ']') AS DISPLAY_TEXT
                FROM Entity
                ORDER BY ID
            """)
            
            entity_data = self.cursor.fetchall()
            
            # Format entities for dropdown: "ID: Text Value"
            entity_values = [f"{eid}: {text}" for eid, text in entity_data]
            
            # Update dropdowns
            self.property_combo['values'] = entity_values
            self.related_combo['values'] = entity_values
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error updating entity dropdowns: {str(e)}")
    
    def on_entity_select(self, event):
        selected_items = self.entity_tree.selection()
        if not selected_items:
            return
        
        # Get values from selected item
        values = self.entity_tree.item(selected_items[0], 'values')
        
        # Populate form fields
        self.entity_id_var.set(values[0])
        self.entity_integer_var.set(values[1] if values[1] else "")
        self.entity_text_var.set(values[2] if values[2] else "")
        self.entity_boolean_var.set(values[3] if values[3] else "")
        self.entity_blob_var.set("[BLOB data]" if values[4] else "")
        self.entity_real_var.set(values[5] if values[5] else "")
        self.entity_numeric_var.set(values[6] if values[6] else "")
        
        # Enable editing of form
        self.entity_id_entry.config(state="readonly")
    
    def on_relationship_select(self, event):
        selected_items = self.relationship_tree.selection()
        if not selected_items:
            return
        
        # Get values from selected item
        values = self.relationship_tree.item(selected_items[0], 'values')
        
        # Populate form fields
        self.relationship_id_var.set(values[0])
        
        # Set property ID in dropdown
        property_id = values[1]
        for idx, item in enumerate(self.property_combo['values']):
            if item.startswith(f"{property_id}:"):
                self.property_combo.current(idx)
                break
        
        # Set related ID in dropdown (if not NULL)
        related_id = values[3]
        if related_id:
            for idx, item in enumerate(self.related_combo['values']):
                if item.startswith(f"{related_id}:"):
                    self.related_combo.current(idx)
                    break
        else:
            self.related_id_var.set("")
    
    def new_entity(self):
        # Clear form fields
        self.entity_id_var.set("")
        self.entity_integer_var.set("")
        self.entity_text_var.set("")
        self.entity_boolean_var.set("")
        self.entity_blob_var.set("[BLOB data]")
        self.entity_real_var.set("")
        self.entity_numeric_var.set("")
        
        # Set ID field to read-only since it's auto-generated
        self.entity_id_entry.config(state="readonly")
        
        # Focus on the first editable field
        self.entity_text_entry.focus()
    
    def save_entity(self):
        # Get values from form
        entity_id = self.entity_id_var.get()
        integer_value = self.entity_integer_var.get()
        text_value = self.entity_text_var.get()
        boolean_value = self.entity_boolean_var.get()
        real_value = self.entity_real_var.get()
        numeric_value = self.entity_numeric_var.get()
        
        # Validate required fields (in this case, at least one value should be set)
        if not any([integer_value, text_value, boolean_value, real_value, numeric_value]):
            messagebox.showwarning("Validation Error", "Please set at least one value.")
            return
        
        try:
            # Convert empty strings to NULL for database
            if integer_value == "":
                integer_value = None
            if text_value == "":
                text_value = None
            if boolean_value == "":
                boolean_value = None
            if real_value == "":
                real_value = None
            if numeric_value == "":
                numeric_value = None
            
            # Insert or update based on whether we have an ID
            if entity_id:
                # Update existing entity
                self.cursor.execute("""
                    UPDATE Entity 
                    SET INTEGER_VALUE = ?, TEXT_VALUE = ?, BOOLEAN_VALUE = ?,
                        REAL_VALUE = ?, NUMERIC_VALUE = ?
                    WHERE ID = ?
                """, (integer_value, text_value, boolean_value, real_value, numeric_value, entity_id))
                action = "updated"
            else:
                # Insert new entity
                self.cursor.execute("""
                    INSERT INTO Entity (INTEGER_VALUE, TEXT_VALUE, BOOLEAN_VALUE, REAL_VALUE, NUMERIC_VALUE)
                    VALUES (?, ?, ?, ?, ?)
                """, (integer_value, text_value, boolean_value, real_value, numeric_value))
                action = "created"
            
            # Commit changes
            self.conn.commit()
            
            # Reload data
            self.load_entity_data()
            self.load_relationship_data()  # Refresh related data
            
            messagebox.showinfo("Success", f"Entity {action} successfully.")
            self.status_bar.config(text=f"Entity {action} successfully.")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Error saving entity: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")
    
    def delete_entity(self):
        entity_id = self.entity_id_var.get()
        if not entity_id:
            messagebox.showwarning("Selection Error", "Please select an entity to delete.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entity? This will also delete any relationships using this entity."):
            return
        
        try:
            # Check for relationships using this entity
            self.cursor.execute("""
                SELECT COUNT(*) FROM Relationship
                WHERE PROPERTY_ID = ? OR RELATED_ID = ?
            """, (entity_id, entity_id))
            
            relationship_count = self.cursor.fetchone()[0]
            
            if relationship_count > 0:
                if not messagebox.askyesno("Confirm Cascade Delete", f"This entity is used in {relationship_count} relationships. Deleting it will also delete these relationships. Continue?"):
                    return
                
                # Delete relationships first
                self.cursor.execute("""
                    DELETE FROM Relationship
                    WHERE PROPERTY_ID = ? OR RELATED_ID = ?
                """, (entity_id, entity_id))
            
            # Delete entity
            self.cursor.execute("DELETE FROM Entity WHERE ID = ?", (entity_id,))
            
            # Commit changes
            self.conn.commit()
            
            # Reload data
            self.load_entity_data()
            self.load_relationship_data()
            
            # Clear form
            self.new_entity()
            
            messagebox.showinfo("Success", "Entity deleted successfully.")
            self.status_bar.config(text="Entity deleted successfully.")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Error deleting entity: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")
    
    def new_relationship(self):
        # Clear form fields
        self.relationship_id_var.set("")
        self.property_id_var.set("")
        self.related_id_var.set("")
        
        # Set ID field to read-only since it's auto-generated
        self.relationship_id_entry.config(state="readonly")
        
        # Focus on property combo
        self.property_combo.focus()
    
    def save_relationship(self):
        # Get values from form
        relationship_id = self.relationship_id_var.get()
        
        # Extract ID from dropdown text (format: "ID: Text")
        property_id_text = self.property_id_var.get()
        related_id_text = self.related_id_var.get()
        
        if not property_id_text:
            messagebox.showwarning("Validation Error", "Property Entity is required.")
            return
        
        # Extract the ID number from the selected text
        try:
            property_id = int(property_id_text.split(":")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Validation Error", "Invalid Property Entity format.")
            return
        
        # Related ID can be NULL
        related_id = None
        if related_id_text:
            try:
                related_id = int(related_id_text.split(":")[0])
            except (ValueError, IndexError):
                messagebox.showwarning("Validation Error", "Invalid Related Entity format.")
                return
        
        try:
            # Insert or update based on whether we have an ID
            if relationship_id:
                # Update existing relationship
                self.cursor.execute("""
                    UPDATE Relationship 
                    SET PROPERTY_ID = ?, RELATED_ID = ?
                    WHERE ID = ?
                """, (property_id, related_id, relationship_id))
                action = "updated"
            else:
                # Insert new relationship
                self.cursor.execute("""
                    INSERT INTO Relationship (ID, PROPERTY_ID, RELATED_ID)
                    VALUES (?, ?, ?)
                """, (None, property_id, related_id))  # SQLite will auto-generate ID
                action = "created"
            
            # Commit changes
            self.conn.commit()

            # Reload data
            self.load_relationship_data()

            messagebox.showinfo("Success", f"Relationship {action} successfully.")
            self.status_bar.config(text=f"Relationship {action} successfully.")

        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Error saving relationship: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")

    def delete_relationship(self):
        relationship_id = self.relationship_id_var.get()
        if not relationship_id:
            messagebox.showwarning("Selection Error", "Please select a relationship to delete.")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this relationship?"):
            return

        try:
            # Delete relationship
            self.cursor.execute("DELETE FROM Relationship WHERE ID = ?", (relationship_id,))

            # Commit changes
            self.conn.commit()

            # Reload data
            self.load_relationship_data()

            # Clear form
            self.new_relationship()

            messagebox.showinfo("Success", "Relationship deleted successfully.")
            self.status_bar.config(text="Relationship deleted successfully.")

        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Error deleting relationship: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")

    def export_data(self):
        # Ask for export type
        export_type = simpledialog.askstring(
            "Export Data",
            "Export as (csv/excel):",
            initialvalue="csv"
        )

        if not export_type:
            return

        export_type = export_type.lower()

        if export_type not in ['csv', 'excel']:
            messagebox.showwarning("Invalid Type", "Export type must be 'csv' or 'excel'")
            return

        try:
            # Ask for file path
            if export_type == 'csv':
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
            else:  # excel
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
                )

            if not file_path:
                return  # User cancelled

            # Get data from database
            entity_df = pd.read_sql_query("SELECT * FROM Entity", self.conn)
            relationship_df = pd.read_sql_query("""
                SELECT r.ID, r.PROPERTY_ID,
                       COALESCE(e1.TEXT_VALUE, '[Entity ' || r.PROPERTY_ID || ']') AS PROPERTY_VALUE,
                       r.RELATED_ID,
                       COALESCE(e2.TEXT_VALUE, '[Entity ' || r.RELATED_ID || ']') AS RELATED_VALUE
                FROM Relationship r
                LEFT JOIN Entity e1 ON r.PROPERTY_ID = e1.ID
                LEFT JOIN Entity e2 ON r.RELATED_ID = e2.ID
            """, self.conn)

            # Export based on type
            if export_type == 'csv':
                # Export as CSV
                with open(file_path, 'w', newline='') as f:
                    f.write("# ENTITY TABLE\n")
                    entity_df.to_csv(f, index=False)
                    f.write("\n\n# RELATIONSHIP TABLE\n")
                    relationship_df.to_csv(f, index=False)
            else:  # excel
                # Export as Excel
                with pd.ExcelWriter(file_path) as writer:
                    entity_df.to_excel(writer, sheet_name='Entities', index=False)
                    relationship_df.to_excel(writer, sheet_name='Relationships', index=False)

            messagebox.showinfo("Export Successful", f"Data exported to {file_path}")
            self.status_bar.config(text=f"Data exported to {file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")
            self.status_bar.config(text=f"Error: {str(e)}")

    def show_about(self):
        about_text = """
Entity Relationship Database Manager

A GUI application for managing an Entity-Relationship database structure.
This application allows you to:
- Create, read, update, and delete entities
- Create, read, update, and delete relationships between entities
- Run custom SQL queries
- Export data to CSV or Excel

Database Schema:
- Entity: Flexible entity with various value types
- Relationship: Connects entities with property-related relationships
"""
        messagebox.showinfo("About", about_text)

    def __del__(self):
        # Close database connection when object is destroyed
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    root = tk.Tk()
    app = EntityRelationshipGUI(root, "EntityRelationship.sqlite3")
    root.mainloop()


if __name__ == "__main__":
    main()
