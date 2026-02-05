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

    public void save(ToolState state) {
        repository.save(state);
    }

    public List<ToolState> read() {
        return repository.readLast();
    }

    public void clear() {
        repository.clear();
    }

    
}