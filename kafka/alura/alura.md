- List topics
```shell
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

- Consume
```
docker-compose exec kafka kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic YOUR_TOPIC --from-beginning
```