# electric_skate

> Customer service chatbot for an electric skate company powered by RAG

## Project requirements

### Astral/uv

- Install [uv](https://github.com/astral-sh/uv) to manage your Python version, virtual environments, dependencies and
tooling configs: see [installation docs](https://github.com/astral-sh/uv?tab=readme-ov-file#installation).


### Docker Engine

Install [Docker Engine](https://docs.docker.com/engine/install/) to build and run the API's Docker image locally.

## Installation

### Python virtual environment and dependencies

Run the following command:

```bash
uv sync
```

or else:

```bash
make install
```


### Install git hooks (running before commit and push commands)

```bash
uv run pre-commit install
```


### Pull data from DVC remote

- Make sure you have access to the DVC remote bucket (see bucket URL in `.dvc/config` file). If not, ask an administrator to give you access.
- Pull the data:

  ```bash
  uv run dvc pull
  ```


## Testing

To run unit tests, run `pytest` with:

```bash
uv run pytest tests --cov src
```

or

```bash
make test
```

## Formatting and static analysis

### Code formatting with `ruff`

To check code formatting, run `ruff format` with:

```bash
uv run ruff format --check .
```

or

```bash
make format-check
```

You can also [integrate it to your IDE](https://docs.astral.sh/ruff/integrations/) to reformat
your code each time you save a file.

### Static analysis with `ruff`

To run static analysis, run `ruff` with:

```bash
uv run ruff check src tests
```

or

```bash
make lint-check
```

To run static analysis and to apply auto-fixes, run `ruff` with:

```bash
make lint-fix
```

### Type checking with `mypy`

To type check your code, run `mypy` with:

```bash
uv run mypy src --explicit-package-bases --namespace-packages
```

or

```bash
make type-check
```


## API

The project includes an API built with [FastAPI](https://fastapi.tiangolo.com/). Its code can be found at `src/api`.

The API is containerized using a [Docker](https://docs.docker.com/get-started/) image, built from the `Dockerfile` and `docker-compose.yml` at the root.

To build and start the API, use the following Makefile command:

```bash
make start-api
```

You can test the `hello_world` route by [importing the Postman collection](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-postman-data) at `postman`.

For more details on the API routes, check the automatically generated [swagger](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-postman-data) at the `/docs` url.

## Streamlit

The project includes a Streamlit app.
See its documentation in the [specific README](src/streamlit_app/README.md).
Ceci est un projet de chatbot customer service pour des skates électriques avec du RAG
