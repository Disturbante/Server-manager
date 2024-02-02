import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import json

class ServerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Manager")

        # Left column with list of servers
        self.server_listbox = tk.Listbox(root, selectmode=tk.SINGLE)
        self.server_listbox.grid(row=0, column=0, rowspan=3, sticky=tk.N+tk.S+tk.E+tk.W)

        # Populate server list from file
        self.servers = self.load_servers()
        for server in self.servers:
            self.server_listbox.insert(tk.END, server)

        # Add and Remove buttons
        add_button = tk.Button(root, text="Add Server", command=self.add_server)
        add_button.grid(row=3, column=0, sticky=tk.W)
        remove_button = tk.Button(root, text="Remove Server", command=self.remove_server)
        remove_button.grid(row=3, column=0, sticky=tk.E)

        # Right big window for the terminal
        self.terminal_frame = tk.Frame(root)
        self.terminal_frame.grid(row=0, column=1, rowspan=3, sticky=tk.N+tk.S+tk.E+tk.W)

        # Binding server selection to show terminal
        self.server_listbox.bind("<<ListboxSelect>>", self.show_terminal)

        # Save servers to file on exit
        root.protocol("WM_DELETE_WINDOW", self.save_servers_on_exit)

    def add_server(self):
        new_name = simpledialog.askstring("Add Server", "Enter server name:")
        if new_name:
            new_ip = simpledialog.askstring("Add Server", "Enter server IP address:")
            if new_ip:
                new_server = f"{new_name} - {new_ip}"
                self.servers.append(new_server)
                self.server_listbox.insert(tk.END, new_server)
                self.save_servers()

    def remove_server(self):
        selected_index = self.server_listbox.curselection()
        if selected_index:
            server_to_remove = self.servers.pop(selected_index[0])
            self.server_listbox.delete(selected_index)
            messagebox.showinfo("Server Removed", f"Server '{server_to_remove}' removed.")
            self.save_servers()

    def show_terminal(self, event):
        selected_index = self.server_listbox.curselection()
        if selected_index:
            selected_server = self.servers[selected_index[0]]
            self.display_terminal(selected_server)

    def display_terminal(self, server):
        # Clear previous terminal content
        for widget in self.terminal_frame.winfo_children():
            widget.destroy()

        # Spawn terminal for the selected server
        name, ip = server.split(' - ')
        terminal_command = f"gnome-terminal --command 'ssh {ip}'"
        subprocess.Popen(terminal_command, shell=True)

    def load_servers(self):
        try:
            with open("servers.json", "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_servers(self):
        with open("servers.json", "w") as file:
            json.dump(self.servers, file)

    def save_servers_on_exit(self):
        self.save_servers()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    server_manager = ServerManager(root)
    root.mainloop()

