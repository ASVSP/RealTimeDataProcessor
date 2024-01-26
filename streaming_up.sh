docker exec spark-master-real ./spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 ./asvsp/scripts/consumer_raw.py &
docker exec spark-master-real ./spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 --jars postgresql-42.2.6.jar ./asvsp/scripts/consumer_common.py &
docker exec spark-master-real ./spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 --jars postgresql-42.2.6.jar ./asvsp/scripts/consumer_country.py &
wait