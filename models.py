from dataclasses import dataclass


@dataclass
class WiFiNetwork:
    ssid: str
    signal: int
    security: str
    active: bool = False

    @property
    def security_display(self) -> str:
        return self.security if self.security else "Open"