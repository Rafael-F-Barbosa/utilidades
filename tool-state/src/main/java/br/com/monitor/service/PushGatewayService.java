package br.com.monitor.service;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Instant;

import jakarta.enterprise.context.ApplicationScoped;

import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.jboss.logging.Logger;

@ApplicationScoped
public class PushGatewayService {
    private static final Logger LOG = Logger.getLogger(PushGatewayService.class);

    @ConfigProperty(name = "pushgateway.url", defaultValue = "http://pushgateway:9091")
    String pushgatewayUrl;

    private final HttpClient httpClient = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();

    /**
     * Push a provided epoch seconds timestamp to Pushgateway in a non-blocking way.
     * Failures are logged and do not propagate.
     */
    public void pushTimestamp(long epochSeconds) {
        String metric = "tool_timestamp{app=\"tool-state\"} " + epochSeconds + "\n";
        String url = pushgatewayUrl.endsWith("/") ? pushgatewayUrl + "metrics/job/tool-state" : pushgatewayUrl + "/metrics/job/tool-state";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .PUT(HttpRequest.BodyPublishers.ofString(metric))
                .header("Content-Type", "text/plain; version=0.0.4")
                .build();

        httpClient.sendAsync(request, HttpResponse.BodyHandlers.discarding())
                .thenAccept(response -> {
                    int code = response.statusCode();
                    if (code >= 200 && code < 300) {
                        LOG.debugf("Pushed metric timestamp=%d to %s", epochSeconds, url);
                    } else {
                        LOG.warnf("Pushgateway returned status %d when pushing timestamp=%d", code, epochSeconds);
                    }
                })
                .exceptionally(t -> {
                    LOG.warnf(t, "Failed to push metric timestamp (non-blocking)");
                    return null;
                });
    }
}
