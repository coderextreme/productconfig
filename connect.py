import sqlite3
import os
import json

connection = sqlite3.connect("ThreeDimAssets.sqlite3")

connection.execute('DROP TABLE "Objects"')

connection.execute('''CREATE TABLE "Objects" (
	"ID"	INTEGER NOT NULL,
	"PROPERTY_NAME"	TEXT NOT NULL,
	"INTEGER_VALUE"	INTEGER,
	"TEXT_VALUE"	TEXT,
	"BOOLEAN_VALUE"	TEXT,
	"BLOB_VALUE"	BLOB,
	"REAL_VALUE"	REAL,
	"NUMERIC_VALUE"	NUMERIC
)''')

cursor = connection.cursor()

def find_files(directory, extension):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                yield os.path.join(root, file)

class IdGen():
    def __init__(self):
        self.id = 0

    def genId(self):
        self.id += 1
        return self.id

ID = IdGen()

def grabMetadata(data, parent):

    if isinstance(data, (tuple, list)):
        for d in data:
            # print(f"{d}\n\n")
            grabMetadata(d, parent)
    elif isinstance(data, str):
        #print(f"{data}\n\n")
        pass
    elif isinstance(data, int):
        #print(f"{data}\n\n")
        pass
    elif isinstance(data, float):
        #print(f"{data}\n\n")
        pass
    elif isinstance(data, object):
        for d in data:
            try:
                if d.startswith("Metadata"):
                    name = data[d]['@name']
                    try:
                        mvalue = data[d]['-value']
                    except KeyError:
                        mvalue = None
                    try:
                        svalue = data[d]['@value']
                    except KeyError:
                        svalue = None
                    setid = ID.genId()
                    result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, TEXT_VALUE)  VALUES (?, ?, ?)", (parent, 'name', name))
                elif d == "Material":
                    setid = ID.genId()
                else:
                    setId = ID.genId()
                    grabMetadata(data[d], setId)
                if d == "Material":
                    try:
                        diffuseColor = data[d]['@diffuseColor']
                        result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'diffuseColor', setid))
                        for (c, component) in enumerate(diffuseColor):
                            if c == 0:
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (setid, 'red', component))
                            elif c == 1:
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (setid, 'green', component))
                            elif c == 2:
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (setid, 'blue', component))
                            elif c == 3:
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (setid, 'alpha', component))
                    except KeyError:
                        diffuseColor = None
                elif d == "MetadataSet":
                    # print(f"{d} {name} {mvalue} {svalue}")
                    result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'metadataset', setid))
                    grabMetadata(data[d], setid)
                elif d == "MetadataInteger":
                    # print(f"{d} {name} {mvalue} {svalue}")
                    if svalue is not None:
                        if isinstance(svalue, list):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                            for (s, sv) in enumerate(svalue):
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (setid, s, sv))
                        else:
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, name, svalue))
                    elif mvalue is not None:
                        result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                        for (m, mv) in enumerate(mvalue):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (setid, m, mv))
                elif d == "MetadataDouble":
                    # print(f"{d} {name} {mvalue} {svalue}")
                    if svalue is not None:
                        if isinstance(svalue, list):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                            for (s, sv) in enumerate(svalue):
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, REAL_VALUE)  VALUES (?, ?, ?)", (setid, s, sv))
                        else:
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, REAL_VALUE)  VALUES (?, ?, ?)", (parent, name, svalue))
                    elif mvalue is not None:
                        result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                        for (m, mv) in enumerate(mvalue):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, REAL_VALUE)  VALUES (?, ?, ?)", (setid, m, mv))
                elif d == "MetadataFloat":
                    # print(f"{d} {name} {mvalue} {svalue}")
                    if svalue is not None:
                        if isinstance(svalue, list):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                            for (s, sv) in enumerate(svalue):
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, REAL_VALUE)  VALUES (?, ?, ?)", (setid, s, sv))
                        else:
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, REAL_VALUE)  VALUES (?, ?, ?)", (parent, name, svalue))
                    elif mvalue is not None:
                        result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                        for (m, mv) in enumerate(mvalue):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, REAL_VALUE)  VALUES (?, ?, ?)", (setid, m, mv))
                elif d == "MetadataString":
                    # print(f"{d} {name} {mvalue} {svalue}")
                    if svalue is not None:
                        if isinstance(svalue, list):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                            for (s, sv) in enumerate(svalue):
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, TEXT_VALUE)  VALUES (?, ?, ?)", (setid, s, sv))
                        else:
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, TEXT_VALUE)  VALUES (?, ?, ?)", (parent, name, svalue))
                    elif mvalue is not None:
                        result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                        for (m, mv) in enumerate(mvalue):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, TEXT_VALUE)  VALUES (?, ?, ?)", (setid, m, mv))
                elif d == "MetadataBoolean":
                    # print(f"{d} {name} {mvalue} {svalue}")
                    if svalue is not None:
                        if isinstance(svalue, list):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                            for (s, sv) in enumerate(svalue):
                                result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, BOOLEAN_VALUE)  VALUES (?, ?, ?)", (setid, s, 'true' if sv else 'false'))
                        else:
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, BOOLEAN_VALUE)  VALUES (?, ?, ?)", (parent, name, 'true' if svalue else 'false'))
                    elif mvalue is not None:
                        result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'array', setid))
                        for (m, mv) in enumerate(mvalue):
                            result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, BOOLEAN_VALUE)  VALUES (?, ?, ?)", (setid, m, 'true' if mv else 'false'))
            except KeyError:
                nextId = ID.genId()
                grabMetadata(data[d], nextId)
    else:
        print(f"{data}\n\n")

for file_path in find_files("C:\\Users\\jcarl\\www.web3d.org\\x3d\\content\\examples\\", ".json"):
    parent = ID.genId()
    result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, TEXT_VALUE)  VALUES (?, ?, ?)", (parent, 'filename', file_path))
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            try:
                metas = data['X3D']['head']['meta']
                for meta in metas:
                    name = meta['@name']
                    content = meta['@content']
                    id = ID.genId()
                    result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, INTEGER_VALUE)  VALUES (?, ?, ?)", (parent, 'meta', id))
                    result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, TEXT_VALUE)  VALUES (?, ?, ?)", (id, 'name', name))
                    result = cursor.execute("INSERT INTO Objects (ID, PROPERTY_NAME, TEXT_VALUE)  VALUES (?, ?, ?)", (id, 'content', content))
            except KeyError:
                pass
            grabMetadata(data, parent)
        except json.decoder.JSONDecodeError:
            pass
connection.commit()

cursor.execute("SELECT * FROM Objects")
for record in cursor.fetchall():
    r = []
    for field in record:
        if field is not None:
            r.append(field)
    print(f"{r}")
connection.close()
