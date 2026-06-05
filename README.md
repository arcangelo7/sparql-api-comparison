# sparql-api-comparison

A repository for testing server-side REST-API-over-SPARQL generators on the same
task. It stands up minimal, real APIs for six tools, **RAMOSE v2**, **grlc**,
**BASIL**, **R4R**, **CRAFTS**, and **RDFProxy**, and exercises each on the same
OpenCitations lookup, so their functional differences can be observed.

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
OMID**, two datasets with no link between them. All six tools take the same
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

Once the stack is up, call the tools directly. Each tool is exercised on the
same six dimensions: the join, output, pagination, versioning, API description,
and authentication.

## RAMOSE

### The join

```sh
curl 'http://localhost:8081/api/v1/citations/10.1007/s11192-022-04367-w?format=json'
```

### Output

```sh
curl 'http://localhost:8081/api/v1/citations/10.1007/s11192-022-04367-w?format=csv'
```

### Pagination

```sh
curl -i 'http://localhost:8081/api/v1/incoming-citations/10.1007/s11192-022-04367-w?format=json&page=1&page_size=2'
```

### Versioning

The API version is carried in the base path (`/api/v1`).

### API description

```sh
curl 'http://localhost:8081/api/v1/openapi.yaml'
```

### Authentication

Not supported.

## grlc

### The join

grlc reaches both endpoints but with one operation each: it cannot join them.

```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-local/article-meta?doi=10.1007/s11192-022-04367-w'
```

```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-local/citations-index?br=https://w3id.org/oc/meta/br/061202127149'
```

### Output

```sh
curl -H 'Accept: text/csv' \
  'http://localhost:8082/api-local/article-meta?doi=10.1007/s11192-022-04367-w'
```

### Pagination

```sh
curl -i -H 'Accept: application/json' \
  'http://localhost:8082/api-local/citing-list?br=https://w3id.org/oc/meta/br/061202127149&page=1'
```

### Versioning

This needs a GitHub token in a `.env` file.

```sh
echo 'GITHUB_TOKEN=your_token_here' > .env
```

```sh
curl -H 'Accept: application/json' \
  'http://localhost:8082/api-git/arcangelo7/sparql-api-comparison/subdir/grlc/queries/commit/1872cd59b0524ce764060ba72f61d5e7aafe29a4/article-meta?doi=10.1007/s11192-022-04367-w'
```

### API description

```sh
curl 'http://localhost:8082/api-local/swagger'
```

### Authentication

Not supported.

## BASIL

### The join

BASIL binds a single endpoint, so it answers from Meta only.

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id)/api.json?doi=10.1007/s11192-022-04367-w"
```

### Output

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

### Pagination

Not supported.

### Versioning

Not supported.

### API description

```sh
curl "http://localhost:8080/basil/$(cat basil/state/api-id)/api-docs"
```

### Authentication

Writes are protected by HTTP Basic; reads are open.

```sh
curl -c /tmp/basil-cookies -X POST 'http://localhost:8080/basil/auth/login' \
  -H 'Content-type: application/json' \
  --data '{"username":"demo","password":"demo"}'
```

## R4R

### The join

R4R binds a single endpoint for the whole server, so it answers from Meta only.

```sh
curl 'http://localhost:8083/articles?doi=10.1007/s11192-022-04367-w'
```

### Output

The response is a Velocity template, so its format is whatever the template
writes (R4R labels every response `application/json`).

```sh
curl 'http://localhost:8083/articles/061202127149'
```

### Pagination

`size` and `offset` page the result, where `offset` is a page index; there are
no `Link` headers and no total count. The agents below are a nested resource (a
subfolder).

```sh
curl 'http://localhost:8083/articles/061202127149/agents?size=2&offset=1'
```

### Versioning

Not supported.

### API description

Not supported: `/doc` serves only static files placed there by hand.

```sh
curl 'http://localhost:8083/doc/index.html'
```

### Authentication

Global: `API_USERS` guards every operation, not only writes. The `r4r-auth`
service (port 8084) is the same image with `API_USERS=demo:demo`.

```sh
curl -u demo:demo 'http://localhost:8084/articles/061202127149'
```

## CRAFTS

### The join

One resource call merges a resource's properties from both endpoints (title from
Meta, citations from Index). The join is keyed by the resource IRI: the same IRI
must identify the entity in both stores, and the client must supply it. You
cannot make a join starting from the DOI.

```sh
curl -H 'Authorization: Bearer oc-read-token' \
  'http://localhost:8085/apis/oc/query?id=articleByDoi&doi=10.1007/s11192-022-04367-w'
```

```sh
curl -H 'Authorization: Bearer oc-read-token' \
  'http://localhost:8085/apis/oc/resource?id=article&iri=https://w3id.org/oc/meta/br/061202127149'
```

### Output

JSON only; CRAFTS does not negotiate other formats.

### Pagination

Not supported.

### Versioning

Not supported.

### API description

Swagger UI serving an OpenAPI 3.0 spec

```sh
curl 'http://localhost:8085/docs/'
```

### Authentication

Every operation requires credentials

## RDFProxy

### The join

Not supported.

```sh
curl 'http://localhost:8086/articles/10.1007/s11192-022-04367-w'
```

### Output

JSON only, shaped by the Pydantic model and wrapped in a `Page` envelope.

### Pagination

```sh
curl 'http://localhost:8086/articles/10.1007/s11192-022-04367-w/authors?page=2&size=2'
```

### Versioning

Not supported.

### API description

FastAPI serves an OpenAPI 3.1 description.

```sh
curl 'http://localhost:8086/openapi.json'
```

The Swagger UI (and ReDoc) render that description in the browser:
<http://localhost:8086/docs> and <http://localhost:8086/redoc>.

### Authentication

Not supported by RDFProxy itself; FastAPI's security utilities would have to be
added by hand.