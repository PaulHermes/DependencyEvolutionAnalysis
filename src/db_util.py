import jaydebeapi
from global_parameters import *
from urllib.parse import urlparse
import re

def create_db():
    # get repo name from url
    parsed_url = urlparse(repo_url)
    repo_name = os.path.basename(parsed_url.path)
    repo_name = repo_name.replace(".git", "")

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

    cursor.execute(f'DROP TABLE IF EXISTS "{repo_name}"')
    cursor.execute(f'CREATE TABLE "{repo_name}" (version VARCHAR(100) PRIMARY KEY)')

    # create row for every .txt
    history_dir = os.path.join(os.path.dirname(__file__), 'dependency_history')
    for filename in os.listdir(history_dir):
        # either put version in filename or in txt (at the moment saving the commit hash for the version entry)
        version = filename[:-4]
        cursor.execute(f'MERGE INTO "{repo_name}" (version) KEY (version) VALUES (?)', [version])

        file_path = os.path.join(history_dir, filename)
        
        with open(file_path, 'r') as file:
            for line in file:
                line = line.rstrip()
                
                # tracking only main dependencies
                if '\\-' in line:
                    line = line[line.index('\\-') + 2:].strip()

                    # TODO needs a bit more finetuning, was unsure what exactly is what now and if test belongs to the version number

                    match = re.match(r"([^:]+):[^:]+:[^:]+:([^:]+)", line.strip())
                    if match:
                        dependency = match.group(1)
                        dependency_version = match.group(2)
                        print("Dependency:", dependency)
                        print("Version:", dependency_version)

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
