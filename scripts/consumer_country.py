from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
import os

spark = SparkSession \
    .builder \
    .appName("Average country AQI") \
    .config("spark.streaming.stopGracefullyOnShutdown", True) \
    .getOrCreate()


def write_mold_lvl(df, epoch_id):
    df.write\
        .format('jdbc') \
        .mode('overwrite') \
        .options(url='jdbc:postgresql://postgres:5432/postgres',
                 driver='org.postgresql.Driver',
                 dbtable='city_mold_lvl',
                 user='asvsp',
                 password='asvsp',
                 connectionTimeout='30000',
                 socketTimeout='60000'
                 ) \
        .save()


def write_avg_aqi(df, epoch_id):
    df.write\
        .format('jdbc') \
        .mode('overwrite') \
        .options(url='jdbc:postgresql://postgres:5432/postgres',
                 driver='org.postgresql.Driver',
                 dbtable='country_avg_aqi',
                 user='asvsp',
                 password='asvsp',
                 connectionTimeout='30000',
                 socketTimeout='60000'
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

china_df = load_df("china_info")
india_df = load_df("india_info")
serbia_df = load_df("serbia_info")

streaming_df = china_df\
    .union(india_df)\
    .union(serbia_df)

# Cities with a known mold level
df_increased_mold_lvl = streaming_df \
    .withWatermark("timestamp", "1 hour") \
    .filter(col("mold_level") > 0)\
    .groupBy(
        "city_name",
        window("timestamp", "1 hour", "20 minutes"),
    ).agg(round(avg("mold_level"), 2).alias("avg_mold_lvl"), round(avg("aqi"), 2).alias("avg_aqi"))


df_increased_mold_lvl = df_increased_mold_lvl \
    .withColumn("window_start", col("window.start")) \
    .withColumn("window_end", col("window.end")) \
    .drop("window")

# Avg country AQI
df_avg_aqi = streaming_df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        "country_code",
        window("timestamp", "10 minutes", "5 minutes"),
    ).agg(round(avg("aqi"), 2).alias("avg_aqi"))

df_avg_aqi = df_avg_aqi\
    .withColumn("window_start", col("window.start")) \
    .withColumn("window_end", col("window.end")) \
    .drop("window")

# Writing to db
query = df_increased_mold_lvl.writeStream \
    .trigger(processingTime='5 seconds') \
    .outputMode("complete") \
    .foreachBatch(write_mold_lvl) \
    .start()\

query = df_avg_aqi.writeStream \
    .trigger(processingTime='5 seconds') \
    .outputMode("complete") \
    .foreachBatch(write_avg_aqi) \
    .start()\

query.awaitTermination()
