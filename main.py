import socket

STOP = 'send//'.encode('utf-8')
SEND = 'send/1/'.encode('utf-8')

with open('ultima_porta.txt', 'wr') as file:
    ultima_porta = file.read()

    if ultima_porta and ultima_porta != 7999:
        PORTA = str(int(ultima_porta)+1)
    else:
        PORTA = '5000'
    file.write(PORTA)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', PORTA))
server.listen()

conn1, indir1 = server.accept()
print(f'> Connessione con {indir1} avvenuta con successo!\nPORTA: {PORTA}')
conn2, indir2 = server.accept()
print(f'> Connessione con {indir2} avvenuta con successo!\nPORTA: {PORTA}')

# dopo collegamento client aspettano uno stato : STOP o SEND
# STOP: solo ascolto
# SEND: acquisizione ed invio di mossa del giocatore
# nello stato STOP il client riceve un dizionario che ridefinisce le sue variabili
# es. grid : [X, O, None, ...]

conn1.sendall(STOP)
conn2.sendall(STOP)

gioco = True
while gioco:
    conn1.sendall(SEND)
    mossa1 = conn1.recv(1024)
    conn1.sendall(STOP)
    conn2.sendall(mossa1)

