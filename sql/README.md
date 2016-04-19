Contains database initialization scripts.
All of these files are PostgreSQL only -- some Postgres-specific features are used and no other databases are or will be supported.

Stuff in here:

- `00-schema.sql`: Creates the necessary data types and tables.
- `01-materialize-rules.sql`: Creates views used for quick rules querying and `offlinedb` compilation.
- `02-triggers.sql`: Creates triggers to NOTIFY when something changes. `offlinedb` LISTENs for these to rebuild on demand.
- `99-testdata.sql`: Adds some test data. Don't apply this in production ;-)

Apply in the obvious order (or using `../Makefile` or `../deadcli newdb`)
