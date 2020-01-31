import socket
import threading
import tkinter as tk


""" References used
https://www.youtube.com/watch?v=VMP1oQOxfM0
https://www.youtube.com/watch?v=JrWHyqonGj8
https://www.youtube.com/watch?v=_FVvlJDQTxk&list=PLhTjy8cBISErYuLZUvVOYsR1giva2payF&index=4
https://www.youtube.com/watch?v=Iu8_IpztiOU
http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
https://docs.python.org/2/library/socket.html
https://stackoverflow.com/questions/667640/how-to-tell-if-a-connection-is-dead-in-python
https://stackoverflow.com/questions/3998742/how-can-i-dynamically-change-the-color-of-a-button-in-tkinter
https://effbot.org/tkinterbook/button.htm#when-to-use
https://codereview.stackexchange.com/questions/214788/socket-chat-room-made-with-tkinter-python
https://www.reddit.com/r/learnpython/comments/6z2x97/socket_python_3_file_transfer_over_tcp/
https://github.com/schedutron/CPAP/blob/master/Chap5/chat_serv.py
https://github.com/schedutron/CPAP/blob/master/Chap5/chat_clnt_GUI.py
http://www.effbot.org/tkinterbook/pack.htm#patterns
"""


# Change the shared path of server according to your folder name.
PATH = "D:/Study/1st Sem/Distrubuted Systems/Lab1/Server"

def handle_client(c):
    """Once the clients get connected this function handles any function related to that client"""
    """This include username verifications, receiving files and writing file to other clients"""

    user_name = str(c.recv(BUFSIZ).decode())
    if user_name in user_names:
        c.send("N".encode())
    else:
        msg.insert(tk.END, user_name + " connected\n")
        user_names.add(user_name)
        clients[c] = user_name
        try:
            c.send("Y".encode())
        except socket.error:
            msg.insert(tk.END, "connection error : make sure server is running, IP and port# are correct\n")
            exit(0)

        file_info = c.recv(BUFSIZ)
        data = file_info.decode('utf8')
        while file_info:
            if data == "EXIT_CONNECTION":
                break
            if (data[:1] == "Y"):
                msg.insert(tk.END, "new file " + data[1:] + " uploaded by " + user_name + "\n")
                f_name = PATH + "/" + str(data[1:])
                file_name = data[1:]
                f = open(f_name, 'wb')
                while True:
                    # get file bytes
                    data = c.recv(BUFSIZ)
                    # write bytes on file
                    f.write(data)
                    if (len(data) <= BUFSIZ):
                        break
                f.close()
                for client in clients:
                    if clients[client] != user_name:
                        client.send(file_info)
                        f = open(f_name, "rb")
                        data = f.read(BUFSIZ)
                        # print("in for " + data)
                        while data:
                            client.send(data)
                            data = f.read(BUFSIZ)
                        msg.insert(tk.END, "sent file " + file_name + " to " + str(clients[client]) + "\n")
            file_info = c.recv(BUFSIZ)
            data = file_info.decode('utf8')

        msg.insert(tk.END, user_name + " Disconnected\n")
        user_names.remove(user_name)
        del clients[c]
        exit(0)



def connect():
    """Handles connection from new clients messages."""
    SERVER.listen(3)

    while True:
        c, addr = SERVER.accept()
        threading.Thread(target=handle_client, args=(c,)).start()


# ----veriables soring
user_names = set()
clients = {}

# ----Now comes the sockets part----
HOST = "127.0.0.1"
PORT = 7777
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)
PATH = "D:/Study/1st Sem/Distrubuted Systems/Lab1/Server"

# below is the code for GUI.
window = tk.Tk()
window.title("Server")

frame = tk.Frame(window)
scrollbar = tk.Scrollbar(frame)  # To navigate through past messages.
# Following will contain the messages.
msg = tk.Listbox(frame, height=50, width=100, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
msg.pack(side=tk.LEFT, fill=tk.BOTH)
msg.pack()
frame.pack()

msg.insert(tk.END, "Server started...\n")

connect_thread = threading.Thread(target=connect)
connect_thread.start()

tk.mainloop()  # Starts GUI execution.