````markdown
# WifiSlayer

![WifiSlayer UI](ui.png)

**WifiSlayer** is a modern wireless network security testing tool built with Python and PyQt6. It provides a graphical user interface (GUI) to manage powerful Linux network utilities such as `airmon-ng`, `airodump-ng`, and `mdk4`, allowing users to perform security audits and stress tests with ease.

---

## Features

![WifiSlayer Interface](ui.jpeg)

- **Interface Management:** Automatically detects wireless network interfaces available on the system.  
- **Monitor Mode:** Enables or disables monitor mode on the selected interface with a single click.  
- **Network Scanning:** Performs real-time scanning of nearby access points, listing BSSID, Channel, and ESSID information.  
- **Deauthentication Attacks:** Executes targeted deauthentication (stress test) attacks using `mdk4` against one or multiple selected targets.  
- **Dark UI:** Features a professional dark-themed interface for better visibility and reduced eye strain.  
- **Automatic Cleanup:** Automatically cleans up temporary files and restarts network services upon application exit.  

---

## Requirements

### 1. System Tools

The following packages must be installed on your Linux system for the application to function correctly:

- `aircrack-ng` (for `airmon-ng` and `airodump-ng`)  
- `mdk4`  
- `network-manager` (for `nmcli` management)  
- `python3`  

#### Installation command for Debian/Kali/Ubuntu:

```bash
sudo apt update && sudo apt install aircrack-ng mdk4 network-manager python3-pip
````

---

### 2. Python Libraries

Install the required Python dependencies using pip:

```bash
pip install PyQt6
```

---

## Installation and Execution

1. **Download Files:** Ensure all project files (`main.py`, `gui.py`, `backend.py`, `ui.png`) are located in the same directory.
2. **Open Terminal:** Navigate to the directory containing the project files.
3. **Start Application:** Since the tool interacts directly with network hardware, it requires root privileges. It is recommended to use the `-E` flag to preserve the Python environment variables:

```bash
sudo -E python3 main.py
```

---

## Usage Instructions

1. **Select Interface:** Choose your wireless network card from the dropdown menu in the top right corner.
2. **Enable Monitor Mode:** Click the **"Enable Monitor"** button to put the card into monitor mode.
3. **Scan Networks:** Click the **"Scan"** button. Nearby networks will begin to populate the table after a few seconds.
4. **Select Targets:** Click on one or more rows in the table to select your targets.
5. **Launch Attack:** Click the **"Attack"** button to start the `mdk4` deauthentication process. Click **"Stop Attack"** to terminate the process.
6. **Safe Exit:** It is recommended to disable monitor mode and click **"Stop Attack"** before closing the application to ensure network services are restored properly.

---

## Project Structure

* `main.py`: The entry point of the application. It handles root privilege checks and initializes the GUI.
* `gui.py`: Contains the user interface design, table management, and button event logic.
* `backend.py`: The core engine that executes terminal commands and processes data in the background.
* `ui.png`: Application interface screenshot used in documentation.

---

## Legal Disclaimer

This tool is developed strictly for educational purposes and authorized penetration testing. Using this tool against networks you do not own or have explicit permission to test is illegal. The developers assume no liability for any misuse of this software.

---

## License

This project is open-source software. Contributions and improvements are welcome.

```
```
