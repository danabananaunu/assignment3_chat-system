#no AI was used for this assignment
import socket
import threading
# the IP address and port for connecting to the server
SERVER_IP = "127.0.0.1"  
SERVER_PORT = 12345
#this function receives messages from the server
def receive_messages(client_socket):
    while True:
        try:
            # here a message from the server is received and decoded
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message) 
        except:
            # disconnection is handled
            print("Disconnected from server.")
            client_socket.close()
            break
# this function sends a message to the server
def send_message(client_socket, message):
    client_socket.send(message.encode('utf-8')) #the message is encoded and then sent
#this is a menu with all the functionalities that the system is required to have
def display_menu():
    print("\n[MENU]")
    print("1. Send a public message")
    print("2. Send a private message")
    print("3. Switch to a channel")
    print("4. List online users")
    print("5. Exit")

def start_client():
    #a socet object is created for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT)) # and connection to the server
    #the system first asks for a nickname and sends it to the server
    nickname = input("Enter your nickname: ").strip()
    client_socket.send(nickname.encode('utf-8'))
    # a new thred to receive messages
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
    #the default channel for the user until they input otherwise
    current_channel = "general" 
    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()
        if choice == "1":  
            message = input("Enter your message: ").strip()
            if message:
                #the channel from which the user sends the text is displayed to be easier to understand
                send_message(client_socket, f"{current_channel}: {message}")  
            else:
                print("Message cannot be empty.")
        elif choice == "2": 
            recipient = input("Enter recipient's nickname: ").strip()
            if recipient:
                message = input(f"Enter message to send to {recipient}: ").strip()
                if message:
                    send_message(client_socket, f"/msg {recipient} {message}")
                else:
                    print("Message cannot be empty.")
            else:
                print("Recipient's nickname cannot be empty.")
        elif choice == "3":  
            new_channel = input("Enter the channel name: ").strip()
            if new_channel:
                send_message(client_socket, f"/join {new_channel}")
                current_channel = new_channel  
            else:
                print("Channel name cannot be empty.")
        elif choice == "4":  
            send_message(client_socket, "/users")
        elif choice == "5":  
            send_message(client_socket, "/exit")
            print("Disconnecting")
            client_socket.close()
            break
        else:
            print("Invalid choice.")
if __name__ == "__main__":
    start_client()