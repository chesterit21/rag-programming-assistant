
namespace Sales.Domain.Abstractions;

public sealed record ValidationError(string Path, string Message);

public sealed class ValidationResult
{
    public bool IsValid => Errors.Count == 0;
    public List<ValidationError> Errors { get; } = new();
    public void Add(string path, string message) => Errors.Add(new ValidationError(path, message));
    public void AddRange(IEnumerable<ValidationError> errors) => Errors.AddRange(errors);
}

public interface IValidator<T>
{
    ValidationResult Validate(T instance);
}

public sealed class ValidationException : Exception
{
    public IReadOnlyCollection<ValidationError> Errors { get; }
    public ValidationException(IEnumerable<ValidationError> errors)
        : base("Validation failed") => Errors = errors.ToList().AsReadOnly();
}
