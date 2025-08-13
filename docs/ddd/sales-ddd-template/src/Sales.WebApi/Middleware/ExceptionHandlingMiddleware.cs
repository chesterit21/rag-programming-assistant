
using System.Text.Json;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Sales.Domain.Abstractions;
using Sales.Domain.Orders;

namespace Sales.WebApi.Middleware;

public sealed class ExceptionHandlingMiddleware : IMiddleware
{
    private readonly ILogger<ExceptionHandlingMiddleware> _log;
    public ExceptionHandlingMiddleware(ILogger<ExceptionHandlingMiddleware> log) => _log = log;

    public async Task InvokeAsync(HttpContext ctx, RequestDelegate next)
    {
        try { await next(ctx); }
        catch (ValidationException ex)
        {
            _log.LogWarning(ex, "Validation error");
            await WriteProblem(ctx, StatusCodes.Status400BadRequest, "validation_error", ex.Errors);
        }
        catch (DomainException ex)
        {
            _log.LogWarning(ex, "Domain error");
            await WriteProblem(ctx, StatusCodes.Status409Conflict, "domain_error", new [] { new { Path = "", Message = ex.Message } });
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Unhandled error");
            await WriteProblem(ctx, StatusCodes.Status500InternalServerError, "unhandled_error");
        }
    }

    private static Task WriteProblem(HttpContext ctx, int status, string title, object? errors = null)
    {
        ctx.Response.ContentType = "application/problem+json";
        ctx.Response.StatusCode = status;
        var problem = new
        {
            type = $"https://httpstatuses.com/{status}",
            title,
            status,
            traceId = ctx.TraceIdentifier,
            errors
        };
        return ctx.Response.WriteAsync(JsonSerializer.Serialize(problem));
    }
}
