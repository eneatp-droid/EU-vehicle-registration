"""
Consumes fleet telemetry events from Kafka using Spark Structured Streaming,
aggregates by time window and flags simple anomalies (engine overheating).

Run with:
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 consumer.py
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, avg, max as spark_max
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "fleet.telemetry"

SCHEMA = StructType([
    StructField("vehicle_id", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("speed_kmh", DoubleType()),
    StructField("rpm", DoubleType()),
    StructField("engine_temp_c", DoubleType()),
    StructField("fuel_level_pct", DoubleType()),
    StructField("latitude", DoubleType()),
    StructField("longitude", DoubleType()),
])

ENGINE_TEMP_ALERT_THRESHOLD_C = 110.0


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("FleetTelemetryConsumer")
        .getOrCreate()
    )


def main():
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    raw_stream = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    events = (
        raw_stream
        .select(from_json(col("value").cast("string"), SCHEMA).alias("data"))
        .select("data.*")
    )

    # Agregação por janela de tempo (média de RPM e temperatura por veículo, a cada 30s)
    windowed_stats = (
        events
        .withWatermark("timestamp", "1 minute")
        .groupBy(window(col("timestamp"), "30 seconds"), col("vehicle_id"))
        .agg(
            avg("rpm").alias("avg_rpm"),
            avg("speed_kmh").alias("avg_speed"),
            spark_max("engine_temp_c").alias("max_engine_temp"),
        )
    )

    stats_query = (
        windowed_stats.writeStream
        .outputMode("update")
        .format("console")
        .option("truncate", False)
        .start()
    )

    # Alertas simples de superaquecimento
    alerts = events.filter(col("engine_temp_c") > ENGINE_TEMP_ALERT_THRESHOLD_C)
    alerts_query = (
        alerts.writeStream
        .outputMode("append")
        .format("console")
        .option("truncate", False)
        .start()
    )

    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
