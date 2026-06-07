# sparql-api-comparison

[![Documentation](https://github.com/arcangelo7/sparql-api-comparison/actions/workflows/docs.yml/badge.svg)](https://arcangelo7.github.io/sparql-api-comparison)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](LICENSE)

Minimal, runnable REST APIs for nine server-side REST-API-over-SPARQL generators, RAMOSE, grlc, BASIL, R4R, CRAFTS, RDFProxy, OBA, Elda, and Walder, each exercised on the same OpenCitations lookup so their functional differences can be observed.

**[Read the comparison](https://arcangelo7.github.io/sparql-api-comparison)**

## Run locally

If you want to run the calls yourself or refresh those outputs, run Docker first:

```sh
docker compose up -d --build
```

With the stack up, execute the notebooks:

```sh
uv run jupyter nbconvert --to notebook --execute --inplace docs/*.ipynb
```

Render them to HTML:

```sh
uv run jupyter-book build docs
```

Stop the stack with `docker compose down`.

## License

ISC. See [LICENSE](LICENSE).
