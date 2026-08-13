# PoC — USGS + Quarkus + Redis

Aplicação Quarkus (Java 21) que consulta a API da USGS periodicamente, armazena os dados no Redis e exibe os terremotos em uma página HTML.

## Como rodar

### 1. Suba o Redis localmente

```shell
docker compose up -d
```

### 2. Inicie a aplicação em modo dev

```shell
./mvnw quarkus:dev
```

> O Redis local fica em `redis://localhost:6379`. Para usar outro Redis, defina `REDIS_URL` (ex.: no arquivo `.env` da raiz do projeto):
>
> ```
> REDIS_URL=redis://localhost:6379
> ```

### 3. Acesse

- Página HTML: <http://localhost:8080>
- API: <http://localhost:8080/api/earthquakes>

## Como funciona

- **Cronjobs** (Quarkus Scheduler) consultam a USGS e armazenam o resultado no Redis em chaves por período:

| Período | Chave no Redis | Frequência |
|---------|----------------|------------|
| última hora (`hour`) | `usgs:earthquakes:hour` | a cada 1 min |
| últimas 24h (`day`) | `usgs:earthquakes:day` | a cada 15 min |
| últimos 7 dias (`week`) | `usgs:earthquakes:week` | a cada 1h |
| últimos 30 dias (`month`) | `usgs:earthquakes:month` | a cada 6h |

Cada valor tem o formato:

```json
{
  "lastUpdated": "2026-08-13T18:30:00Z",
  "data": {
    "type": "FeatureCollection",
    "features": []
  }
}
```

- O endpoint `GET /api/earthquakes` apenas **lê o Redis** — não consulta a USGS.
- A página HTML chama `GET /api/earthquakes`; o botão **Atualizar** também apenas relê o Redis.

## Instrumentação (logs de tempo)

A aplicação registra em log (INFO) o tempo de execução:

- **Jobs**: cada execução do cronjob loga o tempo total (consulta à USGS + gravação no Redis):
  `JOB [hour] executado em 850 ms: 4 terremotos armazenados no Redis`
- **Requests HTTP**: cada requisição loga método, caminho, status e tempo de resposta:
  `REQUEST GET /api/earthquakes -> 200 em 12 ms`

## Endpoints

### Recuperar os terremotos armazenados

`GET /api/earthquakes?period=hour|day|week|month` (padrão: `hour`)

```shell
curl "http://localhost:8080/api/earthquakes?period=month"
```

Resposta:

```json
{
  "lastUpdated": "2026-08-13T18:30:00Z",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "properties": {
          "mag": 2.5,
          "place": "5 km E de Ranson, WV",
          "time": 1723563000000
        }
      }
    ]
  }
}
```

### Página HTML

`GET /` — exibe último horário de atualização, quantidade de terremotos, lista com magnitude/localização/horário, seletor de período e o botão **Atualizar**.

## Fonte de dados

Feeds GeoJSON da USGS (atualizados a cada minuto pela USGS):

- `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson`
- `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson`
- `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson`
- `https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson`
