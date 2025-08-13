
namespace Sales.Domain.Abstractions;

public interface IEvent { }

public sealed class EventEnvelope
{
    public Guid StreamId { get; init; }
    public int Version { get; init; }
    public string Type { get; init; } = default!;
    public string Payload { get; init; } = default!; // JSON
    public DateTime OccurredOnUtc { get; init; }
    public IDictionary<string, string>? Metadata { get; init; }
}

public interface IEventSerializer
{
    string Serialize(IEvent @event);
    IEvent Deserialize(string type, string json);
}

public interface IEventStore
{
    Task<IReadOnlyList<EventEnvelope>> ReadStreamAsync(Guid streamId, CancellationToken ct = default);
    Task AppendToStreamAsync(Guid streamId, int expectedVersion, IEnumerable<IEvent> events, IDictionary<string,string>? metadata = null, CancellationToken ct = default);
}

public abstract class EventSourcedAggregate
{
    private readonly List<IEvent> _uncommitted = new();
    public Guid Id { get; protected set; }
    public int Version { get; protected set; } = 0;
    public IReadOnlyList<IEvent> GetUncommittedEvents() => _uncommitted.AsReadOnly();
    public void ClearUncommittedEvents() => _uncommitted.Clear();

    protected void Apply(IEvent @event)
    {
        When(@event);
        _uncommitted.Add(@event);
        Version++;
    }

    protected abstract void When(IEvent @event);

    public void LoadFromHistory(IEnumerable<IEvent> history)
    {
        foreach (var e in history)
        {
            When(e);
            Version++;
        }
        _uncommitted.Clear();
    }
}
