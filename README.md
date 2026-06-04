# sparql-api-comparison

A repository for testing server-side REST-API-over-SPARQL generators on the same
task. It stands up minimal, real APIs for three tools — **RAMOSE v2**, **grlc**,
and **BASIL** — and exercises each on the same OpenCitations lookup, so their
functional differences can be observed.

## The test case

One bibliographic resource, looked up by DOI, with data that lives in two
independent OpenCitations endpoints:

| | value |
|---|---|
| DOI | `10.1162/qss_a_00292` |
| OMID | `https://w3id.org/oc/meta/br/062104388184` |
| Title (from OpenCitations Meta) | OpenCitations Meta |
| Incoming citations (from OpenCitations Index) | 4 |

Endpoints:

- Meta: `https://sparql.opencitations.net/meta`
- Index: `https://sparql.opencitations.net/index`

The task: **join the title (Meta) with the citation count (Index) on the shared
OMID**, two datasets with no link between them. How far each tool gets is the
point of the comparison.

## What each tool is asked to do

The rule: query **both** endpoints if the tool supports federation, **one** if
it does not.

| Tool | Port | Endpoints | What the demo shows |
|---|---|---|---|
| **RAMOSE v2** | 8081 | Meta **+** Index | one operation that joins the two result sets on the OMID |
| **grlc** | 8082 | Meta **+** Index | two **independent** operations; grlc reaches both endpoints but cannot join them server-side |
| **BASIL** | 8080 | Meta only | one API bound to a single endpoint; the Index citation count is not reachable in the same API |

## Run

Requires Docker (with the Compose plugin). The BASIL image is built from source
(Java 8 + Maven) on first build and takes a few minutes.

```sh
docker compose up -d --build
docker compose logs -f
docker compose down
docker compose down -v && rm -f basil/state/api-id   # full reset
```

Once the stack is up, try the tools by calling their APIs directly.

### Calling the APIs directly

#### RAMOSE

```sh
curl 'http://localhost:8081/api/v1/citations/10.1162/qss_a_00292?format=json'
```

#### grlc
```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-local/article-meta?doi=10.1162/qss_a_00292'
```

```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-local/citations-index?br=https://w3id.org/oc/meta/br/062104388184'
```

#### BASIL

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id)/api.json?omid=https://w3id.org/oc/meta/br/062104388184"
```