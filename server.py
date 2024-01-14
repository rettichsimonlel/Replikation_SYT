import socket
import threading
import sqlite3

# Server configuration
HOST = '127.0.0.1'
PORT = 5555

# Socket setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# Database setup
def create_database_connection(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    return conn

# Sync the database
def sync_database(db_write, db_read):
    # Lock to ensure exclusive access to the databases
    with threading.Lock():
        # Connect to the write database
        conn_write = create_database_connection(db_write)
        cursor_write = conn_write.cursor()

        # Connect to the read database
        conn_read = create_database_connection(db_read)
        cursor_read = conn_read.cursor()

        try:
            # Read data from the write database
            cursor_write.execute('SELECT * FROM data')
            data_to_sync = cursor_write.fetchall()

            # Delete old data from the read database
            cursor_read.execute('DELETE FROM data')
            conn_read.commit()

            # Write data to the read database
            cursor_read.executemany('INSERT INTO data (value) VALUES (?)', [(row[1],) for row in data_to_sync])
            conn_read.commit()

        finally:
            # Close connections
            conn_write.close()
            conn_read.close()

# Client handling function
def handle_client(client_socket):
    try:
        while True:
            # Read or Write database selection
            selection = client_socket.recv(1024).decode('utf-8')
            print(f"selection r/w: {selection}")

            if selection == 'r':
                print("In reading")
                sync_database('write_database.db', 'read_database.db')

                db_conn_read = create_database_connection('read_database.db')
                db_cursor_read = db_conn_read.cursor()

                # Read data from the write database and send it to the client
                db_cursor_read.execute('SELECT * FROM data')
                result_read = db_cursor_read.fetchall()
                client_socket.send(str(result_read).encode('utf-8'))

                db_conn_read.close()

            elif selection == 'w':
                print("In writing")
                db_conn_write = create_database_connection('write_database.db')
                db_cursor_write = db_conn_write.cursor()

                data = client_socket.recv(1024).decode('utf-8')
                print(f"data into database: {data}")

                # Write data to the write database
                db_cursor_write.execute('INSERT INTO data (value) VALUES (?)', (data,))
                db_conn_write.commit()
                print(f"Value: {data} written in the database")

                sync_database('write_database.db', 'read_database.db')

                # Read data from the write database and send it to the client
                db_cursor_write.execute('SELECT * FROM data')
                result_write = db_cursor_write.fetchall()
                client_socket.send(str(result_write).encode('utf-8'))

                db_conn_write.close()

            else:
                raise ValueError("Invalid selection")
                break

    except KeyboardInterrupt:
        print("Server interrupted. Closing socket...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

# Accept and handle incoming connections
try:
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

except KeyboardInterrupt:
    print("Server interrupted. Closing socket...")
finally:
    # Close the server socket
    server_socket.close()

