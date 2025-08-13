
using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Sales.Domain.Abstractions;
using Sales.Infrastructure.EFCore.Data;

namespace Sales.Infrastructure.EFCore.EventStore;

public sealed class DefaultEventSerializer : IEventSerializer
{
    private static readonly JsonSerializerOptions _opt = new(JsonSerializerDefaults.Web) { PropertyNameCaseInsensitive = true };
    public string Serialize(IEvent @event) => JsonSerializer.Serialize(@event, @event.GetType(), _opt);
    public IEvent Deserialize(string type, string json)
    {
        var t = Type.GetType(type, throwOnError: false) ?? AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType(type)).FirstOrDefault(t => t != null);
        if (t == null) throw new InvalidOperationException($"Unknown event type: {type}");
        return (IEvent)JsonSerializer.Deserialize(json, t, _opt)!;
    }
}

public sealed class EfCoreEventStore : IEventStore
{
    private readonly SalesDbContext _db;
    private readonly IEventSerializer _ser;
    public EfCoreEventStore(SalesDbContext db, IEventSerializer ser)
    { _db = db; _ser = ser; }

    public async Task<IReadOnlyList<EventEnvelope>> ReadStreamAsync(Guid streamId, CancellationToken ct = default)
    {
        var list = await _db.Set<StoredEvent>()
            .Where(x => x.StreamId == streamId)
            .OrderBy(x => x.Version)
            .ToListAsync(ct);

        return list.Select(e => new EventEnvelope
        {
            StreamId = e.StreamId,
            Version = e.Version,
            Type = e.Type,
            Payload = e.Payload,
            OccurredOnUtc = e.OccurredOnUtc
        }).ToList();
    }

    public async Task AppendToStreamAsync(Guid streamId, int expectedVersion, IEnumerable<IEvent> events, IDictionary<string,string>? metadata = null, CancellationToken ct = default)
    {
        // optimistic concurrency check
        var lastVersion = await _db.Set<StoredEvent>()
            .Where(x => x.StreamId == streamId)
            .Select(x => (int?)x.Version)
            .OrderByDescending(v => v)
            .FirstOrDefaultAsync(ct) ?? 0;

        if (lastVersion != expectedVersion)
            throw new DbUpdateConcurrencyException($"Expected version {expectedVersion} but found {lastVersion}");

        var version = expectedVersion;
        foreach (var ev in events)
        {
            var type = ev.GetType().FullName!;
            var payload = _ser.Serialize(ev);
            _db.Set<StoredEvent>().Add(new StoredEvent
            {
                StreamId = streamId,
                Version = ++version,
                Type = type,
                Payload = payload,
                OccurredOnUtc = DateTime.UtcNow
            });
        }
        await _db.SaveChangesAsync(ct);
    }
}
