import sqlite3
import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_database(db_path="EntityRelationship.sqlite3"):
    """Create and set up the SQLite database with improved schema."""
    connection = sqlite3.connect(db_path)
    connection.execute('PRAGMA foreign_keys = ON')
    
    # Drop tables if they exist
    connection.executescript('''
        DROP TABLE IF EXISTS "Relationship";
        DROP TABLE IF EXISTS "Entity";
        DROP TABLE IF EXISTS "EntityType";
    ''')
    
    # Create tables with improved schema
    connection.executescript('''
        CREATE TABLE "EntityType" (
            "ID" INTEGER PRIMARY KEY,
            "NAME" TEXT NOT NULL UNIQUE
        );
        
        CREATE TABLE "Entity" (
            "ID" INTEGER PRIMARY KEY,
            "TYPE_ID" INTEGER NOT NULL,
            "INTEGER_VALUE" INTEGER,
            "TEXT_VALUE" TEXT,
            "BOOLEAN_VALUE" INTEGER,
            "BLOB_VALUE" BLOB,
            "REAL_VALUE" REAL,
            "NUMERIC_VALUE" NUMERIC,
            "SOURCE_FILE" TEXT,
            FOREIGN KEY ("TYPE_ID") REFERENCES "EntityType" ("ID")
        );
        
        CREATE TABLE "Relationship" (
            "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
            "SOURCE_ID" INTEGER NOT NULL,
            "PROPERTY_ID" INTEGER NOT NULL,
            "TARGET_ID" INTEGER,
            "RELATIONSHIP_TYPE" TEXT NOT NULL,
            FOREIGN KEY ("SOURCE_ID") REFERENCES "Entity" ("ID"),
            FOREIGN KEY ("PROPERTY_ID") REFERENCES "Entity" ("ID"),
            FOREIGN KEY ("TARGET_ID") REFERENCES "Entity" ("ID")
        );
        
        -- Indexes for better performance
        CREATE INDEX idx_entity_type ON Entity(TYPE_ID);
        CREATE INDEX idx_relationship_source ON Relationship(SOURCE_ID);
        CREATE INDEX idx_relationship_property ON Relationship(PROPERTY_ID);
        CREATE INDEX idx_relationship_target ON Relationship(TARGET_ID);
    ''')
    
    # Pre-populate entity types
    entity_types = [
        (1, "INTEGER"),
        (2, "TEXT"),
        (3, "BOOLEAN"),
        (4, "BLOB"),
        (5, "REAL"),
        (6, "NUMERIC"),
        (7, "OBJECT"),
        (8, "ARRAY"),
        (9, "NULL")
    ]
    
    connection.executemany("INSERT INTO EntityType (ID, NAME) VALUES (?, ?)", entity_types)
    connection.commit()
    
    return connection

