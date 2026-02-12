package br.com.monitor.repository;

import br.com.monitor.dto.ToolState;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.enterprise.context.ApplicationScoped;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

@ApplicationScoped
public class ToolStateRepository {

    private static final Path FILE = Path.of("data/tool-state.json");
    private static final int MAX_STATES = 3;

    private final ObjectMapper mapper = new ObjectMapper();

    public void save(ToolState state) {
        try {
            ensureFileInitialized();

            List<ToolState> states = readAllInternal();

            // adiciona novo estado
            states.add(state);

            // mantém apenas os últimos 3
            if (states.size() > MAX_STATES) {
                states = states.subList(states.size() - MAX_STATES, states.size());
            }

            mapper.writerWithDefaultPrettyPrinter().writeValue(FILE.toFile(), states);

        } catch (IOException e) {
            throw new RuntimeException("Erro ao salvar estado", e);
        }
    }

    public List<ToolState> readLast() {
        try {
            ensureFileInitialized();
            return readAllInternal();
        } catch (IOException e) {
            throw new RuntimeException("Erro ao ler estados", e);
        }
    }

    // =========================
    // Métodos auxiliares
    // =========================

    private void ensureFileInitialized() throws IOException {
        // garante diretório
        Files.createDirectories(FILE.getParent());

        // se arquivo não existe, cria com lista vazia []
        if (!Files.exists(FILE)) {
            mapper.writerWithDefaultPrettyPrinter().writeValue(FILE.toFile(), new ArrayList<>());
            return;
        }

        // se existir mas estiver inválido/corrompido, recria
        try {
            mapper.readValue(FILE.toFile(), new TypeReference<List<ToolState>>() {});
        } catch (Exception e) {
            mapper.writerWithDefaultPrettyPrinter().writeValue(FILE.toFile(), new ArrayList<>());
        }
    }

    private List<ToolState> readAllInternal() throws IOException {
        return mapper.readValue(FILE.toFile(), new TypeReference<List<ToolState>>() {});
    }

    public void clear() {
    try {
        Files.createDirectories(FILE.getParent());
        mapper.writerWithDefaultPrettyPrinter().writeValue(FILE.toFile(), new ArrayList<>());
    } catch (IOException e) {
        throw new RuntimeException("Erro ao limpar estados", e);
    }
}
}
