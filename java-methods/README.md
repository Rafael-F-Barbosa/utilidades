## Execução concorrente Java
- Depende do serviço consumido ter workers(subprocessos que rodam de forma paralela para receber as requisições)
- Pode ser utilizado quando o resultado final não necessitar estar em ordem
```java
    @GET
    @Path("/async")
    @Produces(MediaType.APPLICATION_JSON)
    public Response asyncCall() {
        List<CompletableFuture<String>> futures = new ArrayList<>();


        ExecutorService executor = Executors.newFixedThreadPool(5);

        for (int i = 1; i <= 20; i++) {
            final int id = i;
            futures.add(CompletableFuture.supplyAsync(() -> {
                try {
                    return asyncService.chamada(String.valueOf(id));
                } catch (Exception e) {
                    return "Error for ID " + id;
                }
            }, executor));
        }

        List<String> responses = futures.stream()
            .map(CompletableFuture::join)
            .collect(Collectors.toList());

        return Response.ok().entity(responses).build();
    }

```

- Versão melhorada pelo GPT - Não testada
```java
@GET
@Path("/async")
@Produces(MediaType.APPLICATION_JSON)
public Response asyncCall() {
    List<CompletableFuture<String>> futures = new ArrayList<>();
    ExecutorService executor = Executors.newFixedThreadPool(5);

    try {
        for (int i = 1; i <= 20; i++) {
            final int id = i;
            futures.add(CompletableFuture.supplyAsync(() -> asyncService.chamada(String.valueOf(id)), executor)
                .completeOnTimeout("Timeout for ID " + id, 5, TimeUnit.SECONDS)
                .exceptionally(e -> "Error for ID " + id));
        }

        List<String> responses = futures.stream()
            .map(CompletableFuture::join)
            .collect(Collectors.toList());

        return Response.ok().entity(responses).build();
    } finally {
        executor.shutdown();
    }
}

```
