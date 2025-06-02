# Visualizing changes in software systems

## The Project

This is an ongoing student project work focused on analyzing and visualizing software dependencies over time.
The primary goal is to extract dependency information from github projects and represent them in a tabular format.

Our current focus lies on parsing **maven-based** repositories via their `pom.xml` files.
Later on, we also plan to support **gradle-based** projects by analyzing the `.gradle` files.

The tool takes either:
- a single GitHub repository, or
- a list of repositories as input

For each repository, the tool will:
1. Clone it (only the project structure and pom.xml files, to save space)
2. Traverse the commit history
3. Parse all dependency trees over time
4. Store all dependencies to a project in a database
5. Provide a visual table-based representation of how the dependencies evolved over time

## How to run

- Python 3.x
- Git
- Maven
    - Includes the [Apache Maven Dependency Plugin](https://github.com/apache/maven-dependency-plugin/)

### Setup on Linux

#### 1. Maven
```bash
sudo apt update
sudo apt install maven
```
verify installation with
```mvn -v```

#### 2. Python Packages
This project requires the install of the following packages:
```bash
pip install jaydebeapi

pip install networkx

pip install python.dateutil

pip install pytz
```

#### 3. Gephi
Gephi is the graphics viewer for the dependency graph and can be installed under:
https://gephi.org/users/install/

### Setup on Windows
*Windows is currently not supported*

## Current Features

- Partial Git clone of repositories (with automatic detection of 'pom.xml' directories
- extraction of maven dependency trees using the [maven-dependency-plugin](https://github.com/apache/maven-dependency-plugin/)
- output stored in a .txt file for further steps
- Generation of a h2 database of dependencies of every version
- Ability to limit dependency analysation by number of commmit or date range

## Command Line Parameter
| Parameter | Explaination |
|---|---|
| -h --help | Show help |
| -g --git | Link to GitHub repository to analyze |
| -l --limit | Limits the amount of commits analyzed to last X commits |
| --start | Limits analyzed commits to those commited on this date UTC and after. Input date in form "YYYY-MM-DD" |
| --end | Limits analyzed commits to those commited on this date UTC and before. Input date in form "YYYY-MM-DD" |

## Accessing the database
### Option 1: H2 Webviewer
1. Execute the h2 jar file, this opens the webviewer in a browser:
```bash
java -jar h2-2.3.232.jar
```
2. Connect to the database:

- In field `JDBC URL`enter:
``` 
jdbc:h2:PATH_TO_DATABASE_WITHOUT_FILE_EXTENSION
```
- Leave both `User Name` and `Password` blank
