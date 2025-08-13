
using Sales.Domain.ValueObjects;

namespace Sales.Domain.Orders;

public sealed class Order
{
    private readonly List<OrderLine> _lines = new();
    private readonly List<IDomainEvent> _domainEvents = new();

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
        _lines.Add(new OrderLine(productId, quantity, price));
        RecalculateTotal();
    }

    private void RecalculateTotal()
    {
        Total = _lines
            .Select(l => new Money(l.Price.Amount * l.Quantity, l.Price.Currency))
            .Aggregate(Money.Zero("USD"), (acc, m) => acc.Add(m));
    }

    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();
    private void Raise(IDomainEvent @event) => _domainEvents.Add(@event);
}

public sealed record OrderId(Guid Value) { public static OrderId New() => new(Guid.NewGuid()); }
public sealed record CustomerId(Guid Value) { public static CustomerId New() => new(Guid.NewGuid()); }

public sealed class OrderLine
{
    public ProductId ProductId { get; }
    public int Quantity { get; }
    public Money Price { get; }
    public OrderLine(ProductId productId, int quantity, Money price) { ProductId = productId; Quantity = quantity; Price = price; }
}

public sealed record ProductId(Guid Value) { public static ProductId New() => new(Guid.NewGuid()); }

public interface IDomainEvent { }
public sealed record OrderCreatedDomainEvent(Guid OrderId) : IDomainEvent;

public sealed class DomainException : Exception { public DomainException(string message) : base(message) { } }
