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

## Run

Requires Docker (with the Compose plugin). The BASIL image is built from source on first build and takes a few minutes.

Start in background

```sh
docker compose up -d --build
```

Read logs

```sh
docker compose logs -f
```

Stop

```sh
docker compose down
```

Full reset

```sh
docker compose down -v && rm -f basil/state/api-id basil/state/api-id-rdf
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

The grlc versioning operation authenticates to the
GitHub API, so it needs a token. Put it in a `.env` file in this directory and
Compose passes it to grlc.

```sh
echo 'GITHUB_TOKEN=your_token_here' > .env
```

```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-git/arcangelo7/sparql-api-comparison/subdir/grlc/queries/commit/1872cd59b0524ce764060ba72f61d5e7aafe29a4/article-meta?doi=10.1007/s11192-022-04367-w'
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
