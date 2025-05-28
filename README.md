# 🚀 How to Run SAP MCP

## 🖥️ Run the Server

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Start the server:
   ```sh
   python sap-mcp-server.py
   ```
3. For any changes you do to the server file, you may need to stop and restart the server as follows:

   netstat -ano | findstr :8080 (the port number)
   
This should give you the process to kill. You can then run:

   taskkill /F /PID 12017(or whatever the process ID is)

## 💻 Run the Client

1. Change to the `test` directory:
   ```sh
   cd test
   ```
2. Start the client:
   ```sh
   python sap-mcp-client.py
   ```
