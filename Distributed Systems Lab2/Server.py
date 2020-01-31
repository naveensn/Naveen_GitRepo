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
http://effbot.org/tkinterbook/entry.htm#Tkinter.Entry.delete-method
"""

# Change the shared path of server according to your folder name.
FILE = "D:\\Study\\1st Sem\\Distributed Systems\\Lab2\\Server\\Text.txt"


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
        users.delete(0, tk.END)
        users.insert(tk.END, "Active clients\n")
        for client in clients:
            users.insert(tk.END, " " + str(clients[client]) + "\n")
        try:
            c.send("Y".encode())
        except socket.error:
            msg.insert(tk.END, "connection error : make sure server is running, IP and port# are correct\n")
            exit(0)

        try:
            file_info = c.recv(BUFSIZ)
            data = file_info.decode('utf8')
        except:
            file_info = "EXIT_CONNECTION".encode('utf8')
            data = "EXIT_CONNECTION"

        while file_info:
            if data == "EXIT_CONNECTION":
                break
            if data == "Y":
                msg.insert(tk.END, "File " + FILE + " has been updated by " + user_name + "\n")
                f = open(FILE, 'wb')
                while True:
                    # get file bytes
                    data = c.recv(BUFSIZ)
                    # write bytes on file
                    f.write(data)
                    if len(data) <= BUFSIZ:
                        break
                f.close()
                msg.insert(tk.END, "Updated file has been downloaded and is being sent to others\n")
                for client in clients:
                    if clients[client] != user_name:
                        client.send(file_info)
                        f = open(FILE, "rb")
                        data = f.read(BUFSIZ)
                        # print("in for " + data)
                        while data:
                            client.send(data)
                            data = f.read(BUFSIZ)
                        msg.insert(tk.END, "The updated file sent to " + str(clients[client]) + "\n")
                msg.insert(tk.END, "Update completed, if new update is available, notification will be shown here\n")
            try:
                file_info = c.recv(BUFSIZ)
            except:
                break
            data = file_info.decode('utf8')

        msg.insert(tk.END, user_name + " Disconnected\n")
        user_names.remove(user_name)
        del clients[c]
        if bool(clients):
            users.delete(0, tk.END)
            users.insert(tk.END, "Active clients\n")
            for client in clients:
                users.insert(tk.END, " " + str(clients[client]) + "\n")
        else:
            users.delete(0, tk.END)
            users.insert(tk.END, "No active clients\n")
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

# below is the code for GUI.
window = tk.Tk()
window.title("Server")

frame = tk.Frame(window)
scrollbar = tk.Scrollbar(frame)  # To navigate through past messages.
# Following will contain the messages.
msg = tk.Listbox(frame, height=50, width=100, yscrollcommand=scrollbar.set)

msg.pack(side=tk.LEFT, fill=tk.BOTH)
msg.pack()
users = tk.Listbox(frame, height=40, width=30)
users.pack(side=tk.RIGHT)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
frame.pack()

users.insert(tk.END, "No active clients\n")
msg.insert(tk.END, "Server started...\n")

connect_thread = threading.Thread(target=connect)
connect_thread.start()

tk.mainloop()   # Starts GUI execution.
