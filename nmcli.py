import subprocess
from typing import List, Optional

from models import WiFiNetwork


class NMCLIError(Exception):
    """Raised when nmcli cannot complete an operation."""


class NetworkManager:
    def __init__(self) -> None:
        self.command = "nmcli"

    def _run(self, *args: str) -> str:
        try:
            result = subprocess.run(
                [self.command, *args],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            raise NMCLIError("nmcli bulunamadı.")

        if result.returncode != 0:
            error = result.stderr.strip() or "Bilinmeyen nmcli hatası."
            raise NMCLIError(error)

        return result.stdout

    def wifi_radio_enabled(self) -> bool:
        output = self._run("radio", "wifi")
        return output.strip().lower() == "enabled"

    def set_wifi(self, enabled: bool) -> None:
        self._run("radio", "wifi", "on" if enabled else "off")

    def rescan(self) -> None:
        self._run("device", "wifi", "rescan")

    def scan_wifi(self) -> List[WiFiNetwork]:
        output = self._run(
            "-t",
            "-f",
            "IN-USE,SSID,SIGNAL,SECURITY",
            "device",
            "wifi",
            "list",
        )

        networks: List[WiFiNetwork] = []
        seen = set()

        for line in output.splitlines():
            if not line.strip():
                continue

            parts = line.split(":", 3)

            if len(parts) != 4:
                continue

            active, ssid, signal, security = parts

            ssid = ssid.strip()
            security = security.strip()

            if not ssid:
                continue

            try:
                signal_value = int(signal.strip())
            except ValueError:
                signal_value = 0

            # Aynı SSID birden fazla access point tarafından
            # yayınlanabilir. İlkini gösteriyoruz.
            if ssid in seen:
                continue

            seen.add(ssid)

            networks.append(
                WiFiNetwork(
                    ssid=ssid,
                    signal=signal_value,
                    security=security,
                    active=active.strip() == "*",
                )
            )

        networks.sort(
            key=lambda network: (
                not network.active,
                -network.signal,
                network.ssid.lower(),
            )
        )

        return networks

    def active_connection(self) -> Optional[str]:
        output = self._run(
            "-t",
            "-f",
            "NAME",
            "connection",
            "show",
            "--active",
        )

        for line in output.splitlines():
            name = line.strip()

            if name:
                return name

        return None

    def connect(self, network: WiFiNetwork, password: Optional[str] = None) -> None:
        if network.security:
            if password is None:
                raise NMCLIError("Bu ağ için şifre gerekiyor.")

            self._run(
                "device",
                "wifi",
                "connect",
                network.ssid,
                "password",
                password,
            )
        else:
            self._run(
                "device",
                "wifi",
                "connect",
                network.ssid,
            )

    def disconnect(self) -> None:
        output = self._run(
            "-t",
            "-f",
            "DEVICE,TYPE,STATE",
            "device",
            "status",
        )

        for line in output.splitlines():
            parts = line.split(":")

            if len(parts) < 3:
                continue

            device, device_type, state = parts[:3]

            if device_type == "wifi" and state == "connected":
                self._run("device", "disconnect", device)
                return

        raise NMCLIError("Aktif bir Wi-Fi bağlantısı bulunamadı.")

    def forget(self, ssid: str) -> None:
        connections = self._run(
            "-t",
            "-f",
            "NAME",
            "connection",
            "show",
        )

        for connection in connections.splitlines():
            connection = connection.strip()

            if connection == ssid:
                self._run("connection", "delete", connection)
                return

        raise NMCLIError(f"Kayıtlı bağlantı bulunamadı: {ssid}")