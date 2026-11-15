# V2 extension points

V1 does not open a database or create accounts. `Settings.database_path` reserves
`PAYS_DB_PATH` for SQLite. Keep future migrations and database connections here.
Add an auth router and request-scoped user dependency to `create_app` when V2 is built.
A future `fiches_lues` table should associate a user ID with an ISO3 and a reading
timestamp, with a unique `(user_id, iso3)` pair. The home route can then receive
reading status alongside content availability. No schema or auth endpoints exist yet.
