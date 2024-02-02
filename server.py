import socket
import sys
import threading
import asyncio


class ChatRoom(object):
    def __init__(self, room_name, max_participants):
        self.room_name = room_name
        self.max_participants = max_participants
        self.participants = {}
        self.message_history = []
        self.host = None
        self.lock = threading.Lock()

    def add_participants(self, client_key, client):
        with self.lock:
            self.participants[client_key] = client

    def remove_participants(self, client_key):
        with self.lock:
            del self.participants[client_key]

    def get_participants(self):
        with self.lock:
            return list(self.participants.values())

    def get_max_participants(self):
        with self.lock:
            return self.max_participants

    def get_host(self):
        with self.lock:
            return self.host

    def set_host(self, client):
        with self.lock:
            self.host = client

    def add_message(self, message):
        with self.lock:
            self.message_history.append(message)


class ChatClient(object):
    def __init__(self, connection, address, port):
        self.connection = connection
        self.address = address
        self.port = port

    def send_message(self, message):
        pass

    def receive_message(self):
        pass


async def start_server(server_ip, server_port):
    chat_rooms = {}

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind((server_ip, server_port))
    tcp_sock.listen(1)

    while True:
        print('Waiting connection from client...')
        client, client_address = await loop.sock_accept()
        address, port = client_address
        success_message = "Successfully joined the chatroom!"

        client_info = f"{address},{port},{success_message}"
        client.send(client_info.encode())

        chat_client = ChatClient(client, address, port)
        loop.create_task(handle_client(chat_client, chat_rooms))

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server("127.0.0.1", 9001))
except OSError:
    print("Address already in use. Try again later.")
    sys.exit(1)


def handle_client(chat_client, chat_rooms):
    try:
        while True:
            data = chat_client.connection.recv(1024).decode()

            if not data:
                break

            chat_room_name, max_participants = data.split(':')
            max_participants = int(max_participants)

            if chat_room_name not in chat_rooms:
                chat_room = ChatRoom(chat_room_name, max_participants)
                chat_rooms[chat_room_name] = chat_room

            chat_room = chat_rooms[chat_room_name]
            client_key = f"{chat_client.connection.getpeername()[0]}:{chat_client.connection.getpeername()[1]}"

            print(f"Successfully created a chatroom! [Name: {chat_room_name}, Max Participants: {max_participants}]")

            if len(chat_rooms) <= max_participants:
                chat_room.add_participants(client_key, chat_client.connection)
            else:
                message = "Maximum participants reached in this chat room."
                print(message)

            if chat_room.get_host() is None:
                chat_room.set_host(chat_client.connection)

    except Exception as e:
        print(f"\nClient Error: {e}")
        sys.exit(1)

    finally:
        chat_client.connection.close()


def handle_udp_socket(server_ip, server_port):
    print("hhh")
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        udp_sock.bind((server_ip, server_port))

        while True:
            message, client_address = udp_sock.recvfrom(1024)
            print(message.decode())

            if message:
                sent = udp_sock.sendto(message, client_address)

    except KeyboardInterrupt:
        print('\nUser interrupted.')

    except OSError:
        print("Address already in use. Try again later.")
        sys.exit(1)

    finally:
        print('Closing socket...')
        udp_sock.close()


def main():
    server_ip = "127.0.0.1"
    server_port = 9001

    start_server(server_ip, server_port)
    handle_udp_socket(server_ip, server_port)


if __name__ == "__main__":
    main()
