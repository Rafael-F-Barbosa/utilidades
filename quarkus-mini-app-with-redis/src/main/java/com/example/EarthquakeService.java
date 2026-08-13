package com.example;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.quarkus.redis.datasource.RedisDataSource;
import io.quarkus.redis.datasource.string.StringCommands;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.List;

@ApplicationScoped
public class EarthquakeService {

    public static final String KEY_HOUR = "usgs:earthquakes:hour";
    public static final String KEY_DAY = "usgs:earthquakes:day";
    public static final String KEY_WEEK = "usgs:earthquakes:week";
    public static final String KEY_MONTH = "usgs:earthquakes:month";

    public static final String PERIOD_HOUR = "hour";
    public static final String PERIOD_DAY = "day";
    public static final String PERIOD_WEEK = "week";
    public static final String PERIOD_MONTH = "month";

    private static final List<String> VALID_PERIODS =
            List.of(PERIOD_HOUR, PERIOD_DAY, PERIOD_WEEK, PERIOD_MONTH);

    @Inject
    RedisDataSource redis;

    @Inject
    ObjectMapper objectMapper;

    public void save(String period, UsgsFeed feed) {
        String lastUpdated = DateTimeFormatter.ISO_INSTANT.format(Instant.now());
        EarthquakeData data = new EarthquakeData(lastUpdated, feed);
        try {
            stringCommands().set(keyFor(period), objectMapper.writeValueAsString(data));
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    public EarthquakeData get(String period) {
        String json = stringCommands().get(keyFor(period));
        if (json == null) {
            return new EarthquakeData(null, new UsgsFeed("FeatureCollection", List.of()));
        }
        try {
            return objectMapper.readValue(json, EarthquakeData.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    public boolean isPeriodValid(String period) {
        return VALID_PERIODS.contains(period);
    }

    public String keyFor(String period) {
        return switch (period) {
            case PERIOD_DAY -> KEY_DAY;
            case PERIOD_WEEK -> KEY_WEEK;
            case PERIOD_MONTH -> KEY_MONTH;
            default -> KEY_HOUR;
        };
    }

    private StringCommands<String, String> stringCommands() {
        return redis.string(String.class, String.class);
    }
}
