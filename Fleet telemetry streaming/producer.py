"""
Simulates telemetry events from a fleet of vehicles and publishes them to Kafka.

Run Kafka locally first, e.g. via Docker Compose (bitnami/kafka image).
"""
import json
import logging
import random
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "fleet.telemetry"
NUM_VEHICLES = 10
EVENTS_PER_SECOND = 5


def make_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def generate_event(vehicle_id: str) -> dict:
    """Generate one plausible telemetry reading for a given vehicle."""
    return {
        "vehicle_id": vehicle_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed_kmh": round(random.gauss(70, 20), 1),
        "rpm": round(random.gauss(2200, 500)),
        "engine_temp_c": round(random.gauss(90, 8), 1),
        "fuel_level_pct": round(random.uniform(5, 100), 1),
        "latitude": round(random.uniform(45.0, 55.0), 5),   # faixa aproximada da Europa central
        "longitude": round(random.uniform(0.0, 20.0), 5),
    }


def main():
    producer = make_producer()
    vehicle_ids = [f"VEH-{i:03d}" for i in range(1, NUM_VEHICLES + 1)]

    logger.info("Iniciando simulação de telemetria para %d veículos...", NUM_VEHICLES)
    try:
        while True:
            for vehicle_id in vehicle_ids:
                event = generate_event(vehicle_id)
                producer.send(TOPIC, value=event)
            producer.flush()
            time.sleep(1 / EVENTS_PER_SECOND)
    except KeyboardInterrupt:
        logger.info("Simulação encerrada pelo usuário.")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
