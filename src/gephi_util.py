import jaydebeapi
from global_parameters import *
import networkx as nx

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
    id = 0
    for version, date in rows:
        G.add_node(id, viz={'color': {'r': 255, 'g': 0, 'b': 0, 'a': 1.0}}, version=version, date=date, group="main", parent=id)
        if previous is not None:
            G.add_edge(previous, id)
        cursor.execute(f'''SELECT * FROM "{repo_name}" WHERE version = ?''', [version])
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]

        previous = id
        id += 1

        for col_name, value in zip(columns, row):
            # ignore version and date columns
            if col_name in ('VERSION', 'DATE'):
                continue
            if value is not None:
                G.add_node(id, dependency=col_name, dependency_version=value, group="dependency", parent=previous)
                G.add_edge(previous, id)
                id += 1

    nx.write_gexf(G, gephi_path)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    export_db_to_gexf()
