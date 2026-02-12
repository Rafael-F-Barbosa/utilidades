package br.com.monitor.dto;

import java.util.Map;

public record ToolState(
    String tool,
    String status,
    Map<String, Number> metricas
) {
}

