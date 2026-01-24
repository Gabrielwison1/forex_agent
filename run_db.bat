@echo off
echo Starting Premium PostgreSQL Database...
docker run --name forex_db -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -e POSTGRES_DB=forex_agent -p 5432:5432 -d postgres:15-alpine
echo Database started on port 5432.
pause
