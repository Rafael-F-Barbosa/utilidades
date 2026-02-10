package br.com.monitor.service;

import br.com.monitor.dto.ToolState;
import br.com.monitor.repository.ToolStateRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;

import java.util.List;

@ApplicationScoped
public class ToolStateService {

    @Inject
    ToolStateRepository repository;

    @Inject
    PushGatewayService pushGatewayService;

    public void save(ToolState state) {
        repository.save(state);
        System.out.println("Saved state: " + state + "\n\n");
        try {
            // Trigger non-blocking push of the saved timestamp; failures are handled inside the service
            System.out.println("Pushing timestamp to Pushgateway: " + state.timestamp());
            pushGatewayService.pushTimestamp(state.timestamp());
        } catch (Exception e) {
            System.out.println("Aqui deu ruim!!! \n\n\n");
        }
    }

    public List<ToolState> read() {
        return repository.readLast();
    }

    public void clear() {
        repository.clear();
    }

    
}