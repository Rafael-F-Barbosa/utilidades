package br.com.monitor.resource;

import br.com.monitor.dto.ToolState;
import br.com.monitor.service.ToolStateService;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.util.List;

@Path("/tool-state")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class ToolStateResource {

    @Inject
    ToolStateService service;

    @POST
    public void save(ToolState state) {
        service.save(state);
    }

    @GET
    public List<ToolState> read() {
        return service.read();
    }

    @DELETE
    public Response clear() {
        service.clear();
        return Response.noContent().build();
    }
}