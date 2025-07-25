import jaydebeapi
from global_parameters import *
import networkx as nx
import math

def export_db_to_gexf():
     # jdbc url for h2 db
    url = f"jdbc:h2:file:{db_path}"

    # connect to db
    conn = jaydebeapi.connect(
        "org.h2.Driver",
        url,
        ["", ""],
        h2_jar_path
    )
    cursor = conn.cursor()

    G = nx.Graph()

    # Creates nodes for every version and dependency the version has
    # TODO rename main nodes (maybe check color?)
    cursor.execute(f'SELECT version, date FROM "{repo_name}" ORDER BY date DESC')
    rows = cursor.fetchall()
    previous = None
    spacing = 800
    x_position = 0
    y_position = 0
    id = 0
    for version, date in rows:
        G.add_node(id,
                   label=f"{version}",
                   viz={
                       'color': {'r': 255, 'g': 0, 'b': 0, 'a': 1.0},
                       'position': {'x': x_position, 'y': y_position, 'z': 0}
                       },
                   version=version,
                   date=date,
                   group="main",
                   parent=id)
        if previous is not None:
            G.add_edge(previous, id)
        cursor.execute(f'''SELECT * FROM "{repo_name}" WHERE version = ?''', [version])
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]

        previous = id
        id += 1


        radius = 200
        num_dependencies = len([v for v in row if v is not None]) - 2
        angle_step = 2 * math.pi / max(num_dependencies, 1)

        dep_index = 0

        for col_name, value in zip(columns, row):
            if col_name in ('VERSION', 'DATE'):
                continue
            if value is not None:
                angle = (dep_index * angle_step) + math.pi /2
                x_offset = radius * math.cos(angle)
                y_offset = radius * math.sin(angle)
                
                parent_pos = G.nodes[previous].get('viz', {}).get('position', {'x': 0, 'y': 0})
                x = parent_pos['x'] + x_offset
                y = parent_pos['y'] + y_offset

                G.add_node(
                    id,
                    label=f"{col_name} {value}",
                    dependency=col_name,
                    dependency_version=value,
                    group="dependency",
                    parent=previous,
                    viz={'position': {'x': x, 'y': y, 'z': 0}}
                )
                G.add_edge(previous, id)
                id += 1
                dep_index += 1


        x_position += spacing

    nx.write_gexf(G, gephi_path)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    export_db_to_gexf()
