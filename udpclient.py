import socket

HOST = '127.0.0.1'
PORT = 5042

def msg(buf):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(buf, (HOST, PORT))
    return sock.recv(1024)

if __name__ == '__main__':
    with open('./packet_example.bin', 'rb') as f:
        print(msg(f.read()))
