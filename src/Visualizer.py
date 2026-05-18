import tkinter as tk
from typing import Callable, Optional

from src.models import Graph, Zone, ZoneType, Drone


class GraphView:
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    PADDING = 100
    SCALE = 120

    ZONE_RADIUS = 45
    DRONE_RADIUS = 10

    def __init__(self, graph: Graph, drones: list[Drone]) -> None:
        self.graph = graph
        self.drones = drones
        self.on_next_turn: Optional[Callable[[], None]] = None

        self.min_x = 0
        self.min_y = 0
        self.__calculate_min_coords()

        self.root = tk.Tk()
        self.root.title("Fly-in")

        self.__create_layout()

    def run(self) -> None:
        self.draw()
        self.root.mainloop()

    def draw(self) -> None:
        self.canvas.delete("all")

        self.__draw_connections()
        self.__draw_zones()
        self.__draw_drones_on_zones()
        self.__draw_drones_on_connections()

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def set_on_next_turn(self, callback: Callable[[], None]) -> None:
        self.on_next_turn = callback

    def __create_layout(self) -> None:
        button = tk.Button(self.root, text="Next Turn",
                           command=self.__handle_next_turn)
        button.pack(side="top")

        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(frame, width=self.WINDOW_WIDTH,
                                height=self.WINDOW_HEIGHT,
                                bg="#1e1e1e")

        v_scroll = tk.Scrollbar(frame, orient="vertical",
                                command=self.canvas.yview)
        h_scroll = tk.Scrollbar(frame, orient="horizontal",
                                command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scroll.set,
                              xscrollcommand=h_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    def __handle_next_turn(self) -> None:
        if self.on_next_turn is None:
            return

        self.on_next_turn()
        self.draw()

    def __calculate_min_coords(self) -> None:
        if not self.graph.zones:
            return

        self.min_x = min(zone.x for zone in self.graph.zones.values())
        self.min_y = min(zone.y for zone in self.graph.zones.values())

    def __draw_connections(self) -> None:
        for connection in self.graph.connections:
            x1, y1 = self.__zone_coords(connection.zone_a)
            x2, y2 = self.__zone_coords(connection.zone_b)

            self.canvas.create_line(x1, y1, x2, y2, fill="#555555", width=2)

            if connection.max_capacity > 1:
                mid_x, mid_y = self.__middle_point(x1, y1, x2, y2)
                self.canvas.create_text(mid_x, mid_y - 12,
                                        text=f"×{connection.max_capacity}",
                                        fill="#FFAA00",
                                        font=("Arial", 8, "bold"))

    def __draw_zones(self) -> None:
        for zone in self.graph.zones.values():
            x, y = self.__zone_coords(zone)

            self.canvas.create_oval(
                x - self.ZONE_RADIUS,
                y - self.ZONE_RADIUS,
                x + self.ZONE_RADIUS,
                y + self.ZONE_RADIUS,
                fill=self.__get_zone_color(zone),
                outline="black",
                width=2)

            self.canvas.create_text(
                x, y - 7,
                text=zone.name,
                fill="black" if not self.__get_zone_color(zone) == "black"
                else "white",
                font=("Arial", 7, "bold"))

            if zone.max_drones > 1:
                self.canvas.create_text(
                    x, y + 10,
                    text=f"max={zone.max_drones}",
                    fill="#333333",
                    font=("Arial", 7))

    def __draw_drones_on_zones(self) -> None:
        for zone in self.graph.zones.values():
            x, y = self.__zone_coords(zone)
            drones = list(zone.current_drones)
            MAX_VISIBLE_DRONES = 3
            visible = drones[:MAX_VISIBLE_DRONES]
            hidden = len(drones) - len(visible)
            total = len(visible)

            for index, drone_id in enumerate(visible):
                offset_x = (index - (total - 1) / 2) * 22
                drone_x = x + offset_x
                drone_y = y - self.ZONE_RADIUS + 15
                self.__draw_drone(drone_x, drone_y, drone_id)

            if hidden > 0:
                hidden_x = (x + ((total - 1) / 2) * 22 + 35)
                hidden_y = y - self.ZONE_RADIUS + 15
                self.canvas.create_text(
                    hidden_x,
                    hidden_y,
                    text=f"+{hidden}",
                    fill="white",
                    font=("Arial", 8, "bold"))

    def __draw_drones_on_connections(self) -> None:
        for drone in self.drones:
            if drone.current_connection is None:
                continue

            connection = drone.current_connection

            x1, y1 = self.__zone_coords(connection.zone_a)
            x2, y2 = self.__zone_coords(connection.zone_b)

            drone_x, drone_y = self.__middle_point(x1, y1, x2, y2)
            self.__draw_drone(drone_x, drone_y, drone.drone_id)

    def __draw_drone(self, x: float, y: float, drone_id: int) -> None:
        self.canvas.create_oval(
            x - self.DRONE_RADIUS,
            y - self.DRONE_RADIUS,
            x + self.DRONE_RADIUS,
            y + self.DRONE_RADIUS,
            fill="cyan",
            outline="black"
        )

        self.canvas.create_text(
            x, y,
            text=f"D{drone_id}",
            fill="black",
            font=("Arial", 8, "bold")
        )

    def __zone_coords(self, zone: Zone) -> tuple[float, float]:
        x = (zone.x - self.min_x) * self.SCALE + self.PADDING
        y = (zone.y - self.min_y) * self.SCALE + self.PADDING
        return x, y

    def __middle_point(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float
    ) -> tuple[float, float]:
        return (x1 + x2) / 2, (y1 + y2) / 2

    def __get_zone_color(self, zone: Zone) -> str:
        if zone.color is not None:

            custom = {
                "rainbow": "#FF9800",
                "gold": "#FF9800",
            }
            return custom.get(zone.color, zone.color)

        colors = {
            ZoneType.RESTRICTED: "#FF9800",
            ZoneType.BLOCKED: "#616161",
            ZoneType.PRIORITY: "#03A9F4",
            ZoneType.NORMAL: "#E0E0E0"}

        if zone.is_start:
            return "#4CAF50"

        if zone.is_end:
            return "#F44336"

        return colors[zone.zone_type]
