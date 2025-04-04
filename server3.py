import socket
import threading
# the host and port for the server to listen on
HOST = '0.0.0.0'  
PORT = 12345
# declare "clients" to store connected clients and declare the default channel
clients = {}  
channels = {"general": set()}  
# this function broadcasts the message to all the users in a channel
def broadcast(message, channel, sender=None):
    #checks if the channel exists, gets the socket and formats and sends the message
    if channel in channels:
        for nickname in channels[channel]:
            if nickname != sender:  
                client_socket = clients.get(nickname)
                if client_socket:
                    send_message(client_socket, f"[{channel}] {sender}: {message}" if sender else message)
# function to send private messages
def private_message(sender, recipient, message):
    recipient_socket = clients.get(recipient)
    #gets the receipient's socket and sends the message to both him and the sender itself
    if recipient_socket:
        send_message(recipient_socket, f"[PRIVATE] {sender}: {message}")
        send_message(clients[sender], f"[PRIVATE to {recipient}]: {message}")
    else:
        send_message(clients[sender], f"User '{recipient}' not found!")
#function to send the message
def send_message(client_socket, message):
    try:
        client_socket.send(message.encode('utf-8')) #encodes and sends
    except:
        pass
#this function handles messages from a client
def handle_client(client_socket, nickname):
    #uses the default channel and adds the client
    current_channel = "general"
    channels[current_channel].add(nickname)
    #the first text appears for the user, and the second one to all the users from the channel
    send_message(client_socket, f"{nickname} joined the chat!")
    broadcast(f"{nickname} joined #{current_channel}.", current_channel)
    try:
        while True:
            #simply receives the message
            message = client_socket.recv(1024).decode('utf-8').strip()
            if not message:
                break
            #if the client switches channels
            if message.startswith("/join "):  
                new_channel = message.split(" ", 1)[1].strip()
                if new_channel not in channels:
                    channels[new_channel] = set() #it creates a new one if it does not exist
                channels[current_channel].discard(nickname) #client leaves the current one
                channels[new_channel].add(nickname) # and joins the new one
                current_channel = new_channel # the channel and its users are updated with similar messaes as before
                send_message(client_socket, f"You joined #{current_channel}")
                broadcast(f"{nickname} has joined #{current_channel}.", current_channel)
            # function for a private message
            elif message.startswith("/msg "): 
                parts = message.split(" ", 2)
                if len(parts) == 3: # the message has the right format to be sent
                    recipient, msg = parts[1], parts[2]
                    private_message(nickname, recipient, msg)
                else:
                    send_message(client_socket, "Invalid format.")
            #checks the existing online users
            elif message == "/users":  
                online_users = ", ".join(clients.keys())
                send_message(client_socket, f"Online users: {online_users}")
            # disconnect from the server
            elif message.startswith("/exit"): 
                send_message(client_socket, "Bye bye!")
                break
            else:  
                broadcast(message, current_channel, sender=nickname)
    except:
        pass
    finally:
        disconnect_client(nickname, current_channel) 
# this function removes a disconnected client
def disconnect_client(nickname, channel):
    if nickname in clients:
        clients[nickname].close() #it closes the connection
        del clients[nickname] # and removes it from "clients"
    if nickname in channels[channel]:
        channels[channel].remove(nickname) # also removes it from the channel
    broadcast(f"{nickname} has left #{channel}.", channel) #update the channel
    print(f"{nickname} disconnected.")

def start_server():
    # a socket object is created for the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server running on {HOST}:{PORT}")
    while True:
        #accepts the new connection and asks the nickname
        client_socket, addr = server_socket.accept()
        client_socket.send("Enter your nickname: ".encode('utf-8'))
        nickname = client_socket.recv(1024).decode('utf-8').strip()
        #the nickname should be valid and unique
        if nickname in clients or not nickname:
            client_socket.send("Invalid or duplicate nickname. Connection closed.".encode('utf-8'))
            client_socket.close()
            continue

        clients[nickname] = client_socket #client is added to "clients"
        print(f"{nickname} connected from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, nickname), daemon=True).start()
if __name__ == "__main__":
    start_server()