class EntityManager:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.next_id = self._get_max_id() + 1
    
    def _get_max_id(self):
        """Get the maximum ID from the Entity table."""
        self.cursor.execute("SELECT COALESCE(MAX(ID), 0) FROM Entity")
        return self.cursor.fetchone()[0]
    
    def get_entity_type_id(self, obj):
        """Map Python types to entity type IDs."""
        if obj is None:
            return 9  # NULL
        
        type_mapping = {
            int: 1,      # INTEGER
            str: 2,      # TEXT
            bool: 3,     # BOOLEAN
            bytes: 4,    # BLOB
            float: 5,    # REAL
            dict: 7,     # OBJECT
            list: 8      # ARRAY
        }
        
        return type_mapping.get(type(obj), 2)  # Default to TEXT for unknown types
    
    def generate_id(self):
        """Generate a new unique ID."""
        current_id = self.next_id
        self.next_id += 1
        return current_id
    
    def find_entity(self, entity_type_id, value):
        """Find an entity by type and value."""
        column_map = {
            1: "INTEGER_VALUE",
            2: "TEXT_VALUE",
            3: "BOOLEAN_VALUE",
            4: "BLOB_VALUE",
            5: "REAL_VALUE",
            6: "NUMERIC_VALUE"
        }
        
        if entity_type_id not in column_map:
            return None
            
        column = column_map[entity_type_id]
        
        # Convert boolean to integer for storage
        if entity_type_id == 3:  # BOOLEAN
            value = 1 if value else 0
            
        self.cursor.execute(
            f"SELECT ID FROM Entity WHERE TYPE_ID = ? AND {column} = ?",
            (entity_type_id, value)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def create_entity(self, entity_type_id, value=None, source_file=None):
        """Create a new entity with the given type and value."""
        entity_id = self.generate_id()
        
        column_map = {
            1: "INTEGER_VALUE",
            2: "TEXT_VALUE",
            3: "BOOLEAN_VALUE",
            4: "BLOB_VALUE",
            5: "REAL_VALUE",
            6: "NUMERIC_VALUE"
        }
        
        # For complex types (objects and arrays), just store the type
        if entity_type_id >= 7:
            self.cursor.execute(
                "INSERT INTO Entity (ID, TYPE_ID, SOURCE_FILE) VALUES (?, ?, ?)",
                (entity_id, entity_type_id, source_file)
            )
            return entity_id
        
        # For primitive types, store the value
        if entity_type_id in column_map:
            column = column_map[entity_type_id]
            
            # Convert boolean to integer for storage
            if entity_type_id == 3:  # BOOLEAN
                value = 1 if value else 0
                
            query = f"INSERT INTO Entity (ID, TYPE_ID, {column}, SOURCE_FILE) VALUES (?, ?, ?, ?)"
            self.cursor.execute(query, (entity_id, entity_type_id, value, source_file))
            return entity_id
            
        return None
    
    def create_relationship(self, source_id, property_id, target_id, relationship_type="HAS_PROPERTY"):
        """Create a relationship between entities."""
        try:
            self.cursor.execute(
                "INSERT INTO Relationship (SOURCE_ID, PROPERTY_ID, TARGET_ID, RELATIONSHIP_TYPE) VALUES (?, ?, ?, ?)",
                (source_id, property_id, target_id, relationship_type)
            )
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error creating relationship: {e}")
            return None
            
    def get_or_create_entity(self, value, source_file=None):
        """Get an existing entity or create a new one if it doesn't exist."""
        entity_type_id = self.get_entity_type_id(value)
        
        # For primitive types, check if the entity already exists
        if entity_type_id <= 6:
            entity_id = self.find_entity(entity_type_id, value)
            if entity_id:
                return entity_id
                
        # Create a new entity if it doesn't exist
        return self.create_entity(entity_type_id, value, source_file)
    
    def process_object(self, obj, parent_id, source_file=None, array_index=None):
        """Process an object and its properties recursively."""
        if obj is None:
            return
            
        # Handle different types
        if isinstance(obj, (int, str, float, bool)):
            # Create property entity if this is an array element
            if array_index is None:
                #prop_entity_id = self.get_or_create_entity("value", source_file)
                #value_entity_id = self.get_or_create_entity(obj, source_file)
                #self.create_relationship(parent_id, prop_entity_id, value_entity_id, "HAS_VALUE")
                pass
            else:
                prop_entity_id = self.get_or_create_entity(array_index, source_file)
                value_entity_id = self.get_or_create_entity(obj, source_file)
                self.create_relationship(parent_id, prop_entity_id, value_entity_id, "ARRAY_ELEMENT")
            return
            
        elif isinstance(obj, dict):
            for prop_name, prop_value in obj.items():
                prop_entity_id = self.get_or_create_entity(prop_name, source_file)
                value_entity_id = self.get_or_create_entity(prop_value, source_file)
                self.process_object(prop_value, value_entity_id, source_file)
                self.create_relationship(parent_id, prop_entity_id, value_entity_id, "HAS_VALUE")
                
        elif isinstance(obj, list):
            for index, item in enumerate(obj):
                index_entity_id = self.get_or_create_entity(index, source_file)
                item_entity_id = self.get_or_create_entity(item, source_file)
                self.process_object(item, item_entity_id, source_file, index)
                self.create_relationship(parent_id, index_entity_id, item_entity_id, "ARRAY_ELEMENT")

def find_files(directory, file_pattern):
    """Find files matching the pattern in the given directory."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file_pattern in file:
                yield os.path.join(root, file)

def main():
    # Set the file pattern to search for
    file_patterns = ["cgeball.json"]  # Example: multiple patterns. Can be just one.

    # Directory to search
    search_dir = os.path.expanduser("~/X3DJSONLD/src/main/personal/")

    # Create the database
    connection = create_database()

    # Create entity manager
    entity_manager = EntityManager(connection)

    # Process each matching file for each pattern
    for file_pattern in file_patterns:
        for file_path in find_files(search_dir, file_pattern):
            logger.info(f"Processing file: {file_path} with pattern {file_pattern}")

            # Create a root entity for the file
            root_entity_id = entity_manager.create_entity(7, source_file=file_path)  # 7 = OBJECT

            # Create filename entity and relationship
            filename_prop_id = entity_manager.get_or_create_entity("filename", file_path)
            filename_value_id = entity_manager.get_or_create_entity(file_path, file_path)
            entity_manager.create_relationship(root_entity_id, filename_prop_id, filename_value_id)

            # Read and process the JSON file
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    entity_manager.process_object(data, root_entity_id, file_path)
            except json.JSONDecodeError:
                logger.error(f"JSON decoding error in file: {file_path}")
            except IOError as e:
                logger.error(f"IO error processing file {file_path}: {e}")

    # Commit the changes and close the connection
    connection.commit()
    connection.close()

    logger.info("Database creation completed successfully")

if __name__ == "__main__":
    main()
