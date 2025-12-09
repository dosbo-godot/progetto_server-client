import socket

_sendall_originale = socket.socket.sendall

def sendall_decorato(self, data, *args, **kwargs):
    with open('log.txt', 'a') as f:
        f.write(f'\nSERVER > {data}')
    return _sendall_originale(self, data, *args, **kwargs)

socket.socket.sendall = sendall_decorato

STOP = '900/'
SEND = '900/1'
TURNO = '200'# griglia, editMode
ESITO = '100' # 1 | vincita X ; 2 | vincita O ; 3 | pareggio
MARKER = '0'

def getPorta() -> int:
    with open('ultima_porta.txt') as file:
        ultima_porta = file.read()
    with open('ultima_porta.txt', 'w') as file:
        if ultima_porta and ultima_porta != '7999':
            PORTA = int(ultima_porta) + 1
        else:
            PORTA = 5000
        file.write(str(PORTA))
    return PORTA

def elementiUguali(lista):
    return len(set(lista)) == 1

def formatMesg(codice, *args):
    argomentiF = [str(x) for x in args]
    argomentiF = '/'.join(argomentiF)
    messaggio = f'{codice}/{argomentiF}'

    return messaggio.encode()

class Server:
    def __init__(self) -> None:
        self.PORTA = getPorta()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(True)
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
    
    def assettoIniziale(self) -> None:
        # messaggio pairing riuscito
        self.conn1.sendall(formatMesg(MARKER, 1))
        self.conn2.sendall(formatMesg(MARKER, 2))

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
        risultato = ''
        conta_vuoti = 0
        
        for i, riga in enumerate(griglia):
            numero_vuoti = riga.count('0')
            conta_vuoti += numero_vuoti

            risultato = self.controllaArray(riga, risultato)
    
            # controllo colonne
            colonna = [r[i] for r in griglia]
            risultato = self.controllaArray(colonna, risultato)
    
        # controllo diagonali
        diagonale1 = [griglia[k][k] for k in range(len(griglia))]
        risultato = self.controllaArray(diagonale1, risultato)
        
        diagonale2 = [griglia[k][(k*(-1))-1] for k in range(len(griglia))]
        risultato = self.controllaArray(diagonale2, risultato)

        # controllo pareggio
        if conta_vuoti == 0:
            risultato = '3'

        print(f'$ esito: {risultato}')
        if risultato:
            self.conn1.sendall(formatMesg(ESITO, risultato))
            self.conn2.sendall(formatMesg(ESITO, risultato))
        return risultato

    def formattaGriglia(self, griglia) -> str:
        # 0, 0, 1; 1, 2, 0; 0, 0, 0
        formatG = []
        for riga in griglia:
            formatG.append(','.join(riga))
        formatG = ';'.join(formatG)
        return formatG

    def estraiGriglia(self, grigliaF):
        griglia = []
        for rigaF in grigliaF.split(';'):
            griglia.append(rigaF.split(','))
        return griglia

    def gameLoop(self, griglia) -> None:
        continuo = True
        while continuo:
            # TURNO CLIENT 1
            griglia = self.formattaGriglia(griglia)

            self.conn1.sendall(formatMesg(TURNO, griglia, 1)) # invio griglia e attesa di risposta 
            self.conn2.sendall(formatMesg(TURNO, griglia, 0)) # invio griglia per solo display
            
            griglia = self.conn1.recv(128).decode()
            griglia  = self.estraiGriglia(griglia)
            game = self.analisiGriglia(griglia)
            if game: break

            # TURNO CLIENT 2
            griglia = self.formattaGriglia(griglia)

            self.conn1.sendall(formatMesg(TURNO, griglia, 0)) # invio griglia e attesa di risposta 
            self.conn2.sendall(formatMesg(TURNO, griglia, 1)) # invio griglia per solo display
            
            griglia = self.conn2.recv(128).decode()
            griglia  = self.estraiGriglia(griglia)
            game = self.analisiGriglia(griglia)
            if game: break
        self.arresta()
    
    def arresta(self):
        print('$ partita finita')
        self.conn1.close()
        self.conn2.close()
        self.server.close()

# main

with open('log.txt', 'w'):
    pass
s = Server()
print(s)
s.assettoIniziale()