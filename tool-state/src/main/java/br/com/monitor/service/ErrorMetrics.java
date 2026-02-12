package br.com.monitor.service;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

@ApplicationScoped
public class ErrorMetrics {

    @Inject
    MeterRegistry registry;

    private final Map<String, AtomicInteger> gauges = new ConcurrentHashMap<>();
    private final Map<String, AtomicLong> measures = new ConcurrentHashMap<>();

    // known states to enforce zeros when not active
    private static final String STATE_LOW = "ErroThresholdInferior";
    private static final String STATE_HIGH = "ErroThresholdSuperior";
    private static final String STATE_STABLE = "Estavel";

    @PostConstruct
    void init() {
        // pre-register known state gauges so we can always set 0/1
        gauges.computeIfAbsent(STATE_LOW, this::registerGauge);
        gauges.computeIfAbsent(STATE_HIGH, this::registerGauge);
        gauges.computeIfAbsent(STATE_STABLE, this::registerGauge);
    }

    public void setState(String currentType) {
        // ensure current type gauge exists
        gauges.computeIfAbsent(currentType, this::registerGauge);

        // set 1 for current type, 0 for others
        for (Map.Entry<String, AtomicInteger> e : gauges.entrySet()) {
            e.getValue().set(e.getKey().equals(currentType) ? 1 : 0);
        }
    }

    public void recordMeasure(String metricName, Number value) {
        AtomicLong al = measures.computeIfAbsent(metricName, this::registerMeasure);
        al.set(value == null ? 0L : value.longValue());
    }

    private AtomicLong registerMeasure(String metricName) {
        AtomicLong al = new AtomicLong(0L);
        Gauge.builder("app_measure", al, AtomicLong::get)
             .tag("type", metricName)
             .description("Dynamic measure by type, e.g. temperatura, umidade")
             .register(registry);
        return al;
    }

    private AtomicInteger registerGauge(String type) {
        AtomicInteger ai = new AtomicInteger(0);
        Gauge.builder("app_state", ai, AtomicInteger::get)
             .tag("type", type)
             .description("State gauge: 1 for current, 0 otherwise")
             .register(registry);
        return ai;
    }

}
