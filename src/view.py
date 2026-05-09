from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.models import Zone


class TerminalVisualizer:
    """Display the simulation state in the terminal."""

    VALID_COLORS = {
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "orange,"
    }

    def __init__(self) -> None:
        self.console = Console()

    def display_turn_status(
        self,
        turn_number: int,
        zones: list[Zone],
        moves: list[str],
    ) -> None:
        """Display zones status and movements for a simulation turn."""
        self.__print_turn_title(turn_number)
        self.__print_zones_table(zones)
        self.__print_moves(moves)

    def __print_turn_title(self, turn_number: int) -> None:
        self.console.print(
            Panel(
                f"[bold yellow]TURN {turn_number}[/bold yellow]",
                expand=False,
            )
        )

    def __print_zones_table(self, zones: list[Zone]) -> None:
        table = Table(
            title="Zone Status",
            show_header=True,
            header_style="bold magenta",
        )

        table.add_column("Zone", style="dim")
        table.add_column("Type", justify="center")
        table.add_column("Occupancy", justify="center")
        table.add_column("Drones")

        for zone in zones:
            table.add_row(
                self.__format_zone_name(zone),
                self.__format_zone_type(zone),
                self.__format_occupancy(zone),
                self.__format_drones(zone),
            )

        self.console.print(table)

    def __print_moves(self, moves: list[str]) -> None:
        if not moves:
            return

        moves_text = Text.assemble(
            ("MOVEMENTS: ", "bold cyan"),
            (" ".join(moves), "white"),
        )

        self.console.print(moves_text)
        self.console.print("-" * 40)

    def __format_zone_name(self, zone: Zone) -> str:
        if zone.is_start:
            return f"{zone.name} [START]"

        if zone.is_end:
            return f"{zone.name} [END]"

        return zone.name

    def __format_zone_type(self, zone: Zone) -> str:
        color = self.__safe_color(zone.color)

        return f"[{color}]{zone.zone_type.value}[/]"

    def __format_occupancy(self, zone: Zone) -> str:
        current = len(zone.current_drones)

        if zone.is_start or zone.is_end:
            return f"[blue]{current} drone(s)[/blue]"

        empty_slots = zone.max_drones - current

        return "●" * current + "○" * empty_slots

    def __format_drones(self, zone: Zone) -> str:
        if not zone.current_drones:
            return "-"

        return ", ".join(
            f"D{drone_id}" for drone_id in sorted(zone.current_drones)
        )

    def __safe_color(self, color: str | None) -> str:
        if color is None:
            return "white"

        normalized = color.lower()

        if normalized not in self.VALID_COLORS:
            return "white"

        return normalized

    def display_initial_state(self, zones: list[Zone]) -> None:
        """Display the initial map state before the simulation starts."""
        self.console.print(
            Panel(
                "[bold green]INITIAL MAP STATE[/bold green]",
                expand=False,
            )
        )

        self.__print_zones_table(zones)
        self.console.print("-" * 40)
