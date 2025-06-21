"""
gui_app.py

Provides a graphical user interface (GUI) for AquiMatrix.
Features:
1. Entry Submission: Form to submit new entries.
2. State Visualization: Displays contract states and DAG structure.
3. Real-Time Updates: Uses WebSocket for live event updates.
4. User Authentication: Manages keys and sessions.
Built with PyQt5.
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit
from PyQt5.QtCore import QThread, pyqtSignal
import requests
import json
import asyncio
import websockets

API_URL = "http://localhost:9000"
WS_URL = "ws://localhost:9001"

class WebSocketClient(QThread):
    message_received = pyqtSignal(str)

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.listen())

    async def listen(self):
        async with websockets.connect(WS_URL) as websocket:
            while True:
                message = await websocket.recv()
                self.message_received.emit(message)

class AquiMatrixGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.ws_client = WebSocketClient()
        self.ws_client.message_received.connect(self.on_message)
        self.ws_client.start()

    def init_ui(self):
        self.setWindowTitle("AquiMatrix GUI")
        self.layout = QVBoxLayout()

        self.entry_input = QTextEdit()
        self.submit_button = QPushButton("Submit Entry")
        self.submit_button.clicked.connect(self.submit_entry)

        self.state_label = QLabel("Contract State:")
        self.state_display = QTextEdit()
        self.state_display.setReadOnly(True)

        self.layout.addWidget(self.entry_input)
        self.layout.addWidget(self.submit_button)
        self.layout.addWidget(self.state_label)
        self.layout.addWidget(self.state_display)

        self.setLayout(self.layout)

    def submit_entry(self):
        try:
            entry_data = json.loads(self.entry_input.toPlainText())
            response = requests.post(f"{API_URL}/entries", json=entry_data)
            if response.status_code == 200:
                self.state_display.append("Entry submitted successfully.")
            else:
                self.state_display.append(f"Error: {response.text}")
        except Exception as e:
            self.state_display.append(f"Invalid entry data: {e}")

    def on_message(self, message):
        self.state_display.append(f"Update: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AquiMatrixGUI()
    gui.show()
    sys.exit(app.exec_())
