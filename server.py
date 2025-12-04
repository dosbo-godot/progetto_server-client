import socket

STOP = '900/'.encode('utf-8')
SEND = '900/1'.encode('utf-8')
TURNO = '200/'.encode('utf-8')
ESITO = '100/'.encode('utf-8')
MARKER = '0/'.encode('utf-8')

def getPorta() -> int:
    with open('ultima_porta.txt', 'w+') as file:
        ultima_porta = file.read()

        if ultima_porta and ultima_porta != '7999':
            PORTA = int(ultima_porta) + 1
        else:
            PORTA = 5000
        file.write(str(PORTA))
        print(PORTA)
    return PORTA

def elementiUguali(lista):
    return len(set(lista)) == 1

class Server:
    def __init__(self) -> None:
        self.PORTA = getPorta()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', self.PORTA))
        print(f'Server in ascolto su porta {self.PORTA}')
        self.server.listen()

        # connessione client
        self.conn1, self.ip1 = self.server.accept()
        print(f'> Connessione con {self.ip1} avvenuta con successo!')
        self.conn2, self.ip2 = self.server.accept()
        print(f'> Connessione con {self.ip2} avvenuta con successo!')
    
    def __repr__(self) -> str:
        s = f'\n\n======== SERVER SU PORTA {self.PORTA} ========'
        c1 = f'\n\n>\tCONN1\t:\t{self.conn1}'
        p1 = f'\n>\tIPv4 1\t:\t{self.ip1}'
        c2 = f'\n\n>\tCONN2\t:\t{self.conn2}'
        p2 = f'\n>\tIPv4 2\t:\t{self.ip2}'

        return s+c1+p1+c2+p2
    
    def assetoIniziale(self) -> None:
        # messaggio pairing riuscito
        self.conn1.sendall(MARKER + '1')
        self.conn2.sendall(MARKER + '2') 

        # attesa messaggio di conferma
        while True:
            conferma1 = self.conn1.recv(64).decode()
            conferma2 = self.conn2.recv(64).decode()

            if conferma1 and conferma2:
                break

        griglia = self.nuovaGriglia()
        self.gameLoop(griglia)
    
    def nuovaGriglia(self, l = 3) -> list[list[str]]:
        #[[0, 0, 0],
        # [0, 0, 2],
        # [0, 0, 0]]

        riga = ['0' for _ in range(l)]
        griglia = [riga for _ in range(l)]
        return griglia
    
    def analisiGriglia(self, griglia):
        vincitore = ''
        for i, riga in enumerate(griglia):
            # controllo righe
            if elementiUguali(riga) and riga[0] != '0':
                vincitore = riga[0]
                print(riga)
    
            # controllo colonne
            colonna = [r[i] for r in griglia]
            if elementiUguali(colonna) and colonna[0] != '0':
                vincitore = colonna[0]
                print(colonna)
    
        # controllo diagonali
        diagonale1 = [griglia[k][k] for k in range(len(griglia))]
        diagonale2 = [griglia[k][(k*(-1))-1] for k in range(len(griglia))]
    
        if elementiUguali(diagonale1) and diagonale1[0] != '0':
            vincitore = diagonale1[0]
        elif elementiUguali(diagonale2) and diagonale2[0] != '0':
            vincitore = diagonale2[0]
            print(diagonale2)
    
        if vincitore:
            self.conn1.sendall(ESITO + vincitore)
            self.conn2.sendall(ESITO + vincitore)
    
        print(f'vincitore: {vincitore}')

    def gameLoop(self, griglia) -> None:

        self.conn1.sendall(SEND)
        griglia = self.conn1.recv(1024)
        self.conn1.sendall(STOP)
        self.conn2.sendall(griglia)

        self.conn1.sendall(SEND)
        griglia = self.conn1.recv(1024)
        self.conn1.sendall(STOP)
        self.conn2.sendall(griglia)

# dopo collegamento client aspettano uno stato : STOP o SEND
# STOP: solo ascolto
# SEND: acquisizione ed invio di mossa del giocatore
# nello stato STOP il client riceve un dizionario che ridefinisce le sue variabili
# es. grid : [X, O, None, ...]

# MAIN



'''gioco = True
while gioco:
    conn1.sendall(SEND)
    mossa1 = conn1.recv(1024)
    conn1.sendall(STOP)
    conn2.sendall(mossa1)'''

