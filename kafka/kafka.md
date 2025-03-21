## Kakfa setup

```yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    networks:
      - kafka-network

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    networks:
      - kafka-network

networks:
  kafka-network:
    driver: bridge

```

Criar um tópico kakfa:

```shell
docker exec -it kafka kafka-topics --create \
  --topic my-topic \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

Lista tópicos disponíveis:
```shell
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092
```

Produz mensagens:
```shell
docker exec -it kafka kafka-console-producer --topic my-topic --bootstrap-server localhost:9092
```

Consome mensagens, mas não tira elas do tópico:
```shell
docker exec -it kafka kafka-console-consumer --topic my-topic --bootstrap-server localhost:9092 --from-beginning
```