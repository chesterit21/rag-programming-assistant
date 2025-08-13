
using Sales.Domain.Abstractions;
using Sales.Domain.ValueObjects;

namespace Sales.Domain.Orders;

public sealed record OrderCreated(Guid OrderId, Guid CustomerId, DateTime CreatedAtUtc) : IEvent;
public sealed record OrderLineAdded(Guid OrderId, Guid ProductId, int Quantity, decimal UnitPrice, string Currency) : IEvent;
