#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QInputDialog, QFrame, QTextEdit, QLabel, QLineEdit
)
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtCore import QTimer
import json
import paramiko
from ping3 import ping

class ServerManager(QMainWindow):
    def __init__(self):
        super(ServerManager, self).__init__()

        self.setWindowTitle("Server Manager")

        # Left column with a list of servers (4/10)
        self.server_list_widget = QListWidget()
        self.server_list_widget.setStyleSheet("background-color: darkgrey;")
        self.server_list_widget.itemClicked.connect(self.show_terminal)

        # Add and Remove buttons
        add_button = QPushButton("Add Server", self)
        add_button.clicked.connect(self.add_server)

        remove_button = QPushButton("Remove Server", self)
        remove_button.clicked.connect(self.remove_server)

        # Left layout for the server list
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.server_list_widget)
        left_layout.addWidget(add_button)
        left_layout.addWidget(remove_button)

        # Right layout for the emulated terminal (6/10)
        self.terminal_frame = QFrame(self)
        self.terminal_frame.setStyleSheet("background-color: lightblue;")

        # Terminal content (emulated)
        self.terminal_content = QTextEdit(self.terminal_frame)
        self.terminal_content.setReadOnly(True)

        # Label for the emulated terminal
        terminal_label = QLabel("Emulated Terminal", self.terminal_frame)

        # Input bar for entering commands
        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText("Enter command and press Enter...")
        self.command_input.returnPressed.connect(self.execute_command)

        # Bottom layout for the input bar
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.command_input)

        # Right layout
        right_layout = QVBoxLayout(self.terminal_frame)
        right_layout.addWidget(terminal_label)
        right_layout.addWidget(self.terminal_content)
        right_layout.addLayout(bottom_layout)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 4)
        main_layout.addWidget(self.terminal_frame, 6)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

        # Populate the server list from the file
        self.servers = self.load_servers()
        for server in self.servers:
            self.server_list_widget.addItem(server)

        # Update server statuses initially
        self.update_server_statuses()

        # SSH client instance
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # SSH channel
        self.channel = None

        # QTimer for updating the terminal content
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_terminal)

        # QTimer for updating the server statuses
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_server_statuses)
        self.status_timer.start(30000)  # Set the interval in milliseconds (30 seconds)

    def check_server_status(self, item):
        params = item.text().split(' - ')
        name = params[0]
        ip = params[1]

        try:
            result = ping(ip, timeout=1)  # Set the timeout in seconds

            if result is not None:
                status_text = "Up"
                status_color = QColor(0, 255, 0)  # Green color
            else:
                status_text = "Down"
                status_color = QColor(255, 0, 0)  # Red color

            item.setForeground(status_color)
            item.setText(f"{name} - {ip} - {status_text}")

        except Exception as e:
            item.setForeground(QColor(255, 0, 0))  # Red color for error
            item.setText(f"{name} - {ip} - Error checking status: {str(e)}")


    def update_server_statuses(self):
        # Iterate through servers and update their status in the list
        for i in range(self.server_list_widget.count()):
            item = self.server_list_widget.item(i)
            self.check_server_status(item)

    def show_terminal(self, item):
        selected_server = item.text()
        self.display_terminal(selected_server)

    def add_server(self):
        new_name, ok_name = QInputDialog.getText(self, "Add Server", "Enter server name:")
        if ok_name:
            new_ip, ok_ip = QInputDialog.getText(self, "Add Server", "Enter server IP address:")
            if ok_ip:
                new_server = f"{new_name} - {new_ip}"
                self.servers.append(new_server)
                self.server_list_widget.addItem(new_server)
                self.save_servers()
                self.update_server_statuses()

    def remove_server(self):
        selected_item = self.server_list_widget.currentItem()
        if selected_item:
            server_to_remove = selected_item.text()
            self.servers.remove(server_to_remove)
            self.server_list_widget.takeItem(self.server_list_widget.row(selected_item))
            self.terminal_content.clear()  # Clear the terminal when removing a server
            self.save_servers()
            self.update_server_statuses()

    def display_terminal(self, server):
        self.terminal_content.clear()  # Clear previous terminal content

        # Emulate terminal content for the selected server
        server_params = server.split(' - ')
        name = server_params[0]
        ip = server_params[1]
        self.terminal_content.append(f"Connecting to server {name} at {ip}...\n")

        # Prompt the user for SSH username and password
        username, ok_username = QInputDialog.getText(self, "SSH Authentication", "Enter SSH username:")
        if not ok_username:
            self.terminal_content.append("SSH connection aborted. Username not provided.\n")
            return

        password, ok_password = QInputDialog.getText(self, "SSH Authentication", "Enter SSH password:", QLineEdit.Password)
        if not ok_password:
            self.terminal_content.append("SSH connection aborted. Password not provided.\n")
            return

        # Attempt SSH connection
        try:
            transport = paramiko.Transport((ip, 22))
            transport.connect(username=username, password=password)

            self.channel = transport.open_session()
            self.channel.get_pty(term='dumb')  # Set terminal type
            self.channel.invoke_shell()

            self.terminal_content.append("SSH connection successful!\n")

            # Start the QTimer for updating the terminal
            self.timer.start(100)  # Set the interval in milliseconds (adjust as needed)

        except paramiko.AuthenticationException:
            self.terminal_content.append("SSH authentication failed. Check username and password.\n")
        except paramiko.SSHException as e:
            self.terminal_content.append(f"SSH connection failed: {str(e)}\n")
        except Exception as ecc:
            self.terminal_content.append("SSH connection failed\n")

    def update_terminal(self):
        # Check for new data in the SSH channel and update the terminal content
        if self.channel.recv_ready():
            output = self.channel.recv(1024).decode('utf-8')
            self.terminal_content.insertPlainText(output)
            self.terminal_content.moveCursor(QTextCursor.End)

    def execute_command(self):
        command = self.command_input.text()
        self.command_input.clear()

        if command:
            self.channel.send(command + "\n")

    def load_servers(self):
        try:
            with open("servers.json", "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_servers(self):
        with open("servers.json", "w") as file:
            json.dump(self.servers, file)

    def closeEvent(self, event):
        if self.timer.isActive():
            self.timer.stop()
        if self.status_timer.isActive():
            self.status_timer.stop()
        if self.channel:
            self.channel.close()
        self.ssh_client.close()
        self.save_servers()
        event.accept()

def main():
    app = QApplication(sys.argv)
    main_window = ServerManager()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
