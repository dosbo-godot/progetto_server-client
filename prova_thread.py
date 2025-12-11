import threading
import queue

class Rete(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        self.stato()
    
    def stato(self):
        while True:
            num = input('numero? ')
            q.put(num)


class Gui():
    def __init__(self):
        self.display()
    
    def display(self):
        while True:
            num = q.get()
            pari = 'PARIIII' if int(num)%2 ==0 else 'dispari D:'
            print(f'Numero bello!!! {num} ({pari})')



q = queue.Queue()
r = Rete()
r.start()
g = Gui()

