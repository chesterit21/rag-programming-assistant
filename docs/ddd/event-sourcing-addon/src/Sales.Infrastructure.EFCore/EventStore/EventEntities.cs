
using Microsoft.EntityFrameworkCore;

namespace Sales.Infrastructure.EFCore.EventStore;

public sealed class StoredEvent
{
    public long   Sequence       { get; set; }  // auto-increment
    public Guid   StreamId       { get; set; }
    public int    Version        { get; set; }
    public string Type           { get; set; } = default!;
    public string Payload        { get; set; } = default!;
    public DateTime OccurredOnUtc{ get; set; }
}

public sealed class Snapshot
{
    public Guid StreamId { get; set; }
    public int  Version  { get; set; }
    public string Payload { get; set; } = default!;
    public DateTime CreatedOnUtc { get; set; }
}

public static class EventStoreModel
{
    public static void Configure(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<StoredEvent>(b =>
        {
            b.ToTable("Events");
            b.HasKey(x => x.Sequence);
            b.HasIndex(x => new { x.StreamId, x.Version }).IsUnique();
            b.Property(x => x.Type).HasMaxLength(200);
        });
        modelBuilder.Entity<Snapshot>(b =>
        {
            b.ToTable("Snapshots");
            b.HasKey(x => new { x.StreamId, x.Version });
        });
    }
}
