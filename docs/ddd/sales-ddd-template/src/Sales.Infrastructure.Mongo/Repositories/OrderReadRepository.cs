
using MongoDB.Driver;
using Sales.Infrastructure.Mongo.Models;

namespace Sales.Infrastructure.Mongo.Repositories;

public interface IOrderReadRepository
{
    Task<OrderReadModel?> GetAsync(Guid id, CancellationToken ct = default);
}

public sealed class OrderReadRepository : IOrderReadRepository
{
    private readonly IMongoCollection<OrderReadModel> _col;
    public OrderReadRepository(IMongoDatabase db)
        => _col = db.GetCollection<OrderReadModel>("orders_read");

    public async Task<OrderReadModel?> GetAsync(Guid id, CancellationToken ct = default)
        => await _col.Find(x => x.Id == id).FirstOrDefaultAsync(ct);
}
