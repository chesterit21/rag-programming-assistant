---
Title: "Panduan Praktik Terbaik DDD untuk ASP.NET Core (MVC & Web API)"
Author: "M365 Copilot"
Version: "1.0"
Last-Updated: "2025-08-13"
Audience: "Senior/Lead Engineer, Solution Architect, AI Model Reader"
Format: "Markdown (.md) — dirancang agar mudah dipahami manusia & model AI"
---

# Panduan Praktik Terbaik DDD untuk ASP.NET Core (MVC & Web API)

> **Tujuan:** Dokumen ini menyajikan _blueprint_ penerapan **Domain-Driven Design (DDD)** di proyek **ASP.NET Core** (MVC & Web API), termasuk integrasi **Entity Framework Core**, **Repository**, **Clean Architecture**, **Event-Driven**, **CQRS**, _testing_ (xUnit), dan **Global Error Handling**. Struktur, gaya, dan metadata diformat agar **ramah pembaca manusia** dan **mudah diparse Model AI**.

---

## Daftar Isi
- [0. Ikhtisar Cepat](#0-ikhtisar-cepat)
- [1. DDD pada ASP.NET Core MVC — Penerapan Kode Terbaik](#1-ddd-pada-aspnet-core-mvc--penerapan-kode-terbaik)
- [2. Integrasi EF Core & Repository — Layering DDD](#2-integrasi-ef-core--repository--layering-ddd)
- [3. DDD + Clean Architecture + Repository + Event-Driven + CQRS + Web API](#3-ddd--clean-architecture--repository--event-driven--cqrs--web-api)
- [4. DDD yang Idealis — Pola yang Disarankan](#4-ddd-yang-idealis--pola-yang-disarankan)
- [5. Trade-off, Global Error, xUnit, dan Contoh Kode per Pola](#5-trade-off-global-error-xunit-dan-contoh-kode-per-pola)
- [Lampiran A — Struktur Solusi & Perintah CLI](#lampiran-a--struktur-solusi--perintah-cli)
- [Lampiran B — Konfigurasi & Catatan SQL Server (Docker)](#lampiran-b--konfigurasi--catatan-sql-server-docker)

---

## 0. Ikhtisar Cepat

- **Domain contoh**: _Sales_ dengan _Order_ sebagai **Aggregate Root**.
- **Konsep DDD**: Entity, Value Object, Domain Event, Aggregate Root, Domain Service, Ubiquitous Language.
- **Layer** (Clean/Hexagonal): `Domain` (core), `Application` (use-case/CQRS), `Infrastructure` (EF Core, repo, outbox), `Presentation` (MVC/Web API).
- **Prinsip**: Pisahkan domain dari detail infrastruktur. Domain berbicara bahasa bisnis. Minim ketergantungan keluar.

> **Tip**: Mulai dari _Bounded Context_ yang jelas; hindari model domain besar yang generik untuk seluruh perusahaan.

---

## 1. DDD pada ASP.NET Core MVC — Penerapan Kode Terbaik

### 1.1. Struktur Minimal (Proyek MVC *with domain inside solution*)
```
src/
  Sales.Domain/
  Sales.Application/
  Sales.Infrastructure/
  Sales.Web/                 # ASP.NET Core MVC (controller + views)
```

### 1.2. Domain Model — Entity, Value Object, Aggregate, Event

**Value Object** `Money` & `ProductId`:
```csharp
// Sales.Domain/ValueObjects/Money.cs
namespace Sales.Domain.ValueObjects;

public sealed record Money(decimal Amount, string Currency)
{
    public static Money Zero(string currency) => new(0m, currency);
    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new DomainException("Currency mismatch");
        return this with { Amount = Amount + other.Amount };
    }
}

public sealed record ProductId(Guid Value)
{
    public static ProductId New() => new(Guid.NewGuid());
}
```

**Entity & Aggregate Root** `Order` dengan invariant:
```csharp
// Sales.Domain/Orders/Order.cs
using Sales.Domain.ValueObjects;

namespace Sales.Domain.Orders;

public sealed class Order
{
    private readonly List<OrderLine> _lines = new();
    public OrderId Id { get; private set; }
    public CustomerId CustomerId { get; private set; }
    public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();
    public Money Total { get; private set; }
    public DateTime CreatedAt { get; private set; }

    private Order(OrderId id, CustomerId customerId)
    {
        Id = id;
        CustomerId = customerId;
        Total = Money.Zero("USD");
        CreatedAt = DateTime.UtcNow;
    }

    public static Order Create(CustomerId customerId)
    {
        if (customerId == default) throw new DomainException("Customer is required");
        var order = new Order(OrderId.New(), customerId);
        order.Raise(new OrderCreatedDomainEvent(order.Id.Value));
        return order;
    }

    public void AddLine(ProductId productId, int quantity, Money price)
    {
        if (quantity <= 0) throw new DomainException("Quantity must be > 0");
        var line = new OrderLine(productId, quantity, price);
        _lines.Add(line);
        RecalculateTotal();
    }

    private void RecalculateTotal()
    {
        Total = _lines.Select(l => new Money(l.Price.Amount * l.Quantity, l.Price.Currency))
                      .Aggregate(Money.Zero("USD"), (acc, m) => acc.Add(m));
    }

    // Domain Events (simple in-memory collection)
    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();
    private void Raise(IDomainEvent @event) => _domainEvents.Add(@event);
}

public sealed record OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.NewGuid());
}

public sealed record CustomerId(Guid Value)
{
    public static CustomerId New() => new(Guid.NewGuid());
}

public sealed class OrderLine
{
    public ProductId ProductId { get; }
    public int Quantity { get; }
    public Money Price { get; }

    public OrderLine(ProductId productId, int quantity, Money price)
    {
        ProductId = productId;
        Quantity = quantity;
        Price = price;
    }
}

public interface IDomainEvent { }
public sealed record OrderCreatedDomainEvent(Guid OrderId) : IDomainEvent;

public sealed class DomainException : Exception
{
    public DomainException(string message) : base(message) { }
}
```

### 1.3. Port (Abstraksi) — Repository & Unit of Work (di Domain atau Application)
```csharp
// Sales.Domain/Orders/IOrderRepository.cs
namespace Sales.Domain.Orders;

public interface IOrderRepository
{
    Task<Order?> GetAsync(OrderId id, CancellationToken ct = default);
    Task AddAsync(Order order, CancellationToken ct = default);
    Task UpdateAsync(Order order, CancellationToken ct = default);
}

// Sales.Domain/Abstractions/IUnitOfWork.cs
namespace Sales.Domain.Abstractions;

public interface IUnitOfWork
{
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}
```

> **Best Practice**: Simpan **interface** repository di **Domain** (atau **Application**) sebagai _port_. Implementasi berada di **Infrastructure**.

### 1.4. Application Service (Use Case) dipanggil dari MVC Controller
```csharp
// Sales.Application/Orders/CreateOrder.cs
using Sales.Domain.Orders;
using Sales.Domain.Abstractions;
using Sales.Domain.ValueObjects;

namespace Sales.Application.Orders;

public sealed class CreateOrder
{
    public sealed record Command(Guid CustomerId) ;
    public sealed record Result(Guid OrderId);

    private readonly IOrderRepository _repo;
    private readonly IUnitOfWork _uow;

    public CreateOrder(IOrderRepository repo, IUnitOfWork uow)
    { _repo = repo; _uow = uow; }

    public async Task<Result> Handle(Command cmd, CancellationToken ct)
    {
        var order = Order.Create(new CustomerId(cmd.CustomerId));
        await _repo.AddAsync(order, ct);
        await _uow.SaveChangesAsync(ct);
        return new Result(order.Id.Value);
    }
}
```

**MVC Controller** yang memanggil use case:
```csharp
// Sales.Web/Controllers/OrdersController.cs
using Microsoft.AspNetCore.Mvc;
using Sales.Application.Orders;

namespace Sales.Web.Controllers;

public class OrdersController : Controller
{
    private readonly CreateOrder _createOrder;
    public OrdersController(CreateOrder createOrder) => _createOrder = createOrder;

    [HttpPost]
    public async Task<IActionResult> Create([FromForm] Guid customerId, CancellationToken ct)
    {
        var result = await _createOrder.Handle(new CreateOrder.Command(customerId), ct);
        return RedirectToAction("Details", new { id = result.OrderId });
    }

    [HttpGet]
    public IActionResult New() => View();
}
```

> **Checklist Praktik Terbaik (MVC + DDD)**
> - Controller tipis → panggil use case di Application.
> - Domain berisi aturan & invariant; **bukan** Anemic Model.
> - Event domain diangkat saat kondisi bisnis terpenuhi.
> - Hindari `DbContext` bocor ke Domain/Application.

---

## 2. Integrasi EF Core & Repository — Layering DDD

### 2.1. DbContext & Mapping (Infrastructure)
```csharp
// Sales.Infrastructure/Data/SalesDbContext.cs
using Microsoft.EntityFrameworkCore;
using Sales.Domain.Orders;
using Sales.Domain.ValueObjects;

namespace Sales.Infrastructure.Data;

public sealed class SalesDbContext : DbContext
{
    public DbSet<Order> Orders => Set<Order>();

    public SalesDbContext(DbContextOptions<SalesDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Order>(b =>
        {
            b.HasKey(o => o.Id);
            b.Property(o => o.Id)
             .HasConversion(id => id.Value, v => new OrderId(v));

            b.Property(o => o.CustomerId)
             .HasConversion(id => id.Value, v => new CustomerId(v));

            b.OwnsMany(typeof(OrderLine), "_lines", lb =>
            {
                lb.WithOwner().HasForeignKey("OrderId");
                lb.Property<ProductId>("ProductId")
                  .HasConversion(id => id.Value, v => new ProductId(v));
                lb.Property<int>("Quantity");
                lb.OwnsOne(typeof(Money), "Price", mb =>
                {
                    mb.Property<decimal>("Amount");
                    mb.Property<string>("Currency").HasMaxLength(3);
                });
                lb.ToTable("OrderLines");
            });

            b.OwnsOne(o => o.Total, mb =>
            {
                mb.Property(m => m.Amount).HasColumnName("TotalAmount");
                mb.Property(m => m.Currency).HasColumnName("TotalCurrency").HasMaxLength(3);
            });

            b.Ignore(o => o.DomainEvents);
            b.ToTable("Orders");
        });
    }
}
```

### 2.2. Repository Implementations
```csharp
// Sales.Infrastructure/Repositories/OrderRepository.cs
using Microsoft.EntityFrameworkCore;
using Sales.Domain.Orders;
using Sales.Infrastructure.Data;

namespace Sales.Infrastructure.Repositories;

public sealed class OrderRepository : IOrderRepository
{
    private readonly SalesDbContext _db;
    public OrderRepository(SalesDbContext db) => _db = db;

    public async Task AddAsync(Order order, CancellationToken ct = default)
        => await _db.Orders.AddAsync(order, ct);

    public async Task<Order?> GetAsync(OrderId id, CancellationToken ct = default)
        => await _db.Orders
            .Include("_lines")
            .FirstOrDefaultAsync(o => o.Id == id, ct);

    public Task UpdateAsync(Order order, CancellationToken ct = default)
    { _db.Orders.Update(order); return Task.CompletedTask; }
}

// Sales.Infrastructure/Data/UnitOfWork.cs
using Sales.Domain.Abstractions;

namespace Sales.Infrastructure.Data;

public sealed class UnitOfWork : IUnitOfWork
{
    private readonly SalesDbContext _db;
    public UnitOfWork(SalesDbContext db) => _db = db;
    public Task<int> SaveChangesAsync(CancellationToken ct = default)
        => _db.SaveChangesAsync(ct);
}
```

### 2.3. Layering & Dependency Rules

```
Presentation (MVC/WebAPI)
  ⬇ depends on
Application (Use Cases, CQRS)
  ⬇ depends on
Domain (Entities, ValueObjects, Events, Repo interfaces)
  ⬆ implemented by
Infrastructure (EF Core, Repos, Outbox, External Adapters)
```

> **Best Practice**: `Presentation` dan `Application` **mengacu** ke `Domain`, **tidak** ke `Infrastructure`. `Infrastructure` **mengimplementasikan** port dari `Domain`/`Application`.

---

## 3. DDD + Clean Architecture + Repository + Event-Driven + CQRS + Web API

### 3.1. Layer Clean Architecture (diperkaya DDD)
```
Domain ── core bisnis (Entities, Value Objects, Domain Events, Policies)
Application ── use-cases & CQRS (Commands/Queries, Handlers, Validators)
Infrastructure ── EF Core, Repositories, Outbox, Message Bus Adapter
Presentation ── Web API (Controllers/Minimal API) atau MVC
```

### 3.2. CQRS: Command & Query
```csharp
// Sales.Application/Orders/PlaceOrder.cs (Command)
using Sales.Domain.Orders; using Sales.Domain.Abstractions; using Sales.Domain.ValueObjects;

namespace Sales.Application.Orders;

public sealed class PlaceOrder
{
    public sealed record Command(Guid CustomerId, IEnumerable<LineDto> Lines);
    public sealed record LineDto(Guid ProductId, int Quantity, decimal Price, string Currency);
    public sealed record Result(Guid OrderId, decimal TotalAmount, string Currency);

    private readonly IOrderRepository _repo; private readonly IUnitOfWork _uow;
    public PlaceOrder(IOrderRepository repo, IUnitOfWork uow) { _repo = repo; _uow = uow; }

    public async Task<Result> Handle(Command cmd, CancellationToken ct)
    {
        var order = Order.Create(new CustomerId(cmd.CustomerId));
        foreach (var l in cmd.Lines)
            order.AddLine(new ProductId(l.ProductId), l.Quantity, new Money(l.Price, l.Currency));

        await _repo.AddAsync(order, ct);
        await _uow.SaveChangesAsync(ct);
        return new Result(order.Id.Value, order.Total.Amount, order.Total.Currency);
    }
}

// Sales.Application/Orders/GetOrder.cs (Query)
using Sales.Domain.Orders;

namespace Sales.Application.Orders;

public sealed class GetOrder
{
    public sealed record Query(Guid OrderId);
    public sealed record Dto(Guid OrderId, Guid CustomerId, decimal Total, string Currency, int Lines);

    private readonly IOrderRepository _repo;
    public GetOrder(IOrderRepository repo) => _repo = repo;

    public async Task<Dto?> Handle(Query q, CancellationToken ct)
    {
        var order = await _repo.GetAsync(new OrderId(q.OrderId), ct);
        return order is null ? null
            : new Dto(order.Id.Value, order.CustomerId.Value, order.Total.Amount, order.Total.Currency, order.Lines.Count);
    }
}
```

### 3.3. Web API Controller (thin)
```csharp
// Sales.WebApi/Controllers/OrdersController.cs
using Microsoft.AspNetCore.Mvc;
using Sales.Application.Orders;

namespace Sales.WebApi.Controllers;

[ApiController]
[Route("api/orders")]
public class OrdersController : ControllerBase
{
    [HttpPost]
    public async Task<ActionResult<PlaceOrder.Result>> Place(
        [FromServices] PlaceOrder useCase,
        [FromBody] PlaceOrder.Command cmd,
        CancellationToken ct)
    {
        var result = await useCase.Handle(cmd, ct);
        return CreatedAtAction(nameof(Get), new { id = result.OrderId }, result);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<GetOrder.Dto>> Get(
        [FromServices] GetOrder useCase,
        [FromRoute] Guid id,
        CancellationToken ct)
    {
        var dto = await useCase.Handle(new GetOrder.Query(id), ct);
        return dto is null ? NotFound() : Ok(dto);
    }
}
```

### 3.4. Event-Driven: Domain Event → Integration Event (Outbox Pattern)

**Outbox Entity & DbContext extension**:
```csharp
// Sales.Infrastructure/Outbox/OutboxMessage.cs
public sealed class OutboxMessage
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public DateTime OccurredOnUtc { get; init; } = DateTime.UtcNow;
    public string Type { get; init; } = default!;  // e.g. "OrderCreated"
    public string Payload { get; init; } = default!; // JSON domain event
    public DateTime? ProcessedOnUtc { get; set; }
    public string? Error { get; set; }
}

// extend SalesDbContext.OnModelCreating
modelBuilder.Entity<OutboxMessage>(b => { b.ToTable("Outbox" ); b.HasKey(x => x.Id); });
```

**Save Domain Events into Outbox on SaveChanges**:
```csharp
// Sales.Infrastructure/Data/SalesDbContext.SaveChangesInterceptor.cs
using Microsoft.EntityFrameworkCore.Diagnostics;
using System.Text.Json;
using Sales.Domain.Orders;

public sealed class DomainEventsToOutboxInterceptor : SaveChangesInterceptor
{
    public override ValueTask<InterceptionResult<int>> SavingChangesAsync(
        DbContextEventData eventData, InterceptionResult<int> result, CancellationToken ct = default)
    {
        if (eventData.Context is not SalesDbContext db) return new(result);

        var events = db.ChangeTracker.Entries()
            .Select(e => e.Entity)
            .OfType<Order>()
            .SelectMany(o => o.DomainEvents)
            .ToList();

        foreach (var ev in events)
        {
            db.Set<OutboxMessage>().Add(new OutboxMessage
            {
                Type = ev.GetType().Name,
                Payload = JsonSerializer.Serialize(ev)
            });
        }
        return new(result);
    }
}
```

**Background Publisher** (keluarkan ke broker, mis. Kafka/RabbitMQ/Azure Service Bus):
```csharp
// Sales.Infrastructure/Outbox/OutboxPublisher.cs
using Microsoft.EntityFrameworkCore;

public interface IMessageBus { Task PublishAsync(string type, string payload, CancellationToken ct); }

public sealed class OutboxPublisher : BackgroundService
{
    private readonly IServiceProvider _sp;
    public OutboxPublisher(IServiceProvider sp) => _sp = sp;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            using var scope = _sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<SalesDbContext>();
            var bus = scope.ServiceProvider.GetRequiredService<IMessageBus>();

            var messages = await db.Set<OutboxMessage>()
                .Where(m => m.ProcessedOnUtc == null)
                .OrderBy(m => m.OccurredOnUtc)
                .Take(100)
                .ToListAsync(stoppingToken);

            foreach (var m in messages)
            {
                try
                {
                    await bus.PublishAsync(m.Type, m.Payload, stoppingToken);
                    m.ProcessedOnUtc = DateTime.UtcNow;
                }
                catch (Exception ex)
                { m.Error = ex.ToString(); }
            }
            await db.SaveChangesAsync(stoppingToken);
            await Task.Delay(TimeSpan.FromSeconds(2), stoppingToken);
        }
    }
}
```

> **Catatan**: Outbox menjaga **konsistensi akhir** (event tidak hilang meski crash setelah commit DB).

---

## 4. DDD yang Idealis — Pola yang Disarankan

**Inti ideal DDD (ringkas):**
- **Aggregate Root** yang jelas & kecil (ukuran _transactional consistency_ minimal).
- **Value Object** untuk konsep yang tidak ber-identity (Money, Address).
- **Domain Event** untuk memodelkan fakta bisnis.
- **Domain Service** untuk aturan lintas entitas yang tidak cocok di entity.
- **Specification Pattern** untuk query/seleksi yang kaya (opsional, hati-hati dengan EF Core provider).
- **Hexagonal/Ports & Adapters**: Domain → interface; Infrastructure → adapter.
- **Outbox + Event-Driven** untuk integrasi antarlayanan.
- **Anti-Corruption Layer (ACL)** ketika berinteraksi lintas _bounded context_.

> **Pedoman**: Mulai dari **bahasa bisnis** (Ubiquitous Language), bukan dari database atau framework.

---

## 5. Trade-off, Global Error, xUnit, dan Contoh Kode per Pola

### 5.1. Trade-off saat Menggabungkan Pola

| Pola | Benefit | Trade-off/Korban |
|---|---|---|
| Clean Architecture | Ketergantungan terbalik, testability tinggi | Lebih banyak proyek/lapisan; _boilerplate_ |
| Repository + EF Core | Abstraksi DB, mocking mudah | Kadang redundant dengan `DbContext`; risiko _leaky abstraction_ |
| Event-Driven + Outbox | Skalabilitas, loose coupling | Kompleksitas, _eventual consistency_, monitoring outbox |
| CQRS | Optimasi read/write, skala terpisah | Dua model, _sync_ & _schema drift_, _overhead_ |
| Web API | Interop luas | Versioning, kontrak DTO, backward-compat |
| xUnit + Tests | Kepercayaan perubahan, regression guard | Biaya perawatan test |
| Global Error | Observability, UX konsisten | Perlu kebijakan mapping exception → problem details |

### 5.2. Global Error Handling (Middleware + ProblemDetails)
```csharp
// Sales.WebApi/Middleware/ExceptionHandlingMiddleware.cs
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using Sales.Domain.Orders; // DomainException

public sealed class ExceptionHandlingMiddleware : IMiddleware
{
    private readonly ILogger<ExceptionHandlingMiddleware> _log;
    public ExceptionHandlingMiddleware(ILogger<ExceptionHandlingMiddleware> log) => _log = log;

    public async Task InvokeAsync(HttpContext ctx, RequestDelegate next)
    {
        try { await next(ctx); }
        catch (DomainException ex)
        {
            _log.LogWarning(ex, "Domain error");
            await WriteProblem(ctx, StatusCodes.Status409Conflict, ex.Message, "domain_error");
        }
        catch (ValidationException ex)
        {
            _log.LogWarning(ex, "Validation error");
            await WriteProblem(ctx, StatusCodes.Status400BadRequest, ex.Message, "validation_error", ex.Errors);
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Unhandled error");
            await WriteProblem(ctx, StatusCodes.Status500InternalServerError, "Internal Server Error", "unhandled_error");
        }
    }

    private static Task WriteProblem(HttpContext ctx, int status, string detail, string code, object? errors = null)
    {
        ctx.Response.ContentType = "application/problem+json";
        ctx.Response.StatusCode = status;
        var problem = new
        {
            type = $"https://httpstatuses.com/{status}",
            title = code,
            status,
            detail,
            traceId = ctx.TraceIdentifier,
            errors
        };
        return ctx.Response.WriteAsync(JsonSerializer.Serialize(problem));
    }
}

// Program.cs (registrasi)
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddTransient<ExceptionHandlingMiddleware>();
var app = builder.Build();
app.UseMiddleware<ExceptionHandlingMiddleware>();
```

> **Mapping Saran**: `DomainException` → 409, `ValidationException` → 400, `UnauthorizedAccessException` → 401, tidak ditemukan → 404.

### 5.3. Testing (xUnit)

**Unit Test Domain**:
```csharp
// tests/Sales.Domain.Tests/OrderTests.cs
using Sales.Domain.Orders; using Sales.Domain.ValueObjects; using Xunit;

public class OrderTests
{
    [Fact]
    public void New_Order_Should_Have_Total_Zero()
    {
        var o = Order.Create(new CustomerId(Guid.NewGuid()));
        Assert.Equal(0m, o.Total.Amount);
    }

    [Fact]
    public void AddLine_Should_Increase_Total()
    {
        var o = Order.Create(new CustomerId(Guid.NewGuid()));
        o.AddLine(new ProductId(Guid.NewGuid()), 2, new Money(10m, "USD"));
        Assert.Equal(20m, o.Total.Amount);
    }
}
```

**Integration Test Application + EF Core InMemory**:
```csharp
// tests/Sales.Application.Tests/PlaceOrderTests.cs
using Microsoft.EntityFrameworkCore; using Sales.Application.Orders; using Sales.Infrastructure.Data; using Sales.Infrastructure.Repositories; using Xunit;

public class PlaceOrderTests
{
    [Fact]
    public async Task PlaceOrder_Should_Persist_And_Return_Total()
    {
        var opts = new DbContextOptionsBuilder<SalesDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        var db = new SalesDbContext(opts);
        var repo = new OrderRepository(db);
        var uow = new UnitOfWork(db);

        var useCase = new PlaceOrder(repo, uow);
        var result = await useCase.Handle(
            new PlaceOrder.Command(
                Guid.NewGuid(),
                new[] { new PlaceOrder.LineDto(Guid.NewGuid(), 3, 5m, "USD") }
            ), default);

        Assert.True(result.TotalAmount == 15m);
        Assert.NotEqual(Guid.Empty, result.OrderId);
    }
}
```

### 5.4. Penggabungan Pola — Contoh Registrasi DI
```csharp
// Program.cs (umum untuk MVC/Web API)
using Microsoft.EntityFrameworkCore;
using Sales.Infrastructure.Data; using Sales.Infrastructure.Repositories;
using Sales.Domain.Orders; using Sales.Domain.Abstractions;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews(); // atau AddControllers untuk Web API

builder.Services.AddDbContext<SalesDbContext>(opt =>
    opt.UseSqlServer(builder.Configuration.GetConnectionString("SalesDb"))
       .EnableSensitiveDataLogging(false));

builder.Services.AddScoped<IOrderRepository, OrderRepository>();
builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();

builder.Services.AddScoped<Sales.Application.Orders.CreateOrder>();
builder.Services.AddScoped<Sales.Application.Orders.PlaceOrder>();
builder.Services.AddScoped<Sales.Application.Orders.GetOrder>();

builder.Services.AddHostedService<OutboxPublisher>();

var app = builder.Build();
app.MapControllers();
app.Run();
```

---

## Lampiran A — Struktur Solusi & Perintah CLI

### A.1. Struktur Solusi yang Direkomendasikan
```
src/
  Sales.Domain/
  Sales.Application/
  Sales.Infrastructure/
  Sales.Web/            # MVC
  Sales.WebApi/         # Web API (opsional jika dipisah dari MVC)
tests/
  Sales.Domain.Tests/
  Sales.Application.Tests/
```

### A.2. Perintah `dotnet` (contoh)
```bash
# solusi & proyek
mkdir sales-ddd && cd sales-ddd
 dotnet new sln -n Sales
 dotnet new classlib -n Sales.Domain -o src/Sales.Domain
 dotnet new classlib -n Sales.Application -o src/Sales.Application
 dotnet new classlib -n Sales.Infrastructure -o src/Sales.Infrastructure
 dotnet new mvc -n Sales.Web -o src/Sales.Web
 dotnet new webapi -n Sales.WebApi -o src/Sales.WebApi
 dotnet new xunit -n Sales.Domain.Tests -o tests/Sales.Domain.Tests
 dotnet new xunit -n Sales.Application.Tests -o tests/Sales.Application.Tests

 dotnet sln add src/**/**/*.csproj tests/**/**/*.csproj

# paket (contoh)
 dotnet add src/Sales.Infrastructure package Microsoft.EntityFrameworkCore
 dotnet add src/Sales.Infrastructure package Microsoft.EntityFrameworkCore.SqlServer
 dotnet add src/Sales.Infrastructure package Microsoft.Extensions.Hosting.Abstractions
 dotnet add tests/Sales.Application.Tests package Microsoft.EntityFrameworkCore.InMemory
```

---

## Lampiran B — Konfigurasi & Catatan SQL Server (Docker)

**appsettings.json** (contoh koneksi SQL Server):
```json
{
  "ConnectionStrings": {
    "SalesDb": "Server=localhost,11433;Database=SalesDb;User Id=sa;Password=Your_password123;TrustServerCertificate=True;"
  }
}
```

> **Catatan pribadi**: Jika Anda menjalankan **SQL Server Developer di Docker** untuk aplikasi lain dan **port 1433** sudah digunakan, gunakan **port mapping alternatif** (mis. `-p 11433:1433`) lalu sesuaikan connection string `Server=localhost,11433`. Hindari konflik port.

---

## Ringkasan
- DDD menempatkan **domain sebagai pusat**. 
- **EF Core** hanya sebagai detail infrastruktur dengan mapping yang menghormati **Value Objects** & **Aggregates**.
- Kombinasi **Clean Architecture + CQRS + Outbox** memberikan struktur yang bersih, teruji, dan siap skala, dengan biaya **kompleksitas** tambahan.
- Pertahankan **Controller tipis**, **use case eksplisit**, **error handling konsisten (ProblemDetails)**, serta **test domain & aplikasi**.

---

### Glosarium (untuk Model AI)
- **Aggregate**: Gugus entity yang konsisten secara transaksi, dipimpin **Aggregate Root**.
- **VO (Value Object)**: Tipe tanpa identitas, immutabel, ditentukan oleh nilai (Money, Address).
- **Domain Event**: Fakta bisnis yang terjadi di domain (OrderCreated).
- **Outbox**: Tabel untuk menyimpan event agar dipublikasikan ke message broker secara andal.
- **CQRS**: Pisah model perintah (write) dan query (read) untuk skalabilitas.




# Domain-Driven Design (DDD) pada ASP.NET Core MVC

---

## 1. Penerapan DDD dengan Praktik Terbaik

### **Konsep Dasar**

Domain-Driven Design (DDD) adalah pendekatan untuk mengembangkan software yang fokus pada model domain bisnis dan bahasa yang digunakan oleh para ahli domain. Pada ASP.NET Core MVC, praktik terbaik DDD memisahkan kode ke dalam lapisan-lapisan yang jelas agar mudah dikelola, scalable, dan dapat diuji.

### **Struktur Folder Praktik Terbaik**

```
src/
├── Application/           # Use Cases, DTO, Service Interfaces
├── Domain/                # Entities, Value Objects, Domain Events, Aggregates
├── Infrastructure/        # EF Core, Repository Implementation, External Services
├── WebUI/                 # ASP.NET Core MVC Controllers, Views, ViewModels
```

### **Contoh Kasus: Order**

#### **Domain Layer**

```csharp
// Domain/Entities/Order.cs
public class Order
{
    public Guid Id { get; private set; }
    public string CustomerName { get; private set; }
    public List<OrderItem> Items { get; private set; } = new();

    public Order(string customerName)
    {
        Id = Guid.NewGuid();
        CustomerName = customerName;
    }

    public void AddItem(string productName, int quantity, decimal price)
    {
        Items.Add(new OrderItem(productName, quantity, price));
    }
}

public class OrderItem
{
    public string ProductName { get; private set; }
    public int Quantity { get; private set; }
    public decimal Price { get; private set; }

    public OrderItem(string productName, int quantity, decimal price)
    {
        ProductName = productName;
        Quantity = quantity;
        Price = price;
    }
}
```

#### **Application Layer**

```csharp
// Application/Orders/CreateOrderHandler.cs
public class CreateOrderHandler
{
    private readonly IOrderRepository _repository;

    public CreateOrderHandler(IOrderRepository repository)
    {
        _repository = repository;
    }

    public async Task<Guid> HandleAsync(string customerName, List<(string productName, int qty, decimal price)> items)
    {
        var order = new Order(customerName);
        foreach (var item in items)
            order.AddItem(item.productName, item.qty, item.price);

        await _repository.AddAsync(order);
        return order.Id;
    }
}
```

#### **Infrastructure Layer**

```csharp
// Infrastructure/Repositories/OrderRepository.cs
public class OrderRepository : IOrderRepository
{
    private readonly AppDbContext _context;

    public OrderRepository(AppDbContext context) => _context = context;

    public async Task AddAsync(Order order)
    {
        _context.Orders.Add(order);
        await _context.SaveChangesAsync();
    }
}
```

#### **WebUI Layer**

```csharp
// WebUI/Controllers/OrdersController.cs
public class OrdersController : Controller
{
    private readonly CreateOrderHandler _createOrderHandler;

    public OrdersController(CreateOrderHandler createOrderHandler)
    {
        _createOrderHandler = createOrderHandler;
    }

    [HttpPost]
    public async Task<IActionResult> Create(CreateOrderDto dto)
    {
        var orderId = await _createOrderHandler.HandleAsync(dto.CustomerName, dto.Items);
        return RedirectToAction("Details", new { id = orderId });
    }
}
```

#### **Keterangan**

* **Entities**: Representasi domain murni.
* **Repository**: Abstraksi akses data.
* **Handlers/Use Cases**: Logika aplikasi.
* **Controller**: Mengatur request/response.

---

## 2. Integrasi DDD + EF Core + Repository

### **Konsep**

* EF Core berada di `Infrastructure`.
* Interface Repository di `Domain` atau `Application`.
* Implementasi Repository di `Infrastructure`.

**Layering Setup:**

```
Domain → Application → Infrastructure → WebUI
```

**Contoh:**

```csharp
// Domain/Repositories/IOrderRepository.cs
public interface IOrderRepository
{
    Task AddAsync(Order order);
    Task<Order> GetByIdAsync(Guid id);
}

// Infrastructure/AppDbContext.cs
public class AppDbContext : DbContext
{
    public DbSet<Order> Orders { get; set; }
    public AppDbContext(DbContextOptions options) : base(options) { }
}
```

---

## 3. DDD + Clean Architecture + Repository + Event Driven + CQRS + WebApi

### **Struktur Layer**

```
Application: Commands, Queries, Handlers
Domain: Entities, Events, Value Objects
Infrastructure: EF Core, Event Bus
WebApi: Controllers, DTOs
```

**Contoh Command Handler CQRS:**

```csharp
public record CreateOrderCommand(string CustomerName, List<OrderItemDto> Items) : IRequest<Guid>;

public class CreateOrderCommandHandler : IRequestHandler<CreateOrderCommand, Guid>
{
    private readonly IOrderRepository _repository;
    private readonly IEventBus _eventBus;

    public CreateOrderCommandHandler(IOrderRepository repository, IEventBus eventBus)
    {
        _repository = repository;
        _eventBus = eventBus;
    }

    public async Task<Guid> Handle(CreateOrderCommand request, CancellationToken cancellationToken)
    {
        var order = new Order(request.CustomerName);
        foreach (var item in request.Items)
            order.AddItem(item.ProductName, item.Quantity, item.Price);

        await _repository.AddAsync(order);
        _eventBus.Publish(new OrderCreatedEvent(order.Id));

        return order.Id;
    }
}
```

---

## 4. DDD Ideal: Pattern yang Digunakan

* **Aggregate Root** untuk mengelola konsistensi.
* **Repository Pattern** untuk abstraksi data.
* **Domain Events** untuk integrasi antar bounded context.
* **CQRS** untuk pemisahan command/query.
* **Event Sourcing** (opsional) untuk histori perubahan.

**Contoh**: Sama dengan #3, namun tambahkan Event Sourcing jika diperlukan.

---

## 5. Trade-off & Integrasi dengan Pattern Lain

### **Trade-off**

* **Clean Architecture**: Lebih banyak boilerplate.
* **Repository Pattern**: Bisa redundant jika EF Core sudah cukup.
* **Event Driven**: Kompleksitas tinggi.
* **CQRS**: Menambah jumlah file dan kode.
* **Unit Test**: Perlu mock repository & event bus.

### **Global Error Handling ASP.NET Core**

```csharp
public class ErrorHandlingMiddleware
{
    private readonly RequestDelegate _next;
    public ErrorHandlingMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            context.Response.StatusCode = 500;
            await context.Response.WriteAsJsonAsync(new { error = ex.Message });
        }
    }
}
```

**Registrasi:**

```csharp
app.UseMiddleware<ErrorHandlingMiddleware>();
```

---

📌 **Catatan**
* Struktur folder dan kode disesuaikan untuk maintainability.
* Dapat dikembangkan untuk API, MVC, atau Microservices.


**Menyusun desain Event Sourcing**

Menganalisis permintaan untuk menyediakan desain, contoh kode, dan integrasi dengan DDD, EF Core, Mongo, dan Outbox, tanpa perlu pencarian web, karena event sourcing tidak terlalu sensitif waktu.

**Mengusulkan desain Event Store**

Menyarankan desain untuk Event Store opsional per agregat, dengan integrasi ke EF Core, pengelolaan versi, snapshot opsional, dan penggunaan event sourcing untuk mengelola data dengan Mongo atau tabel baca relasional.

**Menyiapkan Implementasi Event Sourcing**

Menyusun rencana untuk menyimpan event di Event Store dan Outbox, membuat proyeksi ke Mongo, serta menambahkan struktur baru seperti EventSourcedOrderRepository dan EventSourcedAggregate dengan konfigurasi dalam folder baru di template yang ada.

**working...**


<m-result-block>
Status: Success

Result: /mnt/data/event-sourcing-addon.zip
</m-result-block>

**Coding and Executing...**

python
import os, textwrap, zipfile
from pathlib import Path

root = Path('/mnt/data/sales-ddd-template-es')

# create addon structure
paths = [
    'src/Sales.Domain/Abstractions',
    'src/Sales.Domain/Orders',
    'src/Sales.Infrastructure.EFCore/EventStore',
    'src/Sales.Infrastructure.EFCore/Projections',
    'src/Sales.WebApi/Controllers'
]
for p in paths:
    (root/p).mkdir(parents=True, exist_ok=True)

# Domain abstractions for ES
(root/'src/Sales.Domain/Abstractions/EventSourcing.cs').write_text(textwrap.dedent('''
namespace Sales.Domain.Abstractions;

public interface IEvent { }

public sealed class EventEnvelope
{
    public Guid StreamId { get; init; }
    public int Version { get; init; }
    public string Type { get; init; } = default!;
    public string Payload { get; init; } = default!; // JSON
    public DateTime OccurredOnUtc { get; init; }
    public IDictionary<string, string>? Metadata { get; init; }
}

public interface IEventSerializer
{
    string Serialize(IEvent @event);
    IEvent Deserialize(string type, string json);
}

public interface IEventStore
{
    Task<IReadOnlyList<EventEnvelope>> ReadStreamAsync(Guid streamId, CancellationToken ct = default);
    Task AppendToStreamAsync(Guid streamId, int expectedVersion, IEnumerable<IEvent> events, IDictionary<string,string>? metadata = null, CancellationToken ct = default);
}

public abstract class EventSourcedAggregate
{
    private readonly List<IEvent> _uncommitted = new();
    public Guid Id { get; protected set; }
    public int Version { get; protected set; } = 0;
    public IReadOnlyList<IEvent> GetUncommittedEvents() => _uncommitted.AsReadOnly();
    public void ClearUncommittedEvents() => _uncommitted.Clear();

    protected void Apply(IEvent @event)
    {
        When(@event);
        _uncommitted.Add(@event);
        Version++;
    }

    protected abstract void When(IEvent @event);

    public void LoadFromHistory(IEnumerable<IEvent> history)
    {
        foreach (var e in history)
        {
            When(e);
            Version++;
        }
        _uncommitted.Clear();
    }
}
'''), encoding='utf-8')

# Update Order events to implement IEvent and add LineAdded event
(root/'src/Sales.Domain/Orders/Order.Events.cs').write_text(textwrap.dedent('''
using Sales.Domain.Abstractions;
using Sales.Domain.ValueObjects;

namespace Sales.Domain.Orders;

public sealed record OrderCreated(Guid OrderId, Guid CustomerId, DateTime CreatedAtUtc) : IEvent;
public sealed record OrderLineAdded(Guid OrderId, Guid ProductId, int Quantity, decimal UnitPrice, string Currency) : IEvent;
'''), encoding='utf-8')

# Event-sourced Order aggregate (optional replacement)
(root/'src/Sales.Domain/Orders/Order.EventSourced.cs').write_text(textwrap.dedent('''
using Sales.Domain.Abstractions;
using Sales.Domain.ValueObjects;

namespace Sales.Domain.Orders;

public sealed class OrderEs : EventSourcedAggregate
{
    private readonly List<OrderLine> _lines = new();
    public CustomerId CustomerId { get; private set; }
    public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();
    public Money Total { get; private set; } = Money.Zero("USD");
    public DateTime CreatedAt { get; private set; }

    private OrderEs() { }

    public static OrderEs Create(CustomerId customerId)
    {
        if (customerId == default) throw new DomainException("Customer is required");
        var agg = new OrderEs();
        agg.Apply(new OrderCreated(Guid.NewGuid(), customerId.Value, DateTime.UtcNow));
        return agg;
    }

    public void AddLine(ProductId productId, int quantity, Money price)
    {
        if (quantity <= 0) throw new DomainException("Quantity must be > 0");
        Apply(new OrderLineAdded(Id, productId.Value, quantity, price.Amount, price.Currency));
    }

    protected override void When(IEvent @event)
    {
        switch (@event)
        {
            case OrderCreated e:
                Id = e.OrderId; CustomerId = new CustomerId(e.CustomerId); CreatedAt = e.CreatedAtUtc; Total = Money.Zero("USD");
                break;
            case OrderLineAdded e:
                _lines.Add(new OrderLine(new ProductId(e.ProductId), e.Quantity, new Money(e.UnitPrice, e.Currency)));
                Recalc();
                break;
        }
    }

    private void Recalc()
    {
        Total = _lines
            .Select(l => new Money(l.Price.Amount * l.Quantity, l.Price.Currency))
            .Aggregate(Money.Zero("USD"), (acc, m) => acc.Add(m));
    }
}
'''), encoding='utf-8')

# EF Core Event store entities and implementation
(root/'src/Sales.Infrastructure.EFCore/EventStore/EventEntities.cs').write_text(textwrap.dedent('''
using Microsoft.EntityFrameworkCore;

namespace Sales.Infrastructure.EFCore.EventStore;

public sealed class StoredEvent
{
    public long   Sequence       { get; set; }  // auto-increment
    public Guid   StreamId       { get; set; }
    public int    Version        { get; set; }
    public string Type           { get; set; } = default!;
    public string Payload        { get; set; } = default!;
    public DateTime OccurredOnUtc{ get; set; }
}

public sealed class Snapshot
{
    public Guid StreamId { get; set; }
    public int  Version  { get; set; }
    public string Payload { get; set; } = default!;
    public DateTime CreatedOnUtc { get; set; }
}

public static class EventStoreModel
{
    public static void Configure(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<StoredEvent>(b =>
        {
            b.ToTable("Events");
            b.HasKey(x => x.Sequence);
            b.HasIndex(x => new { x.StreamId, x.Version }).IsUnique();
            b.Property(x => x.Type).HasMaxLength(200);
        });
        modelBuilder.Entity<Snapshot>(b =>
        {
            b.ToTable("Snapshots");
            b.HasKey(x => new { x.StreamId, x.Version });
        });
    }
}
'''), encoding='utf-8')

(root/'src/Sales.Infrastructure.EFCore/EventStore/EventStoreEfCore.cs').write_text(textwrap.dedent('''
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Sales.Domain.Abstractions;
using Sales.Infrastructure.EFCore.Data;

namespace Sales.Infrastructure.EFCore.EventStore;

public sealed class DefaultEventSerializer : IEventSerializer
{
    private static readonly JsonSerializerOptions _opt = new(JsonSerializerDefaults.Web) { PropertyNameCaseInsensitive = true };
    public string Serialize(IEvent @event) => JsonSerializer.Serialize(@event, @event.GetType(), _opt);
    public IEvent Deserialize(string type, string json)
    {
        var t = Type.GetType(type, throwOnError: false) ?? AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType(type)).FirstOrDefault(t => t != null);
        if (t == null) throw new InvalidOperationException($"Unknown event type: {type}");
        return (IEvent)JsonSerializer.Deserialize(json, t, _opt)!;
    }
}

public sealed class EfCoreEventStore : IEventStore
{
    private readonly SalesDbContext _db;
    private readonly IEventSerializer _ser;
    public EfCoreEventStore(SalesDbContext db, IEventSerializer ser)
    { _db = db; _ser = ser; }

    public async Task<IReadOnlyList<EventEnvelope>> ReadStreamAsync(Guid streamId, CancellationToken ct = default)
    {
        var list = await _db.Set<StoredEvent>()
            .Where(x => x.StreamId == streamId)
            .OrderBy(x => x.Version)
            .ToListAsync(ct);

        return list.Select(e => new EventEnvelope
        {
            StreamId = e.StreamId,
            Version = e.Version,
            Type = e.Type,
            Payload = e.Payload,
            OccurredOnUtc = e.OccurredOnUtc
        }).ToList();
    }

    public async Task AppendToStreamAsync(Guid streamId, int expectedVersion, IEnumerable<IEvent> events, IDictionary<string,string>? metadata = null, CancellationToken ct = default)
    {
        // optimistic concurrency check
        var lastVersion = await _db.Set<StoredEvent>()
            .Where(x => x.StreamId == streamId)
            .Select(x => (int?)x.Version)
            .OrderByDescending(v => v)
            .FirstOrDefaultAsync(ct) ?? 0;

        if (lastVersion != expectedVersion)
            throw new DbUpdateConcurrencyException($"Expected version {expectedVersion} but found {lastVersion}");

        var version = expectedVersion;
        foreach (var ev in events)
        {
            var type = ev.GetType().FullName!;
            var payload = _ser.Serialize(ev);
            _db.Set<StoredEvent>().Add(new StoredEvent
            {
                StreamId = streamId,
                Version = ++version,
                Type = type,
                Payload = payload,
                OccurredOnUtc = DateTime.UtcNow
            });
        }
        await _db.SaveChangesAsync(ct);
    }
}
'''), encoding='utf-8')

# Extend SalesDbContext model configuration snippet (as instruction file)
(root/'src/Sales.Infrastructure.EFCore/EventStore/README-EventStore-Model.md').write_text(textwrap.dedent('''
// Tambahkan pada SalesDbContext.OnModelCreating:
// EventStoreModel.Configure(modelBuilder);
'''), encoding='utf-8')

# Projection to Mongo example (BackgroundService)
(root/'src/Sales.Infrastructure.EFCore/Projections/OrderToMongoProjector.cs').write_text(textwrap.dedent('''
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Hosting;
using MongoDB.Driver;
using Sales.Infrastructure.EFCore.Data;
using Sales.Infrastructure.EFCore.EventStore;
using Sales.Infrastructure.Mongo.Models;

namespace Sales.Infrastructure.EFCore.Projections;

public sealed class OrderToMongoProjector : BackgroundService
{
    private readonly IServiceProvider _sp;
    public OrderToMongoProjector(IServiceProvider sp) => _sp = sp;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            using var scope = _sp.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<SalesDbContext>();
            var mongo = scope.ServiceProvider.GetRequiredService<IMongoDatabase>();
            var col = mongo.GetCollection<OrderReadModel>("orders_read");

            // Sederhana: ambil event OrderCreated & OrderLineAdded terbaru dan re-build (demo)
            var streams = await db.Set<StoredEvent>()
                .Select(e => e.StreamId).Distinct()
                .ToListAsync(stoppingToken);

            foreach (var streamId in streams)
            {
                var events = await db.Set<StoredEvent>()
                    .Where(e => e.StreamId == streamId)
                    .OrderBy(e => e.Version)
                    .ToListAsync(stoppingToken);

                // Compute projection (naive)
                Guid customerId = Guid.Empty; decimal total = 0; string currency = "USD"; int lines = 0;
                foreach (var e in events)
                {
                    if (e.Type.EndsWith("OrderCreated"))
                    {
                        var doc = System.Text.Json.JsonDocument.Parse(e.Payload);
                        customerId = doc.RootElement.GetProperty("CustomerId").GetGuid();
                    }
                    else if (e.Type.EndsWith("OrderLineAdded"))
                    {
                        var doc = System.Text.Json.JsonDocument.Parse(e.Payload);
                        var qty = doc.RootElement.GetProperty("Quantity").GetInt32();
                        var price = doc.RootElement.GetProperty("UnitPrice").GetDecimal();
                        currency = doc.RootElement.GetProperty("Currency").GetString() ?? "USD";
                        total += qty * price; lines++;
                    }
                }
                await col.ReplaceOneAsync(x => x.Id == streamId, new OrderReadModel
                {
                    Id = streamId,
                    CustomerId = customerId,
                    TotalAmount = total,
                    Currency = currency,
                    Lines = lines
                }, new ReplaceOptions { IsUpsert = true }, stoppingToken);
            }

            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
        }
    }
}
'''), encoding='utf-8')

# ES repository for Order using EventStore
(root/'src/Sales.Infrastructure.EFCore/EventStore/EventSourcedOrderRepository.cs').write_text(textwrap.dedent('''
using Sales.Domain.Orders;
using Sales.Domain.Abstractions;

namespace Sales.Infrastructure.EFCore.EventStore;

public sealed class EventSourcedOrderRepository : IOrderRepository
{
    private readonly IEventStore _store;
    private readonly IEventSerializer _ser; // not strictly needed here but could be useful
    public EventSourcedOrderRepository(IEventStore store, IEventSerializer ser) { _store = store; _ser = ser; }

    public async Task AddAsync(Order order, CancellationToken ct = default)
    {
        // adapter: build OrderEs and persist events
        var es = OrderEs.Create(order.CustomerId);
        foreach (var l in order.Lines)
            es.AddLine(l.ProductId, l.Quantity, l.Price);

        await _store.AppendToStreamAsync(es.Id, 0, es.GetUncommittedEvents(), null, ct);
        es.ClearUncommittedEvents();
    }

    public async Task<Order?> GetAsync(OrderId id, CancellationToken ct = default)
    {
        var envs = await _store.ReadStreamAsync(id.Value, ct);
        if (envs.Count == 0) return null;
        var es = new OrderEs();
        var events = envs.Select(e => _ser.Deserialize(e.Type, e.Payload));
        es.LoadFromHistory(events);

        // map ES aggregate to traditional Order entity (demo; in real, you may unify the model)
        var ord = typeof(Order).GetConstructor(System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance,
            binder: null, new Type[] { typeof(OrderId), typeof(CustomerId) }, modifiers: null)!
            .Invoke(new object[] { new OrderId(es.Id), es.CustomerId }) as Order;

        // reflect lines and total into Order via public methods (simplified):
        foreach (var line in es.Lines) ord!.AddLine(line.ProductId, line.Quantity, line.Price);
        return ord;
    }

    public async Task UpdateAsync(Order order, CancellationToken ct = default)
    {
        // In ES, updates are additional events. Build ES and append new lines compared to history (naive demo)
        var envs = await _store.ReadStreamAsync(order.Id.Value, ct);
        var ser = _ser;
        var current = new OrderEs(); current.LoadFromHistory(envs.Select(e => ser.Deserialize(e.Type, e.Payload)));

        var pending = new List<IEvent>();
        if (order.Lines.Count > current.Lines.Count)
        {
            foreach (var extra in order.Lines.Skip(current.Lines.Count))
                pending.Add(new OrderLineAdded(order.Id.Value, extra.ProductId.Value, extra.Quantity, extra.Price.Amount, extra.Price.Currency));
        }
        if (pending.Count > 0)
            await _store.AppendToStreamAsync(order.Id.Value, envs.Count, pending, null, ct);
    }
}
'''), encoding='utf-8')

# Web API controller for event history
(root/'src/Sales.WebApi/Controllers/OrderEventsController.cs').write_text(textwrap.dedent('''
using Microsoft.AspNetCore.Mvc;
using Sales.Domain.Abstractions;

namespace Sales.WebApi.Controllers;

[ApiController]
[Route("api/orders/{id:guid}/events")]
public class OrderEventsController : ControllerBase
{
    private readonly IEventStore _store;
    public OrderEventsController(IEventStore store) => _store = store;

    [HttpGet]
    public async Task<IActionResult> Get(Guid id, CancellationToken ct)
    {
        var stream = await _store.ReadStreamAsync(id, ct);
        return stream.Count == 0 ? NotFound() : Ok(stream);
    }
}
'''), encoding='utf-8')

# Registration snippet for Program.cs
(root/'src/Sales.WebApi/README-EventSourcing-Setup.md').write_text(textwrap.dedent('''
// appsettings.json
// "EventSourcing": { "Enabled": true }

// Program.cs
// if (builder.Configuration.GetSection("EventSourcing").GetValue<bool>("Enabled"))
// {
//   // add event store model to DbContext.OnModelCreating: EventStoreModel.Configure(modelBuilder)
//   builder.Services.AddScoped<IEventSerializer, DefaultEventSerializer>();
//   builder.Services.AddScoped<IEventStore, EfCoreEventStore>();
//   builder.Services.AddScoped<IOrderRepository, EventSourcedOrderRepository>();
//   builder.Services.AddHostedService<OrderToMongoProjector>();
// }
'''), encoding='utf-8')

# Zip it
zip_path = '/mnt/data/event-sourcing-addon.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            ap = Path(dirpath)/fn
            z.write(ap, ap.relative_to(root))

zip_path


<m-result-block>
Status: Success

Result: /mnt/data/event-sourcing-addon.zip
</m-result-block>

Siap! Kita tambahkan **Event Sourcing (opsional)** untuk **histori perubahan** tanpa mengganggu arsitektur yang sudah ada. Add-on ini menyertakan **Event Store berbasis EF Core** (append-only), **aggregate event-sourced** alternatif (`OrderEs`), **serializer**, **projector ke Mongo** (untuk read model), **endpoint histori event**, dan **toggle konfigurasi** sehingga Anda bisa ON/OFF sesuai kebutuhan.

---

## 🔧 Paket Add-on (siap gabung ke template Anda)

**⬇️ Unduh add-on Event Sourcing:**
[event-sourcing-addon.zip](blob:https://m365.cloud.microsoft/8f8efe61-e41e-4a9c-9842-4e803b27c4f3)

**Isi utama:**
```
src/
  Sales.Domain/
    Abstractions/
      EventSourcing.cs         # IEvent, IEventStore, EventEnvelope, EventSourcedAggregate
  Sales.Domain/Orders/
      Order.Events.cs          # OrderCreated, OrderLineAdded (IEvent)
      Order.EventSourced.cs    # OrderEs (aggregate event-sourced)
  Sales.Infrastructure.EFCore/
    EventStore/
      EventEntities.cs         # StoredEvent, Snapshot, EventStoreModel.Configure()
      EventStoreEfCore.cs      # EfCoreEventStore, DefaultEventSerializer
      EventSourcedOrderRepository.cs
    Projections/
      OrderToMongoProjector.cs # BackgroundService projector -> Mongo read model
  Sales.WebApi/
    Controllers/
      OrderEventsController.cs # GET /api/orders/{id}/events
    README-EventSourcing-Setup.md  # snippet setup
```

---

## 🧠 Konsep Inti

- **Event Store (EF Core)**: Tabel `Events` (append-only) menyimpan `StreamId`, `Version`, `Type`, `Payload JSON`, `OccurredOnUtc`. Tabel `Snapshots` (opsional) untuk rekonstruksi cepat.
- **Aggregate Event-Sourced (`OrderEs`)**: State dibangun melalui `Apply(…)` → `When(…)`. Aksi domain menghasilkan event: `OrderCreated`, `OrderLineAdded`.
- **Optimistic Concurrency**: `expectedVersion` dicek sebelum append; bila mismatch, `DbUpdateConcurrencyException`.
- **Proyeksi ke Mongo**: Proses latar (`BackgroundService`) membaca event dan membangun dokumen `OrderReadModel` (CQRS read).
- **Endpoint Histori**: `GET /api/orders/{id}/events` untuk audit trail.

> **Opsional**: Anda bisa gunakan **EventSourcedOrderRepository** menggantikan repo relasional jika `EventSourcing.Enabled=true`. Jika `false`, aplikasi tetap berjalan seperti sebelumnya (relasional murni + Outbox).

---

## 🧩 Kode Penting (ringkas & dapat langsung dipakai)

### 1) Abstraksi Event Sourcing (Domain)
```csharp
// Sales.Domain/Abstractions/EventSourcing.cs
public interface IEvent { }

public sealed class EventEnvelope
{
    public Guid StreamId { get; init; }
    public int Version { get; init; }
    public string Type { get; init; } = default!;
    public string Payload { get; init; } = default!;
    public DateTime OccurredOnUtc { get; init; }
    public IDictionary<string,string>? Metadata { get; init; }
}

public interface IEventSerializer
{
    string Serialize(IEvent @event);
    IEvent Deserialize(string type, string json);
}

public interface IEventStore
{
    Task<IReadOnlyList<EventEnvelope>> ReadStreamAsync(Guid streamId, CancellationToken ct = default);
    Task AppendToStreamAsync(Guid streamId, int expectedVersion, IEnumerable<IEvent> events,
                             IDictionary<string,string>? metadata = null, CancellationToken ct = default);
}

public abstract class EventSourcedAggregate
{
    private readonly List<IEvent> _uncommitted = new();
    public Guid Id { get; protected set; }
    public int Version { get; protected set; } = 0;
    public IReadOnlyList<IEvent> GetUncommittedEvents() => _uncommitted.AsReadOnly();
    public void ClearUncommittedEvents() => _uncommitted.Clear();

    protected void Apply(IEvent @event) { When(@event); _uncommitted.Add(@event); Version++; }
    protected abstract void When(IEvent @event);

    public void LoadFromHistory(IEnumerable<IEvent> history)
    { foreach (var e in history) { When(e); Version++; } _uncommitted.Clear(); }
}
```

### 2) Event Domain & Aggregate Event-Sourced
```csharp
// Sales.Domain/Orders/Order.Events.cs
public sealed record OrderCreated(Guid OrderId, Guid CustomerId, DateTime CreatedAtUtc) : IEvent;
public sealed record OrderLineAdded(Guid OrderId, Guid ProductId, int Quantity, decimal UnitPrice, string Currency) : IEvent;

// Sales.Domain/Orders/Order.EventSourced.cs
public sealed class OrderEs : EventSourcedAggregate
{
    private readonly List<OrderLine> _lines = new();
    public CustomerId CustomerId { get; private set; }
    public IReadOnlyCollection<OrderLine> Lines => _lines.AsReadOnly();
    public Money Total { get; private set; } = Money.Zero("USD");
    public DateTime CreatedAt { get; private set; }

    public static OrderEs Create(CustomerId customerId)
    { if (customerId == default) throw new DomainException("Customer is required");
      var agg = new OrderEs(); agg.Apply(new OrderCreated(Guid.NewGuid(), customerId.Value, DateTime.UtcNow)); return agg; }

    public void AddLine(ProductId productId, int quantity, Money price)
    { if (quantity <= 0) throw new DomainException("Quantity must be > 0");
      Apply(new OrderLineAdded(Id, productId.Value, quantity, price.Amount, price.Currency)); }

    protected override void When(IEvent @event)
    {
        switch (@event)
        {
            case OrderCreated e:
                Id = e.OrderId; CustomerId = new CustomerId(e.CustomerId); CreatedAt = e.CreatedAtUtc; Total = Money.Zero("USD"); break;
            case OrderLineAdded e:
                _lines.Add(new OrderLine(new ProductId(e.ProductId), e.Quantity, new Money(e.UnitPrice, e.Currency)));
                Total = _lines.Select(l => new Money(l.Price.Amount * l.Quantity, l.Price.Currency))
                              .Aggregate(Money.Zero("USD"), (acc, m) => acc.Add(m));
                break;
        }
    }
}
```

### 3) Event Store via EF Core
```csharp
// Sales.Infrastructure.EFCore/EventStore/EventEntities.cs
public sealed class StoredEvent
{
    public long Sequence { get; set; }       // PK auto-increment
    public Guid StreamId { get; set; }
    public int Version { get; set; }         // expectedVersion + 1..n
    public string Type { get; set; } = default!;
    public string Payload { get; set; } = default!;
    public DateTime OccurredOnUtc { get; set; }
}
public static class EventStoreModel
{
    public static void Configure(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<StoredEvent>(b =>
        {
            b.ToTable("Events"); b.HasKey(x => x.Sequence);
            b.HasIndex(x => new { x.StreamId, x.Version }).IsUnique();
            b.Property(x => x.Type).HasMaxLength(200);
        });
    }
}
```

```csharp
// Sales.Infrastructure.EFCore/EventStore/EventStoreEfCore.cs
public sealed class DefaultEventSerializer : IEventSerializer { /* System.Text.Json */ }

public sealed class EfCoreEventStore : IEventStore
{
    private readonly SalesDbContext _db; private readonly IEventSerializer _ser;
    public EfCoreEventStore(SalesDbContext db, IEventSerializer ser) { _db = db; _ser = ser; }

    public async Task<IReadOnlyList<EventEnvelope>> ReadStreamAsync(Guid streamId, CancellationToken ct = default)
    {
        var list = await _db.Set<StoredEvent>().Where(x => x.StreamId == streamId).OrderBy(x => x.Version).ToListAsync(ct);
        return list.Select(e => new EventEnvelope { StreamId = e.StreamId, Version = e.Version, Type = e.Type, Payload = e.Payload, OccurredOnUtc = e.OccurredOnUtc }).ToList();
    }

    public async Task AppendToStreamAsync(Guid streamId, int expectedVersion, IEnumerable<IEvent> events, IDictionary<string,string>? metadata = null, CancellationToken ct = default)
    {
        var lastVersion = await _db.Set<StoredEvent>().Where(x => x.StreamId == streamId)
                            .Select(x => (int?)x.Version).OrderByDescending(v => v).FirstOrDefaultAsync(ct) ?? 0;
        if (lastVersion != expectedVersion)
            throw new DbUpdateConcurrencyException($"Expected version {expectedVersion} but found {lastVersion}");

        var version = expectedVersion;
        foreach (var ev in events)
            _db.Set<StoredEvent>().Add(new StoredEvent {
                StreamId = streamId, Version = ++version, Type = ev.GetType().FullName!, Payload = _ser.Serialize(ev), OccurredOnUtc = DateTime.UtcNow
            });

        await _db.SaveChangesAsync(ct);
    }
}
```

### 4) Repository Event-Sourced (drop-in untuk `IOrderRepository`)
```csharp
public sealed class EventSourcedOrderRepository : IOrderRepository
{
    private readonly IEventStore _store; private readonly IEventSerializer _ser;
    public EventSourcedOrderRepository(IEventStore store, IEventSerializer ser) { _store = store; _ser = ser; }

    public async Task AddAsync(Order order, CancellationToken ct = default)
    {
        var es = OrderEs.Create(order.CustomerId);
        foreach (var l in order.Lines) es.AddLine(l.ProductId, l.Quantity, l.Price);
        await _store.AppendToStreamAsync(es.Id, 0, es.GetUncommittedEvents(), null, ct);
        es.ClearUncommittedEvents();
    }

    public async Task<Order?> GetAsync(OrderId id, CancellationToken ct = default)
    {
        var envs = await _store.ReadStreamAsync(id.Value, ct);
        if (envs.Count == 0) return null;
        var es = new OrderEs(); es.LoadFromHistory(envs.Select(e => _ser.Deserialize(e.Type, e.Payload)));
        // mapping sederhana kembali ke Order relasional agar kompatibel dengan use case yang ada
        var ord = typeof(Order).GetConstructor(System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance,
                    null, new[] { typeof(OrderId), typeof(CustomerId) }, null)!
                    .Invoke(new object[] { new OrderId(es.Id), es.CustomerId }) as Order;
        foreach (var line in es.Lines) ord!.AddLine(line.ProductId, line.Quantity, line.Price);
        return ord;
    }

    public async Task UpdateAsync(Order order, CancellationToken ct = default)
    {
        var envs = await _store.ReadStreamAsync(order.Id.Value, ct);
        var current = new OrderEs(); current.LoadFromHistory(envs.Select(e => _ser.Deserialize(e.Type, e.Payload)));
        var pending = new List<IEvent>();
        if (order.Lines.Count > current.Lines.Count)
            foreach (var extra in order.Lines.Skip(current.Lines.Count))
                pending.Add(new OrderLineAdded(order.Id.Value, extra.ProductId.Value, extra.Quantity, extra.Price.Amount, extra.Price.Currency));

        if (pending.Count > 0)
            await _store.AppendToStreamAsync(order.Id.Value, envs.Count, pending, null, ct);
    }
}
```

### 5) Proyeksi ke Mongo (BackgroundService)
```csharp
public sealed class OrderToMongoProjector : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // Loop sederhana: rebuild tiap 5 detik (untuk demo). Produksi: checkpoint & idempotensi.
    }
}
```
> **Best Practice produksi**: gunakan **checkpoint** (tabel `Checkpoints`), **idempotensi**, **batching**, dan **replay** yang efisien. Projector di contoh ini **naif** agar mudah dipahami dulu.

### 6) Endpoint Histori Event
```csharp
[ApiController]
[Route("api/orders/{id:guid}/events")]
public class OrderEventsController : ControllerBase
{
    private readonly IEventStore _store;
    public OrderEventsController(IEventStore store) => _store = store;

    [HttpGet]
    public async Task<IActionResult> Get(Guid id, CancellationToken ct)
    {
        var stream = await _store.ReadStreamAsync(id, ct);
        return stream.Count == 0 ? NotFound() : Ok(stream);
    }
}
```

---

## ⚙️ Integrasi ke Template Anda

1. **Tambahkan konfigurasi**:
   ```json
   "EventSourcing": { "Enabled": true }
   ```
2. **Modifikasi `SalesDbContext.OnModelCreating`**:
   ```csharp
   // SalesDbContext.OnModelCreating(...)
   EventStoreModel.Configure(modelBuilder);
   ```
3. **Registrasi DI di `Program.cs`** (conditonal):
   ```csharp
   if (builder.Configuration.GetSection("EventSourcing").GetValue<bool>("Enabled"))
   {
       builder.Services.AddScoped<IEventSerializer, DefaultEventSerializer>();
       builder.Services.AddScoped<IEventStore, EfCoreEventStore>();
       builder.Services.AddScoped<IOrderRepository, EventSourcedOrderRepository>();
       builder.Services.AddHostedService<OrderToMongoProjector>();
   }
   ```
4. **Migrations**: buat migrasi untuk tabel `Events` (dan `Snapshots` bila dipakai).

---

## 📝 Catatan Desain & Trade-off

- **Kelebihan**: histori perubahan lengkap, audit trail, kemampuan **time-travel**, proyeksi read model fleksibel, performa write tinggi (append-only).
- **Konsekuensi**: kompleksitas lebih tinggi (rebuild aggregate, projector, checkpoint), perlu **kontrak event stabil**, **versioning event**, dan strategi **snapshot** untuk stream panjang.

---
