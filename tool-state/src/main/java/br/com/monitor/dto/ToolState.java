package br.com.monitor.dto;

public record ToolState(
    String tool,
    String status,
    long timestamp) {
} 

