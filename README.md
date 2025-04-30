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

```bash
sudo apt update
sudo apt install maven
```
verify installation with
```mvn -v```

### Setup on Windows
#### 1. Download Maven ####

Visit the [Apache Maven download page](https://maven.apache.org/download.cgi).

Download the latest binary zip archive.

#### 2. Extract the Archive ####

Unzip the downloaded archive to a directory of your choice, such as: ```C:\Program Files\Apache\Maven```

#### 3. New Environment Variable ####

Variable name: ```MAVEN_HOME```

Variable value: ```C:\Program Files\Apache\Maven (adjust if you chose a different directory)```


#### 4. Update the Path Variable ####
Add a new entry to the Path Variable: ```C:\Program Files\Apache\Maven\bin```
#### 5. Verify Installation ####

verify installation with
```mvn -v```

## Current Features

- Partial Git clone of repositories (with automatic detection of 'pom.xml' directories
- extraction of maven dependency trees using the [maven-dependency-plugin](https://github.com/apache/maven-dependency-plugin/)
- output stored in a .txt file for further steps
