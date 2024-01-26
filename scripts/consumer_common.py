from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
import os

spark = SparkSession \
    .builder \
    .appName("Average country AQI") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .getOrCreate()


def write_to_postgres(df, epoch_id):
    df.write \
        .format('jdbc') \
        .mode('overwrite') \
        .options(url='jdbc:postgresql://host.docker.internal:5433/postgres',
                 driver='org.postgresql.Driver',
                 dbtable='city_air_quality',
                 user='asvsp',
                 password='asvsp',
                 connectionTimeout='30000'
                 ) \
        .save()


def load_df(topic):
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "broker1:19092") \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load() \
        .selectExpr("CAST(value as string) as value")
    return df.withColumn("value", from_json(df["value"], schema)) \
        .select("value.*") \
        .withColumn("timestamp", current_timestamp())


schema = StructType([
    StructField("identifier_code", StringType(), True),
    StructField("aqi", FloatType(), True),
    StructField("co", FloatType(), True),
    StructField("mold_level", IntegerType(), True),
    StructField("no2", FloatType(), True),
    StructField("o3", FloatType(), True),
    StructField("pm10", FloatType(), True),
    StructField("pm25", FloatType(), True),
    StructField("pollen_level_grass", IntegerType(), True),
    StructField("pollen_level_tree", IntegerType(), True),
    StructField("pollen_level_weed", IntegerType(), True),
    StructField("so2", FloatType(), True),
    StructField("city_name", StringType(), True),
    StructField("country_code", StringType(), True),
    StructField("lat", FloatType(), True),
    StructField("lon", FloatType(), True),
    StructField("state_code", StringType(), True),
    StructField("timezone", StringType(), True),
])

# Modifying streaming data frame
streaming_df = load_df("common") \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
    "city_name",
    window("timestamp", "10 minutes", "5 minutes"),
).agg(round(avg("co"), 2).alias("avg_co"),
      round(avg("no2"), 2).alias("avg_no2"),
      round(avg("so2"), 2).alias("avg_so2"),
      round(avg("o3"), 2).alias("avg_o3"),
      round(avg("pm10"), 2).alias("avg_pm10"),
      round(avg("pm25"), 2).alias("avg_pm25")
      )

streaming_df = streaming_df \
    .withColumn("window_start", col("window.start")) \
    .withColumn("window_end", col("window.end")) \
    .drop("window")

# Writing to db
query = streaming_df.writeStream \
    .trigger(processingTime='5 seconds') \
    .outputMode("complete") \
    .foreachBatch(write_to_postgres) \
    .start() \
    .awaitTermination()
