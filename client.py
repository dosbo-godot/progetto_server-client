import socket
import tkinter
import threading
import queue
import time

_sendall_originale = socket.socket.sendall

def sendall_decorato(self, data, *args, **kwargs):
    with open('log.txt', 'a') as f:
        f.write(f'\nCLIENT > {data}')
    return _sendall_originale(self, data, *args, **kwargs)

socket.socket.sendall = sendall_decorato

def rimanda(func) -> callable:
    def nuovaFunc(self, *args, **kwargs):
        risultato = func(self, *args, **kwargs)
        self.statoFondamentale()
        return risultato
    return nuovaFunc

class Client(threading.Thread):
    def __init__(self):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('127.0.0.1', PORTA))
        print(f'\nConnessione con server su porta {PORTA} avvenuta con successo!')
        print(f'\nIn attesa di un altro client su porta {PORTA} per appaiamento ...')

        # TABELLA EVENTI 
        self.eventi = {'0'   :   self.appaiamento,
                    '200'   :   self.turno,
                    '100'   :   self.esito}
    
    def run(self):
        self.statoFondamentale()

    def statoFondamentale(self):
        # ATTESA
        data = self.client.recv(128).decode(encoding='utf-8')
        if not data:
            self.chiudi()
            return

        data = data.split('/')
        evento = data[0]
        argomenti = data[1:]

        # CHIAMO COMANDO
        self.eventi[evento](argomenti)
    
    @rimanda
    def appaiamento(self, argomenti):
        self.marker = argomenti[0]
        self.client.sendall('OK'.encode())
        print('$ COLLEGAMENTO CLIENT-SERVER-CLIENT avvenuto con SUCCESSO')


    @rimanda
    def esito(self, argomenti):
        e = argomenti[0]
        griglia = argomenti[1]
        griglia = self.estraiGriglia(griglia)
        Q.put(('esito', (e, self.marker, griglia)))
        

    @rimanda
    def turno(self, argomenti):
        griglia = argomenti[0]
        griglia = self.estraiGriglia(griglia)
        edit_mode = argomenti[1]

        Q.put(('griglia', (griglia, edit_mode)))
        if edit_mode == '1':
            mossa = self.getMossa()
            print(f'$ MOSSA: {mossa}')
            self.applicaMossa(griglia, mossa)
            griglia = self.formattaGriglia(griglia)
            self.client.sendall(griglia.encode())

            with open('log.txt  ', 'a') as f:
                f.write(f'\CLIENT {self.marker} > {griglia}')
    
    def getMossa(self):
        while True:
            tipo, dati = Q.get()
            if tipo == "mossa":
                return dati  # (riga, colonna)
            else:
                Q.put((tipo, dati))  # rimetti tutto il resto
                time.sleep(0.01)      # piccola pausa per evitare busy-waiting aggressivo
        
    def mostraGriglia(self, griglia):
        for i, riga in enumerate(griglia):
            riga_format = '\t|\t'.join(riga)
            print(riga_format)

            if i != (len(griglia)-1):
                print('-'*40)
    
    def applicaMossa(self, griglia, mossa):
        riga = mossa[0]
        colonna = mossa[1]

        griglia[riga][colonna] = self.marker
    
    def formattaGriglia(self, griglia) -> str:
        # 0, 0, 1; 1, 2, 0; 0, 0, 0
        formatG = []
        for riga in griglia:
            formatG.append(','.join(riga))
        formatG = ';'.join(formatG)
        return formatG

    def estraiGriglia(self, grigliaF) -> list[list[str]]:
        griglia = []
        for rigaF in grigliaF.split(';'):
            griglia.append(rigaF.split(','))
        return griglia

    '''
    def ottieniMossa(self):
        mossa = input('inserisci mossa: ')
        mossa = mossa.split(',')
        mossa = [int(x) for x in mossa]
        return mossa
    '''
    
    def chiudi(self):
        print(f'\n$ COMUNICAZIONE CON SERVER TERMINATA')
        self.client.close()

