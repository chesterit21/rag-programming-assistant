
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
