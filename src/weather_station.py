import zmq
import time
import json
import random
from datetime import datetime

IP_ADD = '127.0.0.1'
DATA_PROCESSES_INPUT_PORT = 5555


def generate_humidity_and_temperature():
    temperature = round(random.uniform(5, 40), 2)
    humidity = round(random.uniform(40, 100), 2)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    weather_data = {
        "time": timestamp,
        "temperature": temperature,
        "humidity": humidity
    }

    json_data = json.dumps(weather_data)
    return json_data


def generate_CO2():
    co2 = round(random.uniform(300, 500), 2)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    co2_data = {
        "time": timestamp,
        "co2": co2
    }

    json_data = json.dumps(co2_data)
    return json_data


def main():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://{IP_ADD}:{DATA_PROCESSES_INPUT_PORT}")

    try:
        while True:
            time.sleep(2)
            weather = generate_humidity_and_temperature()
            co2 = generate_CO2()
            socket.send_string(f"weather {weather}")
            print(f"Weather is sent from WS1 {weather}")
            time.sleep(2)
            socket.send_string(f"co2 {co2}")
            print(f"CO2 is sent from WS1 {co2}")
    except KeyboardInterrupt:
        print("Terminating weather station")


if __name__ == '__main__':
    main()
