
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
