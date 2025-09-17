import sqlite3
import os

connection = sqlite3.connect("EntityRelationship.sqlite3")

connection.execute('PRAGMA foreign_keys = ON')
connection.execute('DROP TABLE "Relationship"')
connection.execute('DROP TABLE "Entity"')

connection.execute('''CREATE TABLE "Relationship" (
	"ID"	INTEGER NOT NULL,
	"PROPERTY_ID"	INTEGER NOT NULL,
	"RELATED_ID"	INTEGER,
    FOREIGN KEY ("PROPERTY_ID") REFERENCES "Entity" ("ID"),
    FOREIGN KEY ("RELATED_ID") REFERENCES "Entity" ("ID")
)''')

connection.execute('''CREATE TABLE "Entity" (
	"ID"	INTEGER PRIMARY KEY,
	"INTEGER_VALUE"	INTEGER,
	"TEXT_VALUE"	TEXT,
	"BOOLEAN_VALUE"	TEXT,
	"BLOB_VALUE"	BLOB,
	"REAL_VALUE"	REAL,
	"NUMERIC_VALUE"	NUMERIC
)''')

connection.commit()
connection.close()
