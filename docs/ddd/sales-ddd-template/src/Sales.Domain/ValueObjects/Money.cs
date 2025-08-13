
namespace Sales.Domain.ValueObjects;

public sealed record Money(decimal Amount, string Currency)
{
    public static Money Zero(string currency) => new(0m, currency);
    public Money Add(Money other)
    {
        if (Currency != other.Currency) throw new DomainException("Currency mismatch");
        return this with { Amount = Amount + other.Amount };
    }
}
