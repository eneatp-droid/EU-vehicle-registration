# Fleet Telemetry Streaming Pipeline

**Theme:** Simulate telemetry from a fleet of vehicles and process the data in real time.


## Data sources and APIs

- **Kafka** — message broker used for event streaming
  - Local setup: Docker Compose with `bitnami/kafka` or `confluentinc/cp-kafka`
  - Topic: `fleet.telemetry`
- **PySpark Structured Streaming** — stream processing engine for windowed aggregation and anomaly detection
- **Optional:** Postgres or Parquet output for downstream analysis

## Architecture

```
producer.py (sensor simulation) ──▶ Kafka topic "fleet.telemetry"
                                          │
                                          ▼
                          Spark Structured Streaming (consumer.py)
                                          │
                             ┌────────────┴────────────┐
                             ▼                         ▼
                     time-window aggregations     real-time alerts
                     (e.g. avg RPM / 5 min)      (e.g. temp > threshold)
                             │
                             ▼
                    Data lake (Parquet) / Postgres
```

## Local setup

1. Start Kafka locally.
2. Run `producer.py` to generate telemetry for multiple vehicles.
3. Run `consumer.py` to process events and detect anomalies.
4. Optionally store aggregated results in Postgres or Parquet.

## API / dependency notes

No external public API is required for the simulator. The project relies on:
- Kafka broker at `localhost:9092`
- PySpark with Kafka integration
- Python libraries listed in `requirements.txt`

## Example alerts

- Engine temperature above `110°C` for a sustained period
- RPM spikes after acceleration cycles
- speed anomalies from route or sensor drift

## Immediate next steps

1. Define a production event schema for telemetry:
   - vehicle_id
   - timestamp
   - speed_kmh
   - rpm
   - engine_temp_c
   - fuel_level_pct
   - geolocation
2. Add realistic anomaly detection rules:
   - engine temperature above threshold
   - repeated RPM spikes
   - sustained under-speed or over-speed events
3. Connect the producer and consumer to Kafka with an end-to-end pipeline test.
4. Save aggregated results to a Postgres table or Parquet output for history tracking.
5. Add a monitoring dashboard with:
   - active vehicles
   - average RPM
   - alert count
   - fleet health overview

## Recommended roadmap

- Phase 1: validate streaming flow with a small fleet simulation.
- Phase 2: add rolling time-window aggregation and anomaly alerts.
- Phase 3: connect to a warehouse or warehouse-style storage for historical analysis.
- Phase 4: add a real-time operational dashboard for portfolio presentation.
