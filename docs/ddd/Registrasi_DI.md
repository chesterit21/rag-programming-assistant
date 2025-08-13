Berikut adalah **tata cara registrasi Dependency Injection (DI) service di `Program.cs`** untuk **ASP.NET Core versi terbaru (.NET 8)** dengan gaya **minimal hosting model** (yang sekarang menjadi default):

---

## ✅ Struktur Dasar `Program.cs` (.NET 8)

```csharp
using Microsoft.EntityFrameworkCore;
using Sales.Infrastructure.EFCore.Data;
using Sales.Infrastructure.EFCore.Provider;
using Sales.Infrastructure.EFCore.Repositories;
using Sales.Infrastructure.Mongo.Repositories;
using Sales.Domain.Abstractions;
using Sales.Domain.Orders;
using Sales.Application.Orders;
using Sales.Application.Validation;
using Sales.WebApi.Middleware;

var builder = WebApplication.CreateBuilder(args);

// 1. Tambahkan layanan MVC atau Minimal API
builder.Services.AddControllers(); // Untuk API
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// 2. Registrasi DbContext (EF Core) dengan provider dinamis
builder.Services.AddSalesDbContext(builder.Configuration);

// 3. Registrasi MongoDB (opsional)
builder.Services.AddSingleton<IMongoClient>(sp =>
{
    var cs = builder.Configuration.GetConnectionString("Mongo");
    return new MongoDB.Driver.MongoClient(cs);
});
builder.Services.AddSingleton<IMongoDatabase>(sp =>
{
    var client = sp.GetRequiredService<IMongoClient>();
    var dbName = builder.Configuration["Mongo:Database"] ?? "sales";
    return client.GetDatabase(dbName);
});

// 4. Registrasi Repository & Unit of Work
builder.Services.AddScoped<IOrderRepository, OrderRepository>();
builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();
builder.Services.AddScoped<IOrderReadRepository, OrderReadRepository>();

// 5. Registrasi Validator & Use Case
builder.Services.AddScoped<IValidator<PlaceOrder.Command>, PlaceOrderValidator>();
builder.Services.AddScoped<PlaceOrder>();
builder.Services.AddScoped<GetOrder>();

// 6. Middleware Global Error
builder.Services.AddTransient<ExceptionHandlingMiddleware>();

// 7. Event Sourcing (opsional)
if (builder.Configuration.GetSection("EventSourcing").GetValue<bool>("Enabled"))
{
    builder.Services.AddScoped<IEventSerializer, DefaultEventSerializer>();
    builder.Services.AddScoped<IEventStore, EfCoreEventStore>();
    builder.Services.AddScoped<IOrderRepository, EventSourcedOrderRepository>();
    builder.Services.AddHostedService<OrderToMongoProjector>();
}

// 8. Build & Configure Pipeline
var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseMiddleware<ExceptionHandlingMiddleware>();
app.MapControllers();
app.Run();
```

---

### ✅ Penjelasan Best Practice
1. **Gunakan `builder.Services`** untuk semua registrasi DI.
2. **Pisahkan konfigurasi** (misalnya `AddSalesDbContext`) ke extension method agar rapi.
3. **Gunakan `Scoped`** untuk service yang terkait request (misalnya repository, use case).
4. **Gunakan `Singleton`** untuk koneksi global seperti `MongoClient`.
5. **Gunakan `Transient`** untuk middleware custom.
6. **Gunakan `Configuration`** untuk membaca `.env` atau `appsettings.json`.

---

### ✅ Integrasi `.env`
Jika Anda ingin membaca variabel dari `.env`, tambahkan:
```csharp
DotNetEnv.Env.Load(); // Install paket DotNetEnv
```
di awal `Program.cs`, sebelum `builder.Configuration`.

---

🔥 **Mau saya buatkan file `Program.cs` lengkap + `.env.example` + update template agar otomatis load `.env` dan support Event Sourcing toggle?**  
Atau sekalian **Docker Compose** untuk Postgres + Mongo + RabbitMQ agar langsung jalan?