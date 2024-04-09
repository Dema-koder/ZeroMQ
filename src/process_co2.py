import zmq
import json

WEATHER_INPUT_PORT = 5555
IP_ADD = '127.0.0.1'


def main():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{IP_ADD}:{WEATHER_INPUT_PORT}")

    socket.setsockopt_string(zmq.SUBSCRIBE, "co2")

    try:
        with open('co2_data.log', 'a') as log_file:
            while True:
                data = socket.recv_string()
                log_file.write(f"{data[4:]}\n")
                print(f"Received weather data: {data}")
                co2_data = json.loads(data[4:])

                co2_level = co2_data["co2"]

                if co2_level > 400:
                    print("Danger Zone! Please do not leave home")
    except KeyboardInterrupt:
        print("Terminating data_processor")


if __name__ == "__main__":
    main()
