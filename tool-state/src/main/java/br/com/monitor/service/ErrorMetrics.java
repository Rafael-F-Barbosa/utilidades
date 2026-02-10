package br.com.monitor.service;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@ApplicationScoped
public class ErrorMetrics {

    @Inject
    MeterRegistry registry;

    private final Map<String, Counter> counters = new ConcurrentHashMap<>();

    public void countError(String type) {
        counters.computeIfAbsent(type, t ->
                Counter.builder("app_errors_total")
                       .tag("type", t)
                       .register(registry)
        ).increment();
    }

}
