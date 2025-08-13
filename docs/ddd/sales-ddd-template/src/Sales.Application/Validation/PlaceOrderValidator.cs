
using Sales.Domain.Abstractions;
using static System.String;

namespace Sales.Application.Validation;

using Cmd = Sales.Application.Orders.PlaceOrder.Command;
using Line = Sales.Application.Orders.PlaceOrder.LineDto;

public sealed class PlaceOrderValidator : IValidator<Cmd>
{
    public ValidationResult Validate(Cmd instance)
    {
        var vr = new ValidationResult();
        if (instance.CustomerId == Guid.Empty)
            vr.Add("CustomerId", "CustomerId is required");

        if (instance.Lines is null || instance.Lines.Count == 0)
            vr.Add("Lines", "At least one line is required");
        else
            vr.AddRange(ValidateList(instance.Lines, "Lines", ValidateLine));

        return vr;
    }

    private static IEnumerable<ValidationError> ValidateLine(Line line, string path)
    {
        if (line.ProductId == Guid.Empty) yield return new ValidationError($"{path}.ProductId", "ProductId is required");
        if (line.Quantity <= 0) yield return new ValidationError($"{path}.Quantity", "Quantity must be > 0");
        if (line.Price <= 0) yield return new ValidationError($"{path}.Price", "Price must be > 0");
        if (IsNullOrWhiteSpace(line.Currency)) yield return new ValidationError($"{path}.Currency", "Currency is required");
    }

    public static IEnumerable<ValidationError> ValidateList<T>(IReadOnlyList<T> items, string basePath, Func<T,string,IEnumerable<ValidationError>> validator)
    {
        for (int i = 0; i < items.Count; i++)
        {
            var path = $"{basePath}[{i}]";
            foreach (var err in validator(items[i], path))
                yield return err;
        }
    }
}
