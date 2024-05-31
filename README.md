<img src="images/teemo.png" width="150"/>

# Teemo-Lab

This is a repository for the project Teemo-Lab.

The project is to build a platform for the analysis of the data from the game [League of Legends](https://na.leagueoflegends.com/en-us/).

## Project Organization

This project is organized into several directories and files for efficient workflow management:

    ├── LICENSE
    │
    ├── README.md          <- The top-level README for developers using this project
    │
    ├── experiments        <- The directory for experiments by the team members
    │
    ├── images             <- The directory for images
    │
    ├── teemo-lab          <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   └── ...
    │
    ├── tests              <- The directory for tests
    │
    └── ...

## Setup the Environment

To work with [Teemo-Lab](https://github.com/pbj8723/Teemo-Lab), you need to setup the python environment using [conda](https://docs.conda.io/en/latest/). Probably, the simplest way is to use [Docker](https://www.docker.com/). Or you can set it up manually.

To install the dependencies, run the following command:

```bash
conda env create -f environment.yml
```

To activate the environment, run the following command:

```bash
conda activate teemo-lab
```


