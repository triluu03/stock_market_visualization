# Stock Market Visualization in Dash

## Description

This is an application used to visualize the NASDAQ stock market using Dash (and Plotly).

This project is done as part of the course DATA15003 - Interactive Data Visualization at the University of Helsinki.

## Development

This project uses `uv` as its package management tool. You can install `uv` here: <https://docs.astral.sh/uv>. After having installed `uv`, here are some of the most common `uv` command lines:

- `uv add {package_name}`: add a new Python package/library.
- `uv run {some_script}.py`: run a Python script using the packages added in the project.
- `uv sync`: sync and create/update the virtual environment that rests in `.venv/` in the root folder of this project.

## Run the Application Locally

- Place the client's data into the `data/` folder in the root of the project. The `data/` folder should have a structure as following:

```
data/
├── GeneAnnotation_AnnotationHub.tsv
├── ReadMe.txt
├── Run1
│   ├── Run1_countsPerMillion.tsv
│   └── Run1_sampleAnnot.tsv
├── Run2
│   ├── Run2_countsPerMillion.tsv
│   └── Run2_sampleAnnot.tsv
└── SalmoSalar_geneID_combination2.tsv
```

- Install `uv` to your environment: `pip install uv`
- Sync the virtual environment: `uv sync`
- Run the application: `uv run src/app.py`
- The application should be available in: `http://localhost:8050/`
