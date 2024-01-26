from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
import os

spark = SparkSession \
    .builder \
    .appName("Average country AQI") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .getOrCreate()


def write_mongo_row(df, epoch_id):
    df.write.format("mongo") \
        .mode("append") \
        .option("uri", "mongodb://asvsp:asvsp@host.docker.internal:27018/") \
        .option("database", "asvsp") \
        .option("collection", "raw_data") \
        .save()
    pass


def load_df(topic):
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "broker1:19092") \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load() \
        .selectExpr("CAST(value as string) as value")
    return df.withColumn("value", from_json(df["value"], schema))\
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

# Writing to db
query = load_df("raw").writeStream \
    .trigger(processingTime='5 seconds') \
    .outputMode("update") \
    .foreachBatch(write_mongo_row) \
    .start() \

query.awaitTermination()
