import socket

STOP = '900/'.encode('utf-8')
SEND = '900/1'.encode('utf-8')
TURNO = '200/'.encode('utf-8') # griglia, editMode
ESITO = '100/'.encode('utf-8') # 1 | vincita X ; 2 | vincita O ; 3 | pareggio
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

        # connessione clients
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

    def controllaArray(self, lista, esito) -> str:
        if elementiUguali(lista) and lista[0] != '0':
            return lista[0]
        return esito
    
    def analisiGriglia(self, griglia) -> str:
        esito = ''
        conta_vuoti = 0
        
        for i, riga in enumerate(griglia):
            numero_vuoti = riga.count('0')
            conta_vuoti += numero_vuoti

            esito = self.controllaArray(riga, esito)
    
            # controllo colonne
            colonna = [r[i] for r in griglia]
            esito = self.controllaArray(colonna, esito)
    
        # controllo diagonali
        diagonale1 = [griglia[k][k] for k in range(len(griglia))]
        esito = self.controllaArray(diagonale1, esito)
        
        diagonale2 = [griglia[k][(k*(-1))-1] for k in range(len(griglia))]
        esito = self.controllaArray(diagonale2, esito)

        # controllo pareggio
        if not conta_vuoti:
            esito = '3'

        print(f'$ esito: {esito}')
        return esito

    def formattaGriglia(self, griglia) -> str:
        for riga in griglia:
            formatG.append(','.join(riga))
        formatG = ';'.join(formatG)
        return formatG

    def estraiGriglia(self, grigliaF):
        griglia = []
        for rigaF in grigliaF.split(';'):
            griglia.append(rigaF.split(',')
        return griglia

    def gameLoop(self, griglia) -> None:
        while game:
            griglia = self.formattaGriglia(griglia)

            # TURNO CLIENT 1
            self.conn1.sendall(f'{TURNO}{griglia}/1') # invio griglia e attesa di risposta 
            self.conn2.sendall(f'{TURNO}{griglia}/0') # invio griglia per solo display
            
            griglia = self.conn1.recv(1024).decode()
            self.analisiGriglia(griglia)
            griglia = self.formattaGriglia(griglia)

            # TURNO CLIENT 2
            self.conn2.sendall(TURNO + griglia)
            griglia = self.conn2.recv(1024).decode()
            griglia = self.formattaGriglia(griglia)
            self.conn1.sendall(griglia)
        
# dopo collegamento client aspettano uno stato : STOP o SEND
# STOP: solo ascolto
# SEND: acquisizione ed invio di mossa del giocatore
# nello stato STOP il client riceve un dizionario che ridefinisce le sue variabili
# es. grid : [X, O, None, ...]

# MAIN

# self.conn2.sendall(ESITO + vincitore)



'''gioco = True
while gioco:
    conn1.sendall(SEND)
    mossa1 = conn1.recv(1024)
    conn1.sendall(STOP)
    conn2.sendall(mossa1)'''

