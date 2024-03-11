import socket
import cv2
import pickle
import struct
import ssl

def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_ip = '192.168.238.229'
    host_name = 'localhost'
    port = 9998

    # Configure SSL context
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_OPTIONAL
    ssl_context.load_verify_locations(cafile='server.crt')

    # Wrap the socket with SSL/TLS
    client_socket = ssl_context.wrap_socket(client_socket, server_hostname=host_name)
    client_socket.connect((host_ip, port))

    try:
        while True:
            data = b""
            payload_size = struct.calcsize("!I")
            while len(data) < payload_size:
                packet = client_socket.recv(4*1024)
                if not packet:
                    break
                data += packet
            if not packet:
                break

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("!I", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4*1024)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            cv2.imshow("RECEIVING VIDEO", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    finally:
        client_socket.close()

if __name__ == "__main__":
    client()