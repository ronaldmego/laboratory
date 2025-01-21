from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import declarative_base
import pydot

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'
    IDCliente = Column(Integer, primary_key=True)
    Nombre = Column(String)
    Apellido = Column(String)
    Email = Column(String)
    FechaRegistro = Column(Date)

class Producto(Base):
    __tablename__ = 'productos'
    IDProducto = Column(Integer, primary_key=True)
    NombreProducto = Column(String)
    TipoProducto = Column(Integer, ForeignKey('tipo_producto.IDTipoProducto'))
    FechaCreacion = Column(Date)

class TipoProducto(Base):
    __tablename__ = 'tipo_producto'
    IDTipoProducto = Column(Integer, primary_key=True)
    Descripcion = Column(String)

class Transaccion(Base):
    __tablename__ = 'transacciones'
    IDTransaccion = Column(Integer, primary_key=True)
    FechaTransaccion = Column(Date)
    Monto = Column(DECIMAL)
    IDProducto = Column(Integer, ForeignKey('productos.IDProducto'))
    IDCliente = Column(Integer, ForeignKey('clientes.IDCliente'))

# Create a new SQLite database (or connect to an existing one)
engine = create_engine('sqlite:///fintech.db')
Base.metadata.create_all(engine)

# Create a Graphviz DOT file
metadata = MetaData()
metadata.reflect(bind=engine)
dot = pydot.Dot(graph_type='digraph')

for table in metadata.sorted_tables:
    dot.add_node(pydot.Node(table.name))
    for column in table.columns:
        dot.add_node(pydot.Node(f"{table.name}.{column.name}"))
        dot.add_edge(pydot.Edge(table.name, f"{table.name}.{column.name}"))
    for fk in table.foreign_keys:
        dot.add_edge(pydot.Edge(f"{fk.parent.table.name}.{fk.parent.name}", f"{fk.column.table.name}.{fk.column.name}"))

# Save the Graphviz DOT file and generate the ER diagram
dot.write('fintech_er_diagram.dot')
(graph,) = pydot.graph_from_dot_file('fintech_er_diagram.dot')
graph.write_png('fintech_er_diagram.png')
