This project runs `reports-service` using the parent `docker-compose.yml` and an internal Postgres service named `reports-db`.

DB connection string used by the service:

postgresql://postgres:postgres@reports-db:5432/reports
