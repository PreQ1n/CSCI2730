import socket
import json
import threading

class Connect:
    def __init__(self, ip, port, callback):
        self.ip = ip
        self.port = port
        self.socket = None
        self.alive = False
        self.callback = callback

    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip, self.port))
            self.alive = True
            threading.Thread(target=self.receiving, daemon=True).start()
            return True
        except Exception as e:
            print(f"connect to {self.ip}:{self.port} fail")
            return False

    def accept_connection(self, conn):
        self.socket = conn
        self.alive = True   
        threading.Thread(target = self.receiving, daemon = True).start() #we will just create a thread for each connection, since it is a small project
                                                        #we can use event loop for further optimization

    def close(self):
        self.alive = False
        if self.socket:
            self.socket.close()

    def send(self, message):
        if not self.alive:
            return

        try:
            data = json.dumps(message).encode() + b"\n"
            self.socket.sendall(data)
            return True
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError) as e:
            self.alive = False
            return False

    def receiving(self):
        buffer = b""
        while(self.alive):
            try:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    data, buffer = buffer.split(b"\n", 1)
                    if data.strip():
                        message = json.loads(data.decode())
                        self.callback(message, self)
            except Exception as e:
                print(f"[recv] error: {type(e).__name__}: {e}")
                break

    def close(self):
        self.alive = False
        sock = self.socket
        self.socket = None

        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass
            


                

