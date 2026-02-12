# tool-state

This project uses Quarkus, the Supersonic Subatomic Java Framework.

If you want to learn more about Quarkus, please visit its website: <https://quarkus.io/>.

## Running the application in dev mode

You can run your application in dev mode that enables live coding using:

```shell script
./mvnw quarkus:dev
```

> **_NOTE:_**  Quarkus now ships with a Dev UI, which is available in dev mode only at <http://localhost:8080/q/dev/>.

## Packaging and running the application

The application can be packaged using:

```shell script
./mvnw package
```

It produces the `quarkus-run.jar` file in the `target/quarkus-app/` directory.
Be aware that it’s not an _über-jar_ as the dependencies are copied into the `target/quarkus-app/lib/` directory.

The application is now runnable using `java -jar target/quarkus-app/quarkus-run.jar`.

If you want to build an _über-jar_, execute the following command:

```shell script
./mvnw package -Dquarkus.package.jar.type=uber-jar
```

The application, packaged as an _über-jar_, is now runnable using `java -jar target/*-runner.jar`.

## Creating a native executable

You can create a native executable using:

```shell script
./mvnw package -Dnative
```

Or, if you don't have GraalVM installed, you can run the native executable build in a container using:

```shell script
./mvnw package -Dnative -Dquarkus.native.container-build=true
```

You can then execute your native executable with: `./target/tool-state-1.0.0-SNAPSHOT-runner`

If you want to learn more about building native executables, please consult <https://quarkus.io/guides/maven-tooling>.

## Related Guides

- REST Jackson ([guide](https://quarkus.io/guides/rest#json-serialisation)): Jackson serialization support for Quarkus REST. This extension is not compatible with the quarkus-resteasy extension, or any of the extensions that depend on it

## Provided Code

### REST

Easily start your REST Web Services

[Related guide section...](https://quarkus.io/guides/getting-started-reactive#reactive-jax-rs-resources)


### Ideias

Realizar alterações na aplicação para:
Utilizar métricas de gauge, se já não tiver feito
Utilizar ao salvar métricas sempre colocar um estado de 0 nos estados que não estão ativos e 1 para estados ativos, assim ficaria(Estavel=1, SemComunicacao=0, EstadoInesperado=0) 
Salvar também medidas dos estados do Control-M com meter registry, utilizando duas métricas diferentes uma para app_folder_measures com cada tipo sendo os status das folders e uma app_jobs_measures com cada tipo sendo os status dos jobs.

De forma análoga ao exemplo: 
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