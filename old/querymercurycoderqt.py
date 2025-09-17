import sys
import sqlite3
from PySide2.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QLabel
from PySide2.QtGui import QPen, QBrush, QColor
from PySide2.QtCore import Qt, QRectF

# Connect to the SQLite database
connection = sqlite3.connect("EntityRelationship.sqlite3")
connection.execute('PRAGMA foreign_keys = ON')

def get_entities():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Entity")
    return cursor.fetchall()

def get_relationships():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Relationship")
    return cursor.fetchall()

class GraphView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.build_graph()

    def build_graph(self):
        entities = get_entities()
        relationships = get_relationships()

        # Add nodes (entities)
        node_positions = {}
        for i, entity in enumerate(entities):
            node = Node(entity[0], entity[1:])
            node.setPos(i * 100, 100)
            self.scene.addItem(node)
            node_positions[entity[0]] = node.pos()

        # Add edges (relationships)
        for relationship in relationships:
            from_node_pos = node_positions[relationship[1]]
            to_node_pos = node_positions[relationship[2]]
            edge = Edge(from_node_pos, to_node_pos)
            self.scene.addItem(edge)

class Node(QGraphicsEllipseItem):
    def __init__(self, id, data):
        super().__init__(-(0, 0, 80, 80))
        self.id = id
        self.data = data
        self.setPen(QPen(Qt.black))
        self.setBrush(QBrush(QColor(100, 170, 255)))
        self.label = QLabel(f"ID: {id}\nData: {data}")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: rgba(255, 255, 255, 128); border-radius: 4px;")
        self.label.setGeometry(-40, -40, 80, 80)
        self.label.raise_()

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        self.label.move(self.pos().x() - 40, self.pos().y() - 40)

class Edge(QGraphicsLineItem):
    def __init__(self, start_pos, end_pos):
        super().__init__(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
        self.setPen(QPen(Qt.black, 2))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = GraphView()
    view.show()
    sys.exit(app.exec_())
