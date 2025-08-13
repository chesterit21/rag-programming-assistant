
using Microsoft.AspNetCore.Mvc;
using MongoDB.Driver;
using Sales.Domain.Abstractions;
using Sales.Domain.Orders;
using Sales.Application.Orders;
using Sales.Application.Validation;
using Sales.Infrastructure.EFCore.Data;
using Sales.Infrastructure.EFCore.Provider;
using Sales.Infrastructure.EFCore.Repositories;
using Sales.Infrastructure.Mongo.Repositories;
using Sales.WebApi.Middleware;

var builder = WebApplication.CreateBuilder(args);

// Services
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// EF Core provider selection (Postgres/MySQL/SQLite)
builder.Services.AddSalesDbContext(builder.Configuration);

// MongoDB (for read model or alternative query store)
var mongoCs = builder.Configuration.GetConnectionString("Mongo");
var mongoClient = new MongoClient(mongoCs);
builder.Services.AddSingleton<IMongoClient>(mongoClient);
builder.Services.AddSingleton<IMongoDatabase>(sp =>
{
    var client = sp.GetRequiredService<IMongoClient>();
    var dbName = builder.Configuration["Mongo:Database"] ?? "sales";
    return client.GetDatabase(dbName);
});

// DI: repositories & UoW
builder.Services.AddScoped<IOrderRepository, OrderRepository>();
builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();
builder.Services.AddScoped<IOrderReadRepository, OrderReadRepository>();

// Validators
builder.Services.AddScoped<IValidator<PlaceOrder.Command>, PlaceOrderValidator>();

// Use cases
builder.Services.AddScoped<PlaceOrder>();
builder.Services.AddScoped<GetOrder>();

// Middleware
builder.Services.AddTransient<ExceptionHandlingMiddleware>();

var app = builder.Build();

app.UseMiddleware<ExceptionHandlingMiddleware>();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapPost("/api/orders", async ([FromServices] PlaceOrder uc, [FromBody] PlaceOrder.Command cmd, CancellationToken ct) =>
{
    var res = await uc.Handle(cmd, ct);
    return Results.Created($"/api/orders/{res.OrderId}", res);
});

app.MapGet("/api/orders/{id:guid}", async ([FromServices] GetOrder uc, Guid id, CancellationToken ct) =>
{
    var dto = await uc.Handle(new GetOrder.Query(id), ct);
    return dto is null ? Results.NotFound() : Results.Ok(dto);
});

// Example: query via Mongo read repository
app.MapGet("/api/orders-read/{id:guid}", async ([FromServices] IOrderReadRepository repo, Guid id, CancellationToken ct) =>
{
    var r = await repo.GetAsync(id, ct);
    return r is null ? Results.NotFound() : Results.Ok(r);
});

app.Run();
