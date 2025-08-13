
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Sales.Infrastructure.EFCore.Data;

namespace Sales.Infrastructure.EFCore.Provider;

public static class DbProvider
{
    public static IServiceCollection AddSalesDbContext(this IServiceCollection services, IConfiguration cfg)
    {
        var provider = cfg["Database:Provider"]?.ToLowerInvariant() ?? "postgres";
        services.AddDbContext<SalesDbContext>(opt =>
        {
            switch (provider)
            {
                case "postgres":
                    opt.UseNpgsql(cfg.GetConnectionString("Postgres"));
                    break;
                case "mysql":
                    var cs = cfg.GetConnectionString("MySql");
                    opt.UseMySql(cs, ServerVersion.AutoDetect(cs));
                    break;
                case "sqlite":
                    opt.UseSqlite(cfg.GetConnectionString("Sqlite"));
                    break;
                default:
                    throw new InvalidOperationException($"Unsupported provider: {provider}");
            }
        });
        return services;
    }
}
