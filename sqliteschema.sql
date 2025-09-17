-- Table 1: Taxonomy Hierarchy
CREATE TABLE taxonomy (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    rank TEXT NOT NULL,
    scientific_name TEXT NOT NULL,
    common_name TEXT,
    FOREIGN KEY (parent_id) REFERENCES taxonomy(id)
);

-- Table 2: Taxonomic Attributes
CREATE TABLE attributes (
    id INTEGER PRIMARY KEY,
    taxonomy_id INTEGER NOT NULL,
    attribute_name TEXT NOT NULL,
    text_value TEXT,
    numeric_value REAL,
    boolean_value INTEGER,
    FOREIGN KEY (taxonomy_id) REFERENCES taxonomy(id)
);
