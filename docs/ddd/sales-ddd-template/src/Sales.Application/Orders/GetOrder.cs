
using Sales.Domain.Orders;
using Sales.Application.Mapping;

namespace Sales.Application.Orders;

public sealed class GetOrder
{
    public sealed record Query(Guid OrderId);
    public readonly record struct Dto(Guid OrderId, Guid CustomerId, decimal Total, string Currency, int Lines);

    private readonly IOrderRepository _repo;
    public GetOrder(IOrderRepository repo) => _repo = repo;

    public async Task<Dto?> Handle(Query q, CancellationToken ct)
    {
        var order = await _repo.GetAsync(new OrderId(q.OrderId), ct);
        return order?.ToDto();
    }
}
