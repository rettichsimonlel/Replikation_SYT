import socket

# Client configuration
HOST = '127.0.0.1'
PORT = 5555

# Socket setup
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    while True:
        # Select Read or Write database
        selection = input("Choose database (r for read, w for write): ")
        client_socket.send(selection.encode('utf-8'))

        if selection == 'w':
            # Read input from the user
            data = input("Enter data to be written to the server: ")

            # Send data to the server
            client_socket.send(data.encode('utf-8'))

            # Receive and print the synchronized data from the server
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Synchronized data from server: {response}")

        elif selection == 'r':
            # Receive and print data from the server
            response = client_socket.recv(1024).decode('utf-8')
            print(f"All the data: {response}")

except KeyboardInterrupt:
    print("Server interrupted. Closing socket...")
finally:
    # Close the server socket
    client_socket.close()
