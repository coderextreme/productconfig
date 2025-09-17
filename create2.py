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
            "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
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

def main():
    connection = create_database()
    connection.commit()
    connection.close()
    logger.info("Database creation completed successfully")

if __name__ == "__main__":
    main()
