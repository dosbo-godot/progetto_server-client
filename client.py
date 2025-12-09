import socket
import tkinter

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

class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('127.0.0.1', PORTA))
        print(f'\nConnessione con server su porta {PORTA} avvenuta con successo!')
        print(f'\nIn attesa di un altro client su porta {PORTA} per appaiamento ...')

        # TABELLA EVENTI 
        self.eventi = {'0'   :   self.appaiamento,
                    '200'   :   self.turno,
                    '100'   :   self.esito}

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
        print(f'$ PARTITA VINTA DA {e}')

    @rimanda
    def turno(self, argomenti):
        griglia = argomenti[0]
        griglia = self.estraiGriglia(griglia)
        edit_mode = argomenti[1]

        self.mostraGriglia(griglia)
        if edit_mode == '1':
            mossa = self.ottieniMossa()
            self.applicaMossa(griglia, mossa)
            griglia = self.formattaGriglia(griglia)
            self.client.sendall(griglia.encode())

            with open('log.txt', 'a') as f:
                f.write(f'\CLIENT {self.marker} > {griglia}')
        
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

    def ottieniMossa(self):
        mossa = input('inserisci mossa: ')
        mossa = mossa.split(',')
        mossa = [int(x) for x in mossa]
        return mossa
    
    def chiudi(self):
        print(f'\n$ COMUNICAZIONE CON SERVER TERMINATA')
        self.client.close()

class GUI:
    def __init__(self, l = 3):
        self.paginaIniziale()
    
    def paginaIniziale(self):
        # ---- FINESTRA PRINCIPALE ----
        root = tkinter.Tk()
        root.title("Tris Online")
        root.geometry("400x500")
        root.configure(bg="#eeeeee")  # sfondo generale

        # ---- NAVBAR ----
        navbar = tkinter.Frame(root, bg="#303F9F", height=60)
        navbar.pack(fill="x")

        title_label = tkinter.Label(
            navbar,
            text="TRIS ONLINE",
            fg="white",
            bg="#303F9F",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=10)

        # ---- MESSAGGIO ----
        msg_box = tkinter.Label(
            root,
            text="",
            font=("Arial", 14),
            bg="#eeeeee"
        )
        msg_box.pack(pady=20)

        # ---- FRAME GRIGLIA ----
        griglia_frame = tkinter.Frame(root, bg="#eeeeee")
        griglia_frame.pack()

        # ---- BOTTONI 3x3 ----
        bottoni = []
        for r in range(3):
            row = []
            for c in range(3):
                bottone = tkinter.Button(
                    griglia_frame,
                    text="",
                    width=6,
                    height=3,
                    font=("Arial", 24),
                    bg="white"
                )
                bottone.grid(row=r, column=c, padx=5, pady=5)
                row.append(bottone)
            bottoni.append(row)

        # Avvio finestra
        root.mainloop()

with open('ultima_porta.txt', 'r') as file:
    PORTA = int(file.read())

# MAIN
g = GUI()
#c = Client()
