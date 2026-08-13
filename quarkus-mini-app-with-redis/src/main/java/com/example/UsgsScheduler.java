package com.example;

import io.quarkus.scheduler.Scheduled;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.logging.Logger;

@ApplicationScoped
public class UsgsScheduler {

    private static final Logger LOG = Logger.getLogger(UsgsScheduler.class);

    @Inject
    @RestClient
    UsgsClient usgsClient;

    @Inject
    EarthquakeService earthquakeService;

    @Scheduled(every = "1m", concurrentExecution = Scheduled.ConcurrentExecution.SKIP)
    void updateHour() {
        fetchAndStore(EarthquakeService.PERIOD_HOUR, usgsClient.getAllHour());
    }

    @Scheduled(every = "15m", concurrentExecution = Scheduled.ConcurrentExecution.SKIP)
    void updateDay() {
        fetchAndStore(EarthquakeService.PERIOD_DAY, usgsClient.getAllDay());
    }

    @Scheduled(every = "1h", concurrentExecution = Scheduled.ConcurrentExecution.SKIP)
    void updateWeek() {
        fetchAndStore(EarthquakeService.PERIOD_WEEK, usgsClient.getAllWeek());
    }

    @Scheduled(every = "6h", concurrentExecution = Scheduled.ConcurrentExecution.SKIP)
    void updateMonth() {
        fetchAndStore(EarthquakeService.PERIOD_MONTH, usgsClient.getAllMonth());
    }

    private void fetchAndStore(String period, UsgsFeed feed) {
        long start = System.nanoTime();
        try {
            int count = feed.features() == null ? 0 : feed.features().size();
            earthquakeService.save(period, feed);
            long elapsedMs = (System.nanoTime() - start) / 1_000_000;
            LOG.infof("JOB [%s] executado em %d ms: %d terremotos armazenados no Redis", period, elapsedMs, count);
        } catch (Exception e) {
            long elapsedMs = (System.nanoTime() - start) / 1_000_000;
            LOG.errorf(e, "JOB [%s] falhou após %d ms", period, elapsedMs);
        }
    }
}
