
using Microsoft.EntityFrameworkCore;
using Sales.Domain.Orders;
using Sales.Infrastructure.EFCore.Data;

namespace Sales.Infrastructure.EFCore.Repositories;

public sealed class OrderRepository : IOrderRepository
{
    private readonly SalesDbContext _db;
    public OrderRepository(SalesDbContext db) => _db = db;

    public async Task AddAsync(Order order, CancellationToken ct = default)
        => await _db.Orders.AddAsync(order, ct);

    public async Task<Order?> GetAsync(OrderId id, CancellationToken ct = default)
        => await _db.Orders.Include("_lines").FirstOrDefaultAsync(o => o.Id == id, ct);

    public Task UpdateAsync(Order order, CancellationToken ct = default)
    { _db.Orders.Update(order); return Task.CompletedTask; }
}
