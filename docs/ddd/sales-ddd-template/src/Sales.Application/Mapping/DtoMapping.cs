
using Sales.Domain.Orders;

namespace Sales.Application.Mapping;

public readonly record struct OrderSummaryDto(Guid OrderId, Guid CustomerId, decimal Total, string Currency, int Lines);

public static class DtoMappings
{
    public static OrderSummaryDto ToDto(this Order order)
        => new(order.Id.Value, order.CustomerId.Value, order.Total.Amount, order.Total.Currency, order.Lines.Count);
}
