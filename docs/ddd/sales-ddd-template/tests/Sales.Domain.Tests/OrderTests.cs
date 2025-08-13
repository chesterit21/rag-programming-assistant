
using Sales.Domain.Orders;
using Sales.Domain.ValueObjects;
using Xunit;

namespace Sales.Domain.Tests;

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
