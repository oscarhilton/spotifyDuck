from socketengine import host

class Hub:
    def __init__(self, host, port):
        self.h = host(addr=host, port=port)

        self.h.start()
        self.clients = self.h.getClients()
        while len(self.clients) == 0:
            pass

        print("ALL SET UP")
    
    def downloadAllFiles(self):
        for c in clients:
            c.write(data="HEY!", channel="Test")

    def close():
        self.h.close()