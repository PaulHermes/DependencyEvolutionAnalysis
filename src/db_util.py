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

    # TODO ? repo name is in "" to avoid errors due to special characters
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{repo_name}" (version VARCHAR(100) PRIMARY KEY)')

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
                if line.startswith("\\-") and not line.startswith("   \\-"):

                    # TODO needs a bit more finetuning, was unsure what exaxtly is what now and if test belongs to the version number

                    match = re.match(r"([^:]+):([^:]+):[^:]+:(\S+)", line.strip())
                    if match:
                        dependency = match.group(2)
                        dependency_version = match.group(3)

                        # get all columns from table description and put column names in array
                        cursor.execute(f'SELECT * FROM "{repo_name}" LIMIT 1')
                        existing_columns = set(desc[0] for desc in cursor.description)

                        # Only create column if not existing
                        if dependency not in existing_columns:
                            cursor.execute(f'''ALTER TABLE "{repo_name}" ADD COLUMN "{dependency}" VARCHAR(100)''')
                            existing_columns.add(dependency)    # TODO question here

                        # update version for corresponding dependency column and row
                        cursor.execute(f'''UPDATE "{repo_name}" SET "{dependency}" = ? WHERE version = ?''', [dependency_version, version])

    cursor.execute(f'SELECT * FROM "{repo_name}"')
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    conn.close()
