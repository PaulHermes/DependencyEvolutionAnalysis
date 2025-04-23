import subprocess
import os
from global_parameters import *
from mvn_util import *

def run_command(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def partial_clone(repo_url, clone_dir):
    """Sparsely clones metadata of a git repository
        --> only first level, no folders
    
    @param repo_url(str): URL of git repository
    @param clone_dir(str): folder to clone to
    """
    clone_cmd = [
        "git", "clone", "--filter=blob:none", "--sparse",
        repo_url, clone_dir
    ]
    run_command(clone_cmd)

def get_pom_directories(clone_dir):
    ls_output = run_command(["git", "ls-tree", "-r", "HEAD", "--name-only"], cwd=clone_dir) # list all files in the current Git repository
    pom_dirs = set()
    for line in ls_output.splitlines():
        if line.endswith("pom.xml"):
            directory = os.path.dirname(line)
            if directory:
                pom_dirs.add(directory)
            else:
                pom_dirs.add(".")
    return list(pom_dirs)

def sparse_checkout_set(clone_dir, paths):
    run_command(["git", "sparse-checkout", "init"], cwd=clone_dir)
    cmd = ["git", "sparse-checkout", "set"] + paths
    run_command(cmd, cwd=clone_dir)

# Folgendes nur zum Testen von den spezifischen Funktionen hier drin
# Will, dass spaeter hier einfach die git funktionen sind und im main script einfach mit den Funktionen hier gepullt wird 
# und dann mit "mvn dependency:tree" subprocess call die text datei und dann DB eintraege gemacht werden. Allerdings not sure wie die commit history danach genutzt wird
if __name__ == "__main__":
    # Change the current working directory to the directory of the Python script
    os.chdir(script_dir)
    
    # Idee hinter partial clone und sparse checkout ist es, dass wir vorerst durch den blob filter nur Ordnerstruktur herunterladen und KEINE dateiinhalte bis diese benoetigt werden
    # sparse_checkout_set ist dann eben fuer das holen der benoetigten pom.xml dateien
    # Zum Verifizieren "git ls-tree -r HEAD". alles andere sorgt dann dafuer, dass die datei benoetigt wird und gefetcht wuerde
    partial_clone(repo_url, clone_dir)
    pom_paths = get_pom_directories(clone_dir)
    sparse_checkout_set(clone_dir, pom_paths)
    
    output_pom_tree(mvn_path, output_file)
