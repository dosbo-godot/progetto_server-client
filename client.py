import socket

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
                    '100'   :   self.turno,
                    '200'   :   self.esito}

    def statoFondamentale(self):
        # ATTESA
        data = self.client.recv(128).decode(encoding='utf-8')

        data.split('/')
        evento = data[0]
        argomenti = data[1:]

        # CHIAMO COMANDO
        self.eventi[evento](argomenti)
    
    @rimanda
    def appaiamento(self, argomenti):
        self.marker = argomenti[0]
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
        if edit_mode:
            mossa = self.ottieniMossa()
            griglia = self.applicaMossa(griglia, mossa)
            griglia = self.formattaGriglia(griglia)
            self.client.sendall(griglia)
        
    def mostraGriglia(self, griglia):
        for i, riga in enumerate(griglia):
            riga_format = '\t|\t'.join(riga)
            print(riga_format)

            if i != (len(griglia)-1):
                print('-'*20)
    
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



with open('ultima_porta.txt', 'r') as file:
    PORTA = int(file.read())

c = Client()
