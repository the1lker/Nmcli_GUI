import curses
import time
from typing import List, Optional

from models import WiFiNetwork
from nmcli import NMCLIError, NetworkManager


class NetworkTUI:
    def __init__(self, stdscr) -> None:
        self.stdscr = stdscr
        self.nm = NetworkManager()

        self.networks: List[WiFiNetwork] = []
        self.selected = 0

        self.message = ""
        self.running = True

        self.show_password = False
        self.password = ""

    def setup(self) -> None:
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.timeout(500)

        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        curses.init_pair(4, curses.COLOR_YELLOW, -1)

        self.refresh_networks()

    def set_message(self, message: str) -> None:
        self.message = message

    def refresh_networks(self) -> None:
        try:
            self.networks = self.nm.scan_wifi()

            if not self.networks:
                self.selected = 0
            elif self.selected >= len(self.networks):
                self.selected = len(self.networks) - 1

            self.set_message("Wi-Fi ağları yenilendi.")

        except NMCLIError as error:
            self.set_message(str(error))

    def run(self) -> None:
        self.setup()

        while self.running:
            self.draw()

            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if key == -1:
                continue

            self.handle_key(key)

    def handle_key(self, key: int) -> None:
        if self.show_password:
            self.handle_password_key(key)
            return

        if key in (ord("q"), ord("Q"), 27):
            self.running = False

        elif key in (curses.KEY_UP, ord("k")):
            self.move_up()

        elif key in (curses.KEY_DOWN, ord("j")):
            self.move_down()

        elif key in (curses.KEY_ENTER, 10, 13):
            self.connect_selected()

        elif key in (ord("r"), ord("R")):
            self.refresh_networks()

        elif key in (ord("d"), ord("D")):
            self.disconnect()

        elif key in (ord("f"), ord("F")):
            self.forget_selected()

        elif key in (ord("w"), ord("W")):
            self.toggle_wifi()

    def handle_password_key(self, key: int) -> None:
        if key == 27:
            self.show_password = False
            self.password = ""
            self.set_message("Bağlantı iptal edildi.")
            return

        if key in (curses.KEY_ENTER, 10, 13):
            self.show_password = False
            self.connect_with_password()
            return

        if key in (curses.KEY_BACKSPACE, 127, 8):
            self.password = self.password[:-1]
            return

        if 32 <= key <= 126:
            self.password += chr(key)

    def move_up(self) -> None:
        if not self.networks:
            return

        self.selected = max(0, self.selected - 1)

    def move_down(self) -> None:
        if not self.networks:
            return

        self.selected = min(
            len(self.networks) - 1,
            self.selected + 1,
        )

    def connect_selected(self) -> None:
        if not self.networks:
            self.set_message("Bağlanılacak ağ yok.")
            return

        network = self.networks[self.selected]

        if network.active:
            self.set_message(f"{network.ssid} zaten bağlı.")
            return

        if network.security:
            self.show_password = True
            self.password = ""
            self.set_message(
                f"{network.ssid} için şifre girin. Enter = bağlan, Esc = iptal"
            )
            return

        self.connect_network(network)

    def connect_with_password(self) -> None:
        if not self.networks:
            return

        network = self.networks[self.selected]

        try:
            self.nm.connect(network, self.password)
            self.password = ""

            self.set_message(
                f"{network.ssid} ağına bağlanıldı."
            )

            time.sleep(0.5)
            self.refresh_networks()

        except NMCLIError as error:
            self.password = ""
            self.set_message(str(error))

    def connect_network(self, network: WiFiNetwork) -> None:
        try:
            self.nm.connect(network)
            self.set_message(
                f"{network.ssid} ağına bağlanıldı."
            )

            time.sleep(0.5)
            self.refresh_networks()

        except NMCLIError as error:
            self.set_message(str(error))

    def disconnect(self) -> None:
        try:
            self.nm.disconnect()
            self.set_message("Wi-Fi bağlantısı kesildi.")

            time.sleep(0.3)
            self.refresh_networks()

        except NMCLIError as error:
            self.set_message(str(error))

    def forget_selected(self) -> None:
        if not self.networks:
            self.set_message("Seçili ağ yok.")
            return

        network = self.networks[self.selected]

        if not self.confirm(
            f"'{network.ssid}' kaydı silinsin mi?"
        ):
            self.set_message("İşlem iptal edildi.")
            return

        try:
            self.nm.forget(network.ssid)
            self.set_message(
                f"{network.ssid} kayıtlı bağlantılardan silindi."
            )

            time.sleep(0.3)
            self.refresh_networks()

        except NMCLIError as error:
            self.set_message(str(error))

    def toggle_wifi(self) -> None:
        try:
            enabled = self.nm.wifi_radio_enabled()

            self.nm.set_wifi(not enabled)

            state = "açıldı" if not enabled else "kapatıldı"

            self.set_message(f"Wi-Fi {state}.")

            time.sleep(0.3)

            if not enabled:
                self.refresh_networks()
            else:
                self.networks = []

        except NMCLIError as error:
            self.set_message(str(error))

    def confirm(self, question: str) -> bool:
        height, width = self.stdscr.getmaxyx()

        y = height // 2
        x = max(0, (width - len(question) - 20) // 2)

        self.stdscr.attron(curses.A_REVERSE)

        try:
            self.stdscr.addstr(
                y,
                x,
                f" {question} [y/N] ",
            )
        except curses.error:
            pass

        self.stdscr.attroff(curses.A_REVERSE)

        self.stdscr.refresh()

        while True:
            key = self.stdscr.getch()

            if key in (ord("y"), ord("Y")):
                return True

            if key in (
                ord("n"),
                ord("N"),
                10,
                13,
                27,
            ):
                return False

    def draw(self) -> None:
        self.stdscr.erase()

        height, width = self.stdscr.getmaxyx()

        if height < 15 or width < 60:
            self.draw_too_small(height, width)
            self.stdscr.refresh()
            return

        self.draw_header(width)
        self.draw_networks(height, width)
        self.draw_footer(height, width)

        if self.show_password:
            self.draw_password_box(height, width)

        self.stdscr.refresh()

    def draw_too_small(self, height: int, width: int) -> None:
        text = "Terminal çok küçük. En az 60x15 kullanın."

        y = height // 2
        x = max(0, (width - len(text)) // 2)

        try:
            self.stdscr.addstr(y, x, text)
        except curses.error:
            pass

    def draw_header(self, width: int) -> None:
        title = " Network Manager TUI "

        try:
            self.stdscr.addstr(
                1,
                2,
                title,
                curses.color_pair(1) | curses.A_BOLD,
            )

            self.stdscr.addstr(
                2,
                2,
                "Wi-Fi networks",
                curses.A_BOLD,
            )

            self.stdscr.hline(
                3,
                2,
                curses.ACS_HLINE,
                width - 4,
            )

        except curses.error:
            pass

    def draw_networks(self, height: int, width: int) -> None:
        start_y = 5
        available_height = height - 10

        if not self.networks:
            try:
                self.stdscr.addstr(
                    start_y,
                    4,
                    "Wi-Fi ağı bulunamadı.",
                    curses.color_pair(4),
                )
            except curses.error:
                pass

            return

        visible_start = 0

        if self.selected >= available_height:
            visible_start = self.selected - available_height + 1

        visible_networks = self.networks[
            visible_start:visible_start + available_height
        ]

        for index, network in enumerate(visible_networks):
            actual_index = visible_start + index
            y = start_y + index

            selected = actual_index == self.selected

            prefix = ">" if selected else " "
            active = "●" if network.active else " "

            ssid = network.ssid

            max_ssid_length = max(
                10,
                width - 38,
            )

            if len(ssid) > max_ssid_length:
                ssid = ssid[:max_ssid_length - 1] + "…"

            signal = f"{network.signal:>3}%"
            security = network.security_display

            line = (
                f"{prefix} {active} "
                f"{ssid:<{max_ssid_length}} "
                f"{signal}  "
                f"{security}"
            )

            attributes = 0

            if selected:
                attributes |= curses.A_REVERSE

            if network.active:
                attributes |= curses.color_pair(2)

            try:
                self.stdscr.addstr(
                    y,
                    2,
                    line[:width - 4],
                    attributes,
                )
            except curses.error:
                pass

    def draw_footer(self, height: int, width: int) -> None:
        footer_y = height - 4

        try:
            self.stdscr.hline(
                footer_y,
                2,
                curses.ACS_HLINE,
                width - 4,
            )

            help_text = (
                "↑↓ Select   Enter Connect   R Rescan   "
                "D Disconnect   F Forget   W Wi-Fi   Q Quit"
            )

            self.stdscr.addstr(
                footer_y + 1,
                2,
                help_text[:width - 4],
                curses.A_DIM,
            )

            message = self.message

            if len(message) > width - 4:
                message = message[:width - 7] + "..."

            self.stdscr.addstr(
                footer_y + 2,
                2,
                message,
                curses.color_pair(
                    3 if "error" in message.lower()
                    else 4
                ),
            )

        except curses.error:
            pass

    def draw_password_box(self, height: int, width: int) -> None:
        box_width = min(60, width - 8)
        box_height = 7

        start_y = (height - box_height) // 2
        start_x = (width - box_width) // 2

        try:
            self.stdscr.attron(curses.A_REVERSE)

            for y in range(box_height):
                self.stdscr.addstr(
                    start_y + y,
                    start_x,
                    " " * box_width,
                )

            self.stdscr.attroff(curses.A_REVERSE)

            self.stdscr.addstr(
                start_y + 1,
                start_x + 2,
                "Wi-Fi Password",
                curses.A_BOLD,
            )

            self.stdscr.addstr(
                start_y + 3,
                start_x + 2,
                "*" * len(self.password),
            )

            self.stdscr.addstr(
                start_y + 5,
                start_x + 2,
                "Enter: Connect    Esc: Cancel",
                curses.A_DIM,
            )

        except curses.error:
            pass


def start_ui() -> None:
    curses.wrapper(
        lambda stdscr: NetworkTUI(stdscr).run()
    )