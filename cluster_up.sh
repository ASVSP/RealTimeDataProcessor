echo "Cluster up..."
docker-compose up --build -d
echo "Pulling Postgres .jar file..."
docker exec spark-master-real wget https://jdbc.postgresql.org/download/postgresql-42.2.6.jar
#docker exec spark-master-real wget https://search.maven.org/remotecontent?filepath=org/apache/spark/spark-sql-kafka-0-10_2.12/3.0.1/spark-sql-kafka-0-10_2.12-3.0.1.jar -O spark-sql-kafka-0-10.jar
#docker exec spark-master-real wget https://search.maven.org/remotecontent?filepath=org/mongodb/spark/mongo-spark-connector_2.12/3.0.1/mongo-spark-connector_2.12-3.0.1.jar -O mongo-spark-connector_3.0.1.jar
