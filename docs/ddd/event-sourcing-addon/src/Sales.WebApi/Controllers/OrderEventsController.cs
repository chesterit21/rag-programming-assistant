
using Microsoft.AspNetCore.Mvc;
using Sales.Domain.Abstractions;

namespace Sales.WebApi.Controllers;

[ApiController]
[Route("api/orders/{id:guid}/events")]
public class OrderEventsController : ControllerBase
{
    private readonly IEventStore _store;
    public OrderEventsController(IEventStore store) => _store = store;

    [HttpGet]
    public async Task<IActionResult> Get(Guid id, CancellationToken ct)
    {
        var stream = await _store.ReadStreamAsync(id, ct);
        return stream.Count == 0 ? NotFound() : Ok(stream);
    }
}
