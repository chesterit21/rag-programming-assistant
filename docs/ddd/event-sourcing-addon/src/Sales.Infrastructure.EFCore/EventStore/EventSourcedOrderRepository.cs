
using Sales.Domain.Orders;
using Sales.Domain.Abstractions;

namespace Sales.Infrastructure.EFCore.EventStore;

public sealed class EventSourcedOrderRepository : IOrderRepository
{
    private readonly IEventStore _store;
    private readonly IEventSerializer _ser; // not strictly needed here but could be useful
    public EventSourcedOrderRepository(IEventStore store, IEventSerializer ser) { _store = store; _ser = ser; }

    public async Task AddAsync(Order order, CancellationToken ct = default)
    {
        // adapter: build OrderEs and persist events
        var es = OrderEs.Create(order.CustomerId);
        foreach (var l in order.Lines)
            es.AddLine(l.ProductId, l.Quantity, l.Price);

        await _store.AppendToStreamAsync(es.Id, 0, es.GetUncommittedEvents(), null, ct);
        es.ClearUncommittedEvents();
    }

    public async Task<Order?> GetAsync(OrderId id, CancellationToken ct = default)
    {
        var envs = await _store.ReadStreamAsync(id.Value, ct);
        if (envs.Count == 0) return null;
        var es = new OrderEs();
        var events = envs.Select(e => _ser.Deserialize(e.Type, e.Payload));
        es.LoadFromHistory(events);

        // map ES aggregate to traditional Order entity (demo; in real, you may unify the model)
        var ord = typeof(Order).GetConstructor(System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance,
            binder: null, new Type[] { typeof(OrderId), typeof(CustomerId) }, modifiers: null)!
            .Invoke(new object[] { new OrderId(es.Id), es.CustomerId }) as Order;

        // reflect lines and total into Order via public methods (simplified):
        foreach (var line in es.Lines) ord!.AddLine(line.ProductId, line.Quantity, line.Price);
        return ord;
    }

    public async Task UpdateAsync(Order order, CancellationToken ct = default)
    {
        // In ES, updates are additional events. Build ES and append new lines compared to history (naive demo)
        var envs = await _store.ReadStreamAsync(order.Id.Value, ct);
        var ser = _ser;
        var current = new OrderEs(); current.LoadFromHistory(envs.Select(e => ser.Deserialize(e.Type, e.Payload)));

        var pending = new List<IEvent>();
        if (order.Lines.Count > current.Lines.Count)
        {
            foreach (var extra in order.Lines.Skip(current.Lines.Count))
                pending.Add(new OrderLineAdded(order.Id.Value, extra.ProductId.Value, extra.Quantity, extra.Price.Amount, extra.Price.Currency));
        }
        if (pending.Count > 0)
            await _store.AppendToStreamAsync(order.Id.Value, envs.Count, pending, null, ct);
    }
}
