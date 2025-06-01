import jaydebeapi
from global_parameters import *
import re
from datetime import datetime

def create_db():
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

    # only create table if not existing
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS "{repo_name}" (
            version VARCHAR(100) PRIMARY KEY,
            date DATE
        )
    ''')

    # create row for every .txt
    history_dir = os.path.join(os.path.dirname(__file__), 'dependency_history')
    for filename in os.listdir(history_dir):

        file_path = os.path.join(history_dir, filename)
        
        with open(file_path, 'r') as file:

            first_line = file.readline().strip()
            dt = datetime.strptime(first_line, "%Y-%m-%d %H:%M:%S %z")
            date = dt.strftime("%Y-%m-%d")

            second_line = file.readline().strip()

            # takes version from first line in txt
            match = re.match(r"[^:]+:[^:]+:[^:]+:([^:]+)", second_line)
            if match:
                version = match.group(1)
            else:
                version = filename[:-4]
                print(f"[INFO] Couldn't extract version number from pom, taking commit hash instead: {version}")
            cursor.execute(f'MERGE INTO "{repo_name}" (version) KEY (version) VALUES (?)', [version])

            cursor.execute(f'SELECT date FROM "{repo_name}" WHERE version = ?', [version])
            existing_date = cursor.fetchone()

            if existing_date and existing_date[0]:
                # take version release date representing for version
                if date < existing_date[0]:
                    cursor.execute(f'UPDATE "{repo_name}" SET date = ? WHERE version = ?', [date, version])
            else:
                cursor.execute(f'MERGE INTO "{repo_name}" (version, date) KEY (version) VALUES (?, ?)', [version, date])
        
            for line in file:
                line = line.rstrip()
                
                # tracking only main dependencies
                if '\\-' in line:
                    line = line[line.index('\\-') + 2:].strip()

                    match = re.match(r"([^:]+):[^:]+:[^:]+:([^:]+)", line.strip())
                    if match:
                        dependency = match.group(1)
                        dependency_version = match.group(2)

                        # get all columns from table description and put column names in array
                        cursor.execute(f'SELECT * FROM "{repo_name}" LIMIT 1')
                        existing_columns = set(desc[0] for desc in cursor.description)

                        # only create column if not existing
                        if dependency not in existing_columns:
                            cursor.execute(f'''ALTER TABLE "{repo_name}" ADD COLUMN "{dependency}" VARCHAR(100)''')
                            existing_columns.add(dependency)

                        # check if there's already a value for that dependency in that version
                        cursor.execute(f'''SELECT "{dependency}" FROM "{repo_name}" WHERE version = ?''', [version])
                        existing = cursor.fetchone()[0]

                        if existing:
                            # append different versions with ;
                            versions = set(existing.split(';'))
                            versions.add(dependency_version)
                            new_value = ';'.join(sorted(versions))
                        else:
                            new_value = dependency_version

                        # insert into table
                        cursor.execute(f'''UPDATE "{repo_name}" SET "{dependency}" = ? WHERE version = ?''', [new_value, version])


    cursor.execute(f'SELECT * FROM "{repo_name}"')
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    conn.close()