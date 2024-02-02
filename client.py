import socket
import sys


def connect_and_send_info(server_ip, server_port):
    tcp_sock = None

    try:
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.connect((server_ip, server_port))

        data_from_server = tcp_sock.recv(1024).decode()
        address, port, message = data_from_server.split(',')

        if address and port:
            print(f"Your Address: {address}:{port}")
        else:
            print("Failed to receive client information.")

        chat_room_name, max_participants = get_chatroom_info()
        send_chatroom_info(tcp_sock, chat_room_name, max_participants)

        print("---------------------------------")
        print(message)
        print("---------------------------------")

    except KeyboardInterrupt:
        print('\nUser interrupted.')

    except socket.error as err:
        print(f'Socket error: {err}.')
        sys.exit(1)

    finally:
        if tcp_sock is not None:
            tcp_sock.close()


def get_chatroom_info():
    chat_room_name = input("Room Name (Enter a name for the chat room): ")
    maximum_participants = input("Maximum Participants (Enter the maximum number of participants): ")

    while not maximum_participants.isnumeric():
        print("Invalid value for maximum participants.Please enter again.")
        maximum_participants = input("Maximum Participants: ")

    return chat_room_name, maximum_participants


def send_chatroom_info(tcp_sock, chat_room_name, max_participants):
    data = f"{chat_room_name}:{max_participants}"
    encoded_data = data.encode()
    tcp_sock.sendall(encoded_data)


def exchange_message_with_server(server_ip, server_port):
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        udp_sock.bind((server_ip, server_port))

        while True:
            message = input('Enter a message (or "exit" to exit): ')

            if message.lower() == "exit":
                break

            udp_sock.sendto(message.encode(), (server_ip, server_port))

            data, server = udp_sock.recvfrom(4096)
            print(f'Received from {server}: {data.decode()}')

    except KeyboardInterrupt:
        print('\nUser interrupted')

    except socket.error as err:
        print(f'Socket error: {err}')
        sys.exit(1)

    finally:
        print('\nClosing socket...')
        udp_sock.close()


def main():
    server_ip = "127.0.0.1"
    server_port = 9001

    connect_and_send_info(server_ip, server_port)
    exchange_message_with_server(server_ip, server_port)


if __name__ == '__main__':
    main()
