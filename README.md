# nmcli-GUI

A simple terminal-based Wi-Fi manager for Linux, built with Python and `curses`.

`nmcli-GUI` provides a lightweight interactive interface for managing Wi-Fi networks through NetworkManager without leaving the terminal.

## Features

* 📡 Scan available Wi-Fi networks
* 🔐 Connect to password-protected networks
* 🌐 Connect to open networks
* 🔌 Disconnect from the current Wi-Fi network
* 🗑️ Forget saved Wi-Fi networks
* 🔄 Rescan available networks
* 📶 Enable or disable Wi-Fi
* ⌨️ Keyboard-driven terminal interface
* 🚫 No external Python packages required

## Requirements

* Linux
* Python 3
* NetworkManager
* `nmcli`

Check whether `nmcli` is installed:

```bash
nmcli --version
```

Check Python:

```bash
python3 --version
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/nmcli-GUI.git
cd nmcli-GUI
```

Make the main script executable:

```bash
chmod +x main.py
```

Run the application:

```bash
./main.py
```

Or:

```bash
python3 main.py
```

## Global Command

You can also make `nmcli-GUI` available as a system-wide command:

```bash
sudo ln -s "$(realpath main.py)" /usr/local/bin/nmcli-GUI
```

Then simply run:

```bash
nmcli-GUI
```

If you use Zsh and the command was previously not found, refresh the command cache:

```bash
rehash
```

## Controls

| Key       | Action                      |
| --------- | --------------------------- |
| `↑` / `k` | Move up                     |
| `↓` / `j` | Move down                   |
| `Enter`   | Connect to selected network |
| `R`       | Rescan Wi-Fi networks       |
| `D`       | Disconnect                  |
| `F`       | Forget saved network        |
| `W`       | Enable / disable Wi-Fi      |
| `Esc`     | Cancel password / dialog    |
| `Q`       | Quit                        |

## Project Structure

```text
nmcli-GUI/
├── main.py
├── nmcli.py
├── models.py
├── ui.py
└── README.md
```

### `main.py`

Application entry point.

### `ui.py`

Handles the terminal user interface using Python's built-in `curses` module.

### `nmcli.py`

Handles communication with NetworkManager through `nmcli`.

### `models.py`

Contains the data models used by the application.

## Architecture

```text
┌──────────────┐
│    main.py   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     ui.py    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   nmcli.py   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    nmcli     │
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│   NetworkManager   │
└────────────────────┘
```

## Dependencies

The project intentionally uses only Python's standard library.

Main modules:

* `curses`
* `subprocess`
* `dataclasses`
* `typing`

No `pip install` is required.

## Screenshots

*Add screenshots here.*

```markdown
![nmcli-GUI](screenshots/main.png)
```

## Project Status

🚧 **Work in Progress**

The project is currently focused on providing a simple and reliable terminal interface for basic Wi-Fi management.

More features and improvements may be added in the future.

## License

This project is licensed under the MIT License.
