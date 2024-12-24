# Exploring the legal_cases schema from AIGraph4pg

Used pgAdmin 4, right mouse, and "Create Script" to capture
the following content for the AIGraph4pg legal_cases graph.

### Schema 

```
-- SCHEMA: legal_cases

-- DROP SCHEMA IF EXISTS legal_cases ;

CREATE SCHEMA IF NOT EXISTS legal_cases
    AUTHORIZATION chjoakim;
```

### Base Vertex table

```
-- Table: legal_cases._ag_label_vertex

-- DROP TABLE IF EXISTS legal_cases._ag_label_vertex;

CREATE TABLE IF NOT EXISTS legal_cases._ag_label_vertex
(
    id graphid NOT NULL DEFAULT _graphid((_label_id('legal_cases'::name, '_ag_label_vertex'::name))::integer, nextval('legal_cases._ag_label_vertex_id_seq'::regclass)),
    properties agtype NOT NULL DEFAULT agtype_build_map(),
    CONSTRAINT _ag_label_vertex_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS legal_cases._ag_label_vertex
    OWNER to chjoakim;
```

### Base Edge Table 

```
-- Table: legal_cases._ag_label_edge

-- DROP TABLE IF EXISTS legal_cases._ag_label_edge;

CREATE TABLE IF NOT EXISTS legal_cases._ag_label_edge
(
    id graphid NOT NULL DEFAULT _graphid((_label_id('legal_cases'::name, '_ag_label_edge'::name))::integer, nextval('legal_cases._ag_label_edge_id_seq'::regclass)),
    start_id graphid NOT NULL,
    end_id graphid NOT NULL,
    properties agtype NOT NULL DEFAULT agtype_build_map(),
    CONSTRAINT _ag_label_edge_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS legal_cases._ag_label_edge
    OWNER to chjoakim;
```

### Case Table

```
-- Table: legal_cases.Case

-- DROP TABLE IF EXISTS legal_cases."Case";

CREATE TABLE IF NOT EXISTS legal_cases."Case"
(
    -- Inherited from table legal_cases._ag_label_vertex: id graphid NOT NULL DEFAULT _graphid((_label_id('legal_cases'::name, 'Case'::name))::integer, nextval('legal_cases."Case_id_seq"'::regclass)),
    -- Inherited from table legal_cases._ag_label_vertex: properties agtype NOT NULL DEFAULT agtype_build_map()
)
    INHERITS (legal_cases._ag_label_vertex)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS legal_cases."Case"
    OWNER to chjoakim;
```

### cites Table

```
-- Table: legal_cases.cites

-- DROP TABLE IF EXISTS legal_cases.cites;

CREATE TABLE IF NOT EXISTS legal_cases.cites
(
    -- Inherited from table legal_cases._ag_label_edge: id graphid NOT NULL DEFAULT _graphid((_label_id('legal_cases'::name, 'cites'::name))::integer, nextval('legal_cases.cites_id_seq'::regclass)),
    -- Inherited from table legal_cases._ag_label_edge: start_id graphid NOT NULL,
    -- Inherited from table legal_cases._ag_label_edge: end_id graphid NOT NULL,
    -- Inherited from table legal_cases._ag_label_edge: properties agtype NOT NULL DEFAULT agtype_build_map()
)
    INHERITS (legal_cases._ag_label_edge)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS legal_cases.cites
    OWNER to chjoakim;
```

### cited_by Table

```
-- Table: legal_cases.cited_by

-- DROP TABLE IF EXISTS legal_cases.cited_by;

CREATE TABLE IF NOT EXISTS legal_cases.cited_by
(
    -- Inherited from table legal_cases._ag_label_edge: id graphid NOT NULL DEFAULT _graphid((_label_id('legal_cases'::name, 'cited_by'::name))::integer, nextval('legal_cases.cited_by_id_seq'::regclass)),
    -- Inherited from table legal_cases._ag_label_edge: start_id graphid NOT NULL,
    -- Inherited from table legal_cases._ag_label_edge: end_id graphid NOT NULL,
    -- Inherited from table legal_cases._ag_label_edge: properties agtype NOT NULL DEFAULT agtype_build_map()
)
    INHERITS (legal_cases._ag_label_edge)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS legal_cases.cited_by
    OWNER to chjoakim;
```