class GUI:
    def __init__(self, l = 3):
        self.l = l
        self.paginaIniziale()
    
    def paginaIniziale(self) -> None:
        self.edit_mode = 0

        # ---- FINESTRA PRINCIPALE ----
        self.root = tkinter.Tk()
        self.root.title("Tris Online")
        self.root.geometry("450x600")
        self.root.configure(bg="#eeeeee")  # sfondo generale

        # ---- NAVBAR ----
        navbar = tkinter.Frame(self.root, bg="#303F9F", height=60)
        navbar.pack(fill="x")

        label_titolo = tkinter.Label(
            navbar,
            text="TRIS ONLINE",
            fg="white",
            bg="#303F9F",
            font=("Arial", 24, "bold")
        )
        label_titolo.pack(pady=10)

        # ---- MESSAGGIO ----
        self.label_msg = tkinter.Label(
            self.root,
            text="",
            font=("Arial", 14),
            bg="#eeeeee"
        )
        self.label_msg.pack(pady=20)

        # ---- FRAME GRIGLIA ----
        griglia_frame = tkinter.Frame(self.root, bg="#eeeeee")
        griglia_frame.pack()

        # ---- BOTTONI 3x3 ----
        self.bottoni = []
        for i in range(self.l):
            riga = []
            for j in range(self.l):
                bottone = BottoneGriglia(griglia_frame, (i, j), self.bottoneSelezionato)
                riga.append(bottone)
            self.bottoni.append(riga)

        self.root.after(50, self.controllaQueue)

        self.root.mainloop()

    def controllaQueue(self) -> None:
        if not Q.empty():
            data = Q.get()

            if data[0] == 'griglia':
                argomenti = data[1]
                griglia = argomenti[0]
                self.edit_mode = argomenti[1]

                self.disegnaGriglia(griglia)
            
            elif data[0] == 'esito':
                esito = data[1]
                self.disegnaEsito(esito)
        self.root.after(50, self.controllaQueue)

    
    def bottoneSelezionato(self, riga, colonna, marker) -> None:
        selezionato = (riga, colonna)
        if not marker:
            Q.put(('mossa', selezionato))
    
    def disegnaGriglia(self, griglia) -> None:
        print(f'$ GRIGLIA : {griglia}')
        if self.edit_mode == '1':
            self.label_msg.config(text = 'E\' IL TUO TURNO. SELEZIONA UNO SPAZIO.')
        else: 
            self.label_msg.config(text = 'E\' IL TURNO DELL\'AVVERSARIO. ATTENDI...')

        l = len(griglia)
        for i in range(l):
            for j in range(l):
                bottone : BottoneGriglia = self.bottoni[i][j]
                self.marker = griglia[i][j]
                
                if self.marker == '1':
                    bottone.configuraTesto('X')
                elif self.marker == '2':
                    bottone.configuraTesto('O')
    
    def disegnaEsito(self, e) -> None:
        esito = e[0]
        marker = e[1]
        griglia = e[2]

        self.disegnaGriglia(griglia)
        if esito == marker:
            self.label_msg.config(text='PARTITA VINTA. COMPLIMENTI!')
        elif esito == '3':
            self.label_msg.config(text='PATTA!')
        else:
            self.label_msg.config(text='PARTITA PERSA :(')

    
class BottoneGriglia:

    def __init__(self, root, coord, func):
        self.riga = coord[0]
        self.colonna = coord[1]
        self.func = func
        self.bottone = tkinter.Button(
            root,
            text="",
            width=6,
            height=3,
            font=("Arial", 24),
            bg="white",
            command = self.premuto
        )
        self.bottone.grid(row=self.riga, column=self.colonna, padx=5, pady=5)
    
    def __repr__(self):
        return f'Bottone ({self.riga}, {self.colonna})'

    def premuto(self):
        self.func(self.riga, self.colonna, self.bottone['text'])
    
    def configuraTesto(self, testo):
        self.bottone.config(text = testo)



with open('ultima_porta.txt', 'r') as file:
    PORTA = int(file.read())

# MAIN
Q = queue.Queue()

c = Client()
c.start()

g = GUI()
