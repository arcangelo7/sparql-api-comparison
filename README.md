# sparql-api-comparison

A repository for testing server-side REST-API-over-SPARQL generators on the same
task. It stands up minimal, real APIs for three tools, **RAMOSE v2**, **grlc**,
and **BASIL**, and exercises each on the same OpenCitations lookup, so their
functional differences can be observed.

## The test case

One bibliographic resource, looked up by DOI, with data that lives in two
independent OpenCitations endpoints:

| | value |
|---|---|
| DOI | `10.1007/s11192-022-04367-w` |
| OMID | `https://w3id.org/oc/meta/br/061202127149` |
| Title (from OpenCitations Meta) | Identifying And Correcting Invalid Citations Due To DOI Errors In Crossref Data |
| Incoming citations (from OpenCitations Index) | 6 |

Endpoints:

- Meta: `https://sparql.opencitations.net/meta`
- Index: `https://sparql.opencitations.net/index`

The task: **join the title (Meta) with the citation count (Index) on the shared
OMID**, two datasets with no link between them. All three tools take the same
input, the DOI. How far each one gets is the point of the comparison.

## What each tool is asked to do

The rule: query **both** endpoints if the tool supports federation, **one** if
it does not.

| Tool | Port | Endpoints | What the demo shows |
|---|---|---|---|
| **RAMOSE v2** | 8081 | Meta **+** Index | one operation that joins the two result sets on the OMID |
| **grlc** | 8082 | Meta **+** Index | two **independent** operations; grlc reaches both endpoints but cannot join them server-side |
| **BASIL** | 8080 | Meta only | one API bound to a single endpoint; the Index citation count is not reachable in the same API |

## Run

Requires Docker (with the Compose plugin). The BASIL image is built from source on first build and takes a few minutes.

```sh
docker compose up -d --build
docker compose logs -f
docker compose down
docker compose down -v && rm -f basil/state/api-id basil/state/api-id-rdf   # full reset
```

Once the stack is up, call the tools directly.

## RAMOSE

### Join across two endpoints

```sh
curl 'http://localhost:8081/api/v1/citations/10.1007/s11192-022-04367-w?format=json'
```

### Output format

```sh
curl 'http://localhost:8081/api/v1/citations/10.1007/s11192-022-04367-w?format=csv'
```

### Pagination

```sh
curl -i 'http://localhost:8081/api/v1/incoming-citations/10.1007/s11192-022-04367-w?format=json&page=1&page_size=2'
```

### OpenAPI 3.0 description

```sh
curl 'http://localhost:8081/api/v1/openapi.yaml'
```

## grlc

### Two independent operations

grlc reaches both endpoints but with one operation each: it cannot join them

```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-local/article-meta?doi=10.1007/s11192-022-04367-w'
```

```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-local/citations-index?br=https://w3id.org/oc/meta/br/061202127149'
```

### Output format

```sh
curl -H 'Accept: text/csv' \
  'http://localhost:8082/api-local/article-meta?doi=10.1007/s11192-022-04367-w'
```

### Pagination and control over the JSON structure

```sh
curl -i -H 'Accept: application/json' \
  'http://localhost:8082/api-local/citing-list?br=https://w3id.org/oc/meta/br/061202127149&page=1'
```

### OpenAPI 2.0 description

```sh
curl 'http://localhost:8082/api-local/swagger'
```

### Versioning

```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-git/arcangelo7/sparql-api-comparison/subdir/grlc/queries/commit/11c068087bfde3c5a93258d896a6c9c87de0e6ad/article-meta?doi=10.1162/qss_a_00292'
```

## BASIL

BASIL binds a single endpoint, so it answers from Meta only

### Output formats

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id)/api.json?doi=10.1007/s11192-022-04367-w"
```

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id)/api.csv?doi=10.1007/s11192-022-04367-w"
```

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id)/api.xml?doi=10.1007/s11192-022-04367-w"
```

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id-rdf)/api.ttl?doi=10.1007/s11192-022-04367-w"
```

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id-rdf)/api.rdf?doi=10.1007/s11192-022-04367-w"
```

### Authentication

```sh
curl -c /tmp/basil-cookies -X POST 'http://localhost:8080/basil/auth/login' \
  -H 'Content-type: application/json' \
  --data '{"username":"demo","password":"demo"}'
```

### Swagger 1.2

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id)/api-docs"
```
