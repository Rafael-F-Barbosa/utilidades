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
        repository.save(state);
        System.out.println("Saved state: " + state + "\n\n");
        long ts = state.timestamp();
        // Determine state and increment appropriate metric
        if (ts < 50) {
            errorMetrics.countError("ErroThresholdInferior");
        } else if (ts > 100) {
            errorMetrics.countError("ErroThresholdSuperior");
        } else {
            errorMetrics.countError("AplicacaoEstavel");
        }
    }

    public List<ToolState> read() {
        return repository.readLast();
    }

    public void clear() {
        repository.clear();
    }

    
}