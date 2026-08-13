package com.example;

import io.quarkus.redis.datasource.RedisDataSource;
import io.quarkus.redis.datasource.keys.KeyScanCursor;
import io.quarkus.redis.datasource.string.StringCommands;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import java.util.LinkedHashMap;
import java.util.Map;

@Path("/values")
public class ValuesResource {

    @Inject
    RedisDataSource redis;

    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> set(KeyValue kv) {
        StringCommands<String, String> strings = redis.string(String.class, String.class);
        strings.set(kv.key(), kv.value());
        return Map.of(kv.key(), kv.value());
    }

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, String> getAll() {
        StringCommands<String, String> strings = redis.string(String.class, String.class);
        Map<String, String> result = new LinkedHashMap<>();
        KeyScanCursor<String> keys = redis.key(String.class).scan();
        for (String key : keys.toIterable()) {
            result.put(key, strings.get(key));
        }
        return result;
    }

    public record KeyValue(String key, String value) {
    }
}
