
// appsettings.json
// "EventSourcing": { "Enabled": true }

// Program.cs
// if (builder.Configuration.GetSection("EventSourcing").GetValue<bool>("Enabled"))
// {
//   // add event store model to DbContext.OnModelCreating: EventStoreModel.Configure(modelBuilder)
//   builder.Services.AddScoped<IEventSerializer, DefaultEventSerializer>();
//   builder.Services.AddScoped<IEventStore, EfCoreEventStore>();
//   builder.Services.AddScoped<IOrderRepository, EventSourcedOrderRepository>();
//   builder.Services.AddHostedService<OrderToMongoProjector>();
// }
