import socket
import cv2
import pickle
import struct
import threading
import ssl

def handle_client(client_socket, addr):
    print('GOT CONNECTION FROM:', addr)
    try:

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow backend on Windows
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            print("Error: Failed to open camera.")
            return

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to read frame.")
                break

            data = pickle.dumps(frame)
            message_size = struct.pack("!L", len(data))
            client_socket.sendall(message_size + data)

            cv2.imshow('TRANSMITTING VIDEO', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        cap.release()
        client_socket.close()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '0.0.0.0'
    port = 9998
    socket_address = (host_ip, port)

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    server_socket = ssl_context.wrap_socket(server_socket, server_side=True)

    try:
        server_socket.bind(socket_address)
        server_socket.listen(5)
        print("LISTENING AT:", socket_address)

        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()

    except Exception as e:
        print(f"Error in server: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server()
