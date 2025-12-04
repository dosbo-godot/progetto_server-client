import socket

def appaiamento(_):
    print('$ COLLEGAMENTO CLIENT-CLIENT avvenuto con SUCCESSO')

def esito(args):
    e = args[0]
    print(f'$ PARTITA VINTA DA {e}')

eventi = {'0'   :   appaiamento,
          '100' :   esito}

with open('ultima_porta.txt', 'r') as file:
    PORTA = int(file.read())

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', PORTA))
print(f'\nConnessione con server su porta {PORTA} avvenuta con successo!')
print(f'\nIn attesa di un altro client su porta {PORTA} per appaiamento ...')

data = client.recv(1024).decode(encoding='utf-8')
data.split('/')

evento = data[0]
argomenti = data[1:]
eventi[evento](argomenti)
