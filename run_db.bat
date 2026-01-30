@echo off
echo Starting Premium PostgreSQL Database...
docker run --name forex_db -e POSTGRES_USER=forex_admin -e POSTGRES_PASSWORD=forex_secure_2024 -e POSTGRES_DB=forex_agent -p 5433:5432 -d postgres:15-alpine
echo Database started on port 5433 (mapped from container port 5432).
pause
