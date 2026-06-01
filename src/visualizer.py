import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional, Any

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
        self.on_next_turn: Optional[Callable[[], Any]] = None

        self.min_x = 0
        self.min_y = 0
        self._calculate_min_coords()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Fly-in Visualizer")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

        self._create_layout()

    def run(self) -> None:
        self.draw()
        self.root.mainloop()

    def draw(self) -> None:
        self.canvas.delete("all")

        self._draw_connections()
        self._draw_zones()
        self._draw_drones_on_zones()
        self._draw_drones_on_connections()

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def set_on_next_turn(self, callback: Callable[[], Any]) -> None:
        self.on_next_turn = callback

    def _create_layout(self) -> None:

        button = ctk.CTkButton(self.root, text="Next Turn",
                               command=self._handle_next_turn,
                               font=("Arial", 13, "bold"))
        button.pack(side="top", pady=10)
        # close_button = tk.Button(self.root, text="Close",
        #                         command=self.root.destroy)

        # close_button.pack(side="top")

        frame = ctk.CTkFrame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(frame, width=self.WINDOW_WIDTH,
                                height=self.WINDOW_HEIGHT,
                                bg="#1a1a1a", bd=0, highlightthickness=0)

        v_scroll = ctk.CTkScrollbar(frame, orientation="vertical",
                                    command=self.canvas.yview)
        h_scroll = ctk.CTkScrollbar(frame, orientation="horizontal",
                                    command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scroll.set,
                              xscrollcommand=h_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    def _handle_next_turn(self) -> None:
        if self.on_next_turn is None:
            return
        self.on_next_turn()
        self.draw()

    def _calculate_min_coords(self) -> None:
        if not self.graph.zones:
            return
        self.min_x = min(zone.x for zone in self.graph.zones.values())
        self.min_y = min(zone.y for zone in self.graph.zones.values())

    def _draw_connections(self) -> None:
        for connection in self.graph.connections:
            x1, y1 = self._zone_coords(connection.zone_a)
            x2, y2 = self._zone_coords(connection.zone_b)

            self.canvas.create_line(x1, y1, x2, y2, fill="#3d3d3d", width=3)

            if connection.max_capacity > 1:
                mid_x, mid_y = self._middle_point(x1, y1, x2, y2)
                self.canvas.create_text(mid_x, mid_y - 14,
                                        text=f"×{connection.max_capacity}",
                                        fill="#FFCC00",
                                        font=("Arial", 9, "bold"))

    def _draw_zones(self) -> None:
        for zone in self.graph.zones.values():
            x, y = self._zone_coords(zone)
            zone_color = self._get_zone_color(zone)

            text_color = "white" if zone_color in ["black"] else "black"

            self.canvas.create_oval(
                x - self.ZONE_RADIUS,
                y - self.ZONE_RADIUS,
                x + self.ZONE_RADIUS,
                y + self.ZONE_RADIUS,
                fill=zone_color,
                outline="#2b2b2b",
                width=2)

            self.canvas.create_text(
                x, y - 7,
                text=zone.name,
                fill=text_color,
                font=("Arial", 8, "bold"))

            if zone.max_drones > 1:
                self.canvas.create_text(
                    x, y + 12,
                    text=f"max={zone.max_drones}",
                    fill="#444444" if text_color == "black" else "#cccccc",
                    font=("Arial", 8))

    def _draw_drones_on_zones(self) -> None:
        for zone in self.graph.zones.values():
            x, y = self._zone_coords(zone)
            drones = list(zone.current_drones)
            MAX_VISIBLE_DRONES = 3
            visible = drones[:MAX_VISIBLE_DRONES]
            hidden = len(drones) - len(visible)
            total = len(visible)

            for index, drone_id in enumerate(visible):
                offset_x = (index - (total - 1) / 2) * 24
                drone_x = x + offset_x
                drone_y = y - self.ZONE_RADIUS + 18
                self._draw_drone(drone_x, drone_y, drone_id)

            if hidden > 0:
                hidden_x = (x + ((total - 1) / 2) * 24 + 35)
                hidden_y = y - self.ZONE_RADIUS + 18
                self.canvas.create_text(
                    hidden_x,
                    hidden_y,
                    text=f"+{hidden}",
                    fill="#ffffff",
                    font=("Arial", 9, "bold"))

    def _draw_drones_on_connections(self) -> None:
        for drone in self.drones:
            if drone.current_connection is None:
                continue

            connection = drone.current_connection
            x1, y1 = self._zone_coords(connection.zone_a)
            x2, y2 = self._zone_coords(connection.zone_b)

            drone_x, drone_y = self._middle_point(x1, y1, x2, y2)
            self._draw_drone(drone_x, drone_y, drone.drone_id)

    def _draw_drone(self, x: float, y: float, drone_id: int) -> None:
        self.canvas.create_oval(
            x - self.DRONE_RADIUS,
            y - self.DRONE_RADIUS,
            x + self.DRONE_RADIUS,
            y + self.DRONE_RADIUS,
            fill="#00F0FF",
            outline="#1a1a1a",
            width=1)

        self.canvas.create_text(
            x, y,
            text=f"D{drone_id}",
            fill="black",
            font=("Arial", 8, "bold"))

    def _zone_coords(self, zone: Zone) -> tuple[float, float]:
        x = (zone.x - self.min_x) * self.SCALE + self.PADDING
        y = (zone.y - self.min_y) * self.SCALE + self.PADDING
        return x, y

    def _middle_point(self, x1: float, y1: float,
                      x2: float, y2: float) -> tuple[float, float]:
        return (x1 + x2) / 2, (y1 + y2) / 2

    def _get_zone_color(self, zone: Zone) -> str:
        if zone.color is not None:
            custom = {"rainbow": "#FF9800", "gold": "#FF9800"}
            return custom.get(zone.color, zone.color)

        colors = {
            ZoneType.RESTRICTED: "#FF9800",
            ZoneType.BLOCKED: "#4a4a4a",
            ZoneType.PRIORITY: "#1FBFEF",
            ZoneType.NORMAL: "#CFD8DC"}

        if zone.is_start:
            return "#4CAF50"
        if zone.is_end:
            return "#FF5252"

        return colors[zone.zone_type]
