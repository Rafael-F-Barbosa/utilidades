package com.example;

import jakarta.inject.Inject;
import jakarta.ws.rs.DefaultValue;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/api/earthquakes")
public class EarthquakeResource {

    @Inject
    EarthquakeService earthquakeService;

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response get(@QueryParam("period") @DefaultValue("hour") String period) {
        if (!earthquakeService.isPeriodValid(period)) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity("Período inválido. Use: hour, day, week ou month.")
                    .build();
        }
        return Response.ok(earthquakeService.get(period)).build();
    }
}
