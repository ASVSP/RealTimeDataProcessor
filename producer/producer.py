import json as json
import time
import os
import requests
from dotenv import load_dotenv
from kafka import KafkaProducer
import datetime
import uuid

# Environment variables
load_dotenv()
api_url = os.environ.get("API_URL")
kafka_broker = os.environ["KAFKA_BROKER"]
common_topic = os.environ["COMMON_TOPIC"]
raw_topic = os.environ["RAW_TOPIC"]


# Set up serializer
def serializer(message):
    return json.dumps(message).encode('utf-8')


# Kafka producer
producer = KafkaProducer(
    api_version=(0, 11, 5),
    bootstrap_servers=[kafka_broker],
    value_serializer=serializer
)


def fetch_air_quality():
    with open('location_coordinates.json') as f:
        location_coordinates = json.load(f)
        for location in location_coordinates:
            for idx, coordinates in enumerate(location):
                topic = coordinates['topic']
                coordinates.pop('topic')
                response = requests.get(api_url, params=coordinates).json()
                # Modifying response json object
                response['identifier_code'] = uuid.uuid4().hex
                response['aqi'] = response['data'][0]['aqi']
                response['co'] = response['data'][0]['co']
                response['mold_level'] = response['data'][0]['mold_level']
                response['no2'] = response['data'][0]['no2']
                response['o3'] = response['data'][0]['o3']
                response['pm10'] = response['data'][0]['pm10']
                response['pm25'] = response['data'][0]['pm25']
                response['pollen_level_grass'] = response['data'][0]['pollen_level_grass']
                response['pollen_level_tree'] = response['data'][0]['pollen_level_tree']
                response['pollen_level_weed'] = response['data'][0]['pollen_level_weed']
                response['so2'] = response['data'][0]['so2']
                response.pop("data")

                debug = True
                if debug:
                    print(f"--- Response {idx + 1} ---")
                    print(f"Params: {coordinates}")
                    print(f"Sending record to Kafka topics: {topic}; {common_topic}; {raw_topic}")
                    print(f"Record: {response}")
                    print(f"Timestamp: {datetime.datetime.now()}")
                producer.send(topic, response)
                producer.send(common_topic, response)
                producer.send(raw_topic, response)
                producer.flush()


def main():
    while True:
        fetch_air_quality()
        time.sleep(180)


if __name__ == "__main__":
    main()
