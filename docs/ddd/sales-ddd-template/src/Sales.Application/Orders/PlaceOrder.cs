
using Sales.Domain.Abstractions;
using Sales.Domain.Orders;
using Sales.Domain.ValueObjects;
using Sales.Application.Validation;

namespace Sales.Application.Orders;

public sealed class PlaceOrder
{
    public sealed record LineDto(Guid ProductId, int Quantity, decimal Price, string Currency);
    public sealed record Command(Guid CustomerId, IReadOnlyList<LineDto> Lines);
    public sealed record Result(Guid OrderId, decimal TotalAmount, string Currency);

    private readonly IOrderRepository _repo; private readonly IUnitOfWork _uow; private readonly IValidator<Command> _validator;

    public PlaceOrder(IOrderRepository repo, IUnitOfWork uow, IValidator<Command> validator)
    { _repo = repo; _uow = uow; _validator = validator; }

    public async Task<Result> Handle(Command cmd, CancellationToken ct)
    {
        var vr = _validator.Validate(cmd); if (!vr.IsValid) throw new ValidationException(vr.Errors);

        var order = Order.Create(new CustomerId(cmd.CustomerId));
        foreach (var l in cmd.Lines)
            order.AddLine(new ProductId(l.ProductId), l.Quantity, new Money(l.Price, l.Currency));

        await _repo.AddAsync(order, ct);
        await _uow.SaveChangesAsync(ct);
        return new Result(order.Id.Value, order.Total.Amount, order.Total.Currency);
    }
}
