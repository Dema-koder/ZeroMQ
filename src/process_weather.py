import zmq
import json
import threading
from datetime import datetime, timedelta

WEATHER_INPUT_PORT = 5555
FASHION_SOCKET_PORT = 5556

IP_ADD = '127.0.0.1'

latest_data = {'average-temp': 0, 'average-hum': 0}
prev_weather_data = []


def average_temperature_humidity():
    current_time = datetime.now() - timedelta(seconds=30)
    k = 0
    for data in prev_weather_data:
        if datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S') >= current_time:
            k = k + 1
            latest_data['average-temp'] += data[1]
            latest_data['average-hum'] += data[2]

    if k == 0:
        latest_data['average-temp'] = 0
        latest_data['average-hum'] = 0
        return

    latest_data['average-temp'] = latest_data['average-temp'] / k
    latest_data['average-hum'] /= latest_data['average-hum'] / k

    for data in prev_weather_data[:]:
        if datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S') < current_time:
            prev_weather_data.remove(data)


def recommendation():
    result = ""
    average_temperature_humidity()
    if latest_data['average-temp'] < 10:
        result = "Today weather is cold. Its better to wear warm clothes"
    elif 10 < latest_data['average-temp'] < 25:
        result = "Feel free to wear spring/autumn clothes"
    else:
        result = "Go for light clothes"
    print(result)
    return result


def report():
    average_temperature_humidity()
    result = f"The last 30 sec average Temperature is {latest_data['average-temp']} and Humidity {latest_data['average-hum']}"
    print(result)
    return result


def receive_weather_data():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{IP_ADD}:{WEATHER_INPUT_PORT}")

    socket.setsockopt_string(zmq.SUBSCRIBE, "weather")

    try:
        with open('weather_data.log', 'a') as log_file:
            while True:
                data = socket.recv_string()
                log_file.write(f"{data[8:]}\n")
                print(f"Received weather data: {data}")
                weather_data = json.loads(data[8:])
                prev_weather_data.append((weather_data["time"], weather_data["temperature"], weather_data["humidity"]))

    except KeyboardInterrupt:
        socket.close()
        print("Terminating...")


def handle_client_request():
    client_context = zmq.Context()
    client_socket = client_context.socket(zmq.REP)
    client_socket.bind(f"tcp://{IP_ADD}:{FASHION_SOCKET_PORT}")

    try:
        while True:
            message = client_socket.recv_string()
            print(f"Received request: {message}")

            if message == "Fashion":
                response = recommendation()
                client_socket.send_string(response)
            elif message == "Weather":
                response = report()
                client_socket.send_string(response)
            else:
                client_socket.send_string("Query Not Found")
    except KeyboardInterrupt:
        client_socket.close()
        print("Terminating...")


def main():
    threading.Thread(target=receive_weather_data).start()
    threading.Thread(target=handle_client_request).start()


if __name__ == "__main__":
    main()
