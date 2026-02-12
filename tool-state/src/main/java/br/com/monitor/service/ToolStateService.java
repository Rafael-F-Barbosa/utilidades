package br.com.monitor.service;

import br.com.monitor.dto.ToolState;
import br.com.monitor.repository.ToolStateRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.List;

@ApplicationScoped
public class ToolStateService {

    @Inject
    ToolStateRepository repository;

    @Inject
    ErrorMetrics errorMetrics;

    public void save(ToolState state) {
        // determine metric name and value (take first metric if multiple)
        String metricName = null;
        Number metricValue = null;
        if (state.metricas() != null && !state.metricas().isEmpty()) {
            var it = state.metricas().entrySet().iterator();
            var e = it.next();
            metricName = e.getKey();
            metricValue = e.getValue();
        }

        long ts = metricValue == null ? 0L : metricValue.longValue();

        // Determine state using the same thresholds as before
        if (ts < 50) {
            errorMetrics.setState("ErroThresholdInferior");
        } else if (ts > 100) {
            errorMetrics.setState("ErroThresholdSuperior");
        } else {
            errorMetrics.setState("Estavel");
        }

        // record the dynamic measure (e.g., temperatura, umidade)
        if (metricName != null) {
            errorMetrics.recordMeasure(metricName, metricValue);
        }

        // persist with server timestamp for sorting/history
        ToolState toPersist = new ToolState(state.tool(), state.status(), state.metricas());
        repository.save(toPersist);
        System.out.println("Saved state: " + toPersist + "\n\n");
    }

    public List<ToolState> read() {
        return repository.readLast();
    }

    public void clear() {
        repository.clear();
    }

    
}