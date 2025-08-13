
using Microsoft.EntityFrameworkCore;
using Sales.Domain.Orders;
using Sales.Domain.ValueObjects;

namespace Sales.Infrastructure.EFCore.Data;

public sealed class SalesDbContext : DbContext
{
    public DbSet<Order> Orders => Set<Order>();
    public SalesDbContext(DbContextOptions<SalesDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Order>(b =>
        {
            b.HasKey(o => o.Id);
            b.Property(o => o.Id).HasConversion(id => id.Value, v => new OrderId(v));
            b.Property(o => o.CustomerId).HasConversion(id => id.Value, v => new CustomerId(v));

            b.OwnsMany(typeof(OrderLine), "_lines", lb =>
            {
                lb.WithOwner().HasForeignKey("OrderId");
                lb.Property<ProductId>("ProductId").HasConversion(id => id.Value, v => new ProductId(v));
                lb.Property<int>("Quantity");
                lb.OwnsOne(typeof(Money), "Price", mb =>
                {
                    mb.Property<decimal>("Amount");
                    mb.Property<string>("Currency").HasMaxLength(3);
                });
                lb.ToTable("OrderLines");
            });

            b.OwnsOne(o => o.Total, mb =>
            {
                mb.Property(m => m.Amount).HasColumnName("TotalAmount");
                mb.Property(m => m.Currency).HasColumnName("TotalCurrency").HasMaxLength(3);
            });

            b.Ignore(o => o.DomainEvents);
            b.ToTable("Orders");
        });
    }
}
