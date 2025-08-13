
# Sales DDD Template (ASP.NET Core Web API)

## Features
- DDD layering: Domain, Application, Infrastructure (EF Core & Mongo), WebApi
- EF Core provider switch: PostgreSQL / MySQL / SQLite
- MongoDB (query/read repository)
- Manual validation & manual mapping to **record struct DTO**
- Global error handling with RFC 7807 (ProblemDetails-style)
- Minimal API endpoints with Swagger

## Quick Start
```bash
# create solution and add projects
cd src
# (Alternatively use the provided csproj and then run the following)
cd ..
dotnet new sln -n Sales
 dotnet sln add src/Sales.Domain/Sales.Domain.csproj
 dotnet sln add src/Sales.Application/Sales.Application.csproj
 dotnet sln add src/Sales.Infrastructure.EFCore/Sales.Infrastructure.EFCore.csproj
 dotnet sln add src/Sales.Infrastructure.Mongo/Sales.Infrastructure.Mongo.csproj
 dotnet sln add src/Sales.WebApi/Sales.WebApi.csproj
 dotnet sln add tests/Sales.Domain.Tests/Sales.Domain.Tests.csproj

# restore & run Web API
cd src/Sales.WebApi
 dotnet restore
 dotnet run
```

## Configure Database Provider
Edit `src/Sales.WebApi/appsettings.json`:
```json
{
  "Database": { "Provider": "postgres" },
  "ConnectionStrings": {
    "Postgres": "Host=localhost;Port=5432;Database=SalesDb;Username=postgres;Password=postgres",
    "MySql": "Server=localhost;Port=3306;Database=SalesDb;User=root;Password=Password123;",
    "Sqlite": "Data Source=sales.db",
    "Mongo": "mongodb://localhost:27017"
  },
  "Mongo": { "Database": "sales" }
}
```
Allowed values: `postgres`, `mysql`, `sqlite`.

## Validate DTO List
Validation occurs in `PlaceOrderValidator` using `ValidateList` helper which emits indexed paths like `Lines[2].Price`.

## EF Core Projection to DTO (record struct)
Use `Select` in queries (example in Application/GetOrder via `ToDto()` mapping extension). EF Core will project values into DTO without tracking.

## Mongo Read Endpoint
`GET /api/orders-read/{id}` reads a pre-projected document from Mongo (if you populate it via background sync/outbox in your real app).

