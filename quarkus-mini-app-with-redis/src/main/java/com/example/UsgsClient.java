package com.example;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@Path("/earthquakes/feed/v1.0/summary")
@RegisterRestClient(configKey = "usgs-api")
public interface UsgsClient {

    @GET
    @Path("/all_hour.geojson")
    @Produces(MediaType.APPLICATION_JSON)
    UsgsFeed getAllHour();

    @GET
    @Path("/all_day.geojson")
    @Produces(MediaType.APPLICATION_JSON)
    UsgsFeed getAllDay();

    @GET
    @Path("/all_week.geojson")
    @Produces(MediaType.APPLICATION_JSON)
    UsgsFeed getAllWeek();

    @GET
    @Path("/all_month.geojson")
    @Produces(MediaType.APPLICATION_JSON)
    UsgsFeed getAllMonth();
}
