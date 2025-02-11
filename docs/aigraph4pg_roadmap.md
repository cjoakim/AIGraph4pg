# AIGraph4pg - Project Roadmap

## Initial Release: Feb/March 2025

  - az CLI deployment process for Azure PostgreSQL
  - Curated and vectorized legal_cases relational and graph datasets
  - Relational functionality with the legal_cases table
  - JSONB functionality with the legal_cases table
  - Simple agefreighter example; python/agefreighter_example.py
  - AGE graph loading with the agefreighter library
  - AGE graph queries with D3.js visualization of query results
  - DiskANN vector search
  - Initial generative AI for openCypher query generation
  - Jypyter notebook for AGE and agefreighter
  - Documentation:
    - Architecture diagram
    - Integrated docs in the web app via clicking the library icon
    - Commplete markdown docs in the \docs directory, including quick_start
    - Complete html documentation with mkdocs
  - Docker support:
    - Dockerfile
    - Docker compose script
    - image in Docker Hub: cjoakim/aigraph4pg
  - Deploy to an AzureSamples repo

## April/May 2025

  - Add the **azure_ai** extension for embeddings generation
    - https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/generative-ai-azure-overview
  - Integrate **Semantic Ranking** with DiskANN vector search
    - https://techcommunity.microsoft.com/blog/adforpostgresql/introducing-the-semantic-ranking-solution-for-azure-database-for-postgresql/4298781

## Backlog

  - In-database vectorization with SLM
  - RBAC
  - Enhanced IDE integration
  - Fabric Mirroring integration
  - Integrate ongoing Azure Database for PostgreSQL innovation
