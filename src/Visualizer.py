import tkinter as tk

from src.models import Graph, Zone, ZoneType, Drone


class GraphView:

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    PADDING = 100
    ZONE_RADIUS = 35
    DRONE_RADIUS = 10
    LINE_WIDTH = 5

    def __init__(self, graph: Graph, drones: list[Drone]):
        self.graph = graph
        self.drones = drones

        self.scale = 100
        self.min_x = 0
        self.min_y = 0

        self.__fit_graph_to_window()

        self.root = tk.Tk()
        self.root.title("Fly-in")

        self.canvas = tk.Canvas(
            self.root,
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            bg="#1e1e1e"
        )
        self.on_next_turn = None
        self.next_button = tk.Button(self.root,
                                     text="Next Turn",
                                     command=self.__handle_next_turn)
        self.next_button.pack()
        self.canvas.pack(fill="both", expand=True)

    def run(self) -> None:
        self.draw()
        self.root.mainloop()

    def draw(self) -> None:
        self.canvas.delete("all")
        self.__draw_connections()
        self.__draw_zones()
        self.__draw_drones()
        self.__draw_drones_on_connections()

    def __handle_next_turn(self) -> None:
        if self.on_next_turn is not None:
            self.on_next_turn()
            self.draw()

    def set_on_next_turn(self, callback) -> None:
        self.on_next_turn = callback

    def __fit_graph_to_window(self) -> None:
        """Calculate a simple scale so the whole graph fits on screen."""
        if not self.graph.zones:
            return

        xs = [zone.x for zone in self.graph.zones.values()]
        ys = [zone.y for zone in self.graph.zones.values()]

        self.min_x = min(xs)
        self.min_y = min(ys)

        width = max(max(xs) - self.min_x, 1)
        height = max(max(ys) - self.min_y, 1)

        usable_width = self.WINDOW_WIDTH - self.PADDING * 2
        usable_height = self.WINDOW_HEIGHT - self.PADDING * 2

        self.scale = min(usable_width / width, usable_height / height)

    def __draw_connections(self) -> None:
        for connection in self.graph.connections:
            x1, y1 = self.__zone_coords(connection.zone_a)
            x2, y2 = self.__zone_coords(connection.zone_b)

            self.canvas.create_line(x1, y1, x2, y2, fill="white",
                                    width=self.LINE_WIDTH)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2

            self.canvas.create_text(
                mid_x,
                mid_y - 15,
                text=f"cap={connection.max_capacity}",
                fill="white",
                font=("Arial", 9, "bold")
            )

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
                width=2
            )

            self.canvas.create_text(
                x,
                y,
                text=zone.name,
                fill="black",
                font=("Arial", 10, "bold")
            )

    def __draw_drones(self) -> None:
        for zone in self.graph.zones.values():
            x, y = self.__zone_coords(zone)
            drones = list(zone.current_drones)
            total = len(drones)
            for index, drone_id in enumerate(drones):
                offset_x = (index - (total - 1) / 2) * 22
                drone_x = x + offset_x
                drone_y = y - self.ZONE_RADIUS - 15
                self.canvas.create_oval(
                    drone_x - self.DRONE_RADIUS,
                    drone_y - self.DRONE_RADIUS,
                    drone_x + self.DRONE_RADIUS,
                    drone_y + self.DRONE_RADIUS,
                    fill="cyan", outline="black",)
                self.canvas.create_text(
                    drone_x, drone_y,
                    text=f"D{drone_id}",
                    fill="black", font=("Arial", 8, "bold"),)

    def __draw_drones_on_connections(self) -> None:
        for drone in self.drones:
            if drone.current_connection is None:
                continue

            connection = drone.current_connection

            x1, y1 = self.__zone_coords(connection.zone_a)
            x2, y2 = self.__zone_coords(connection.zone_b)

            drone_x = (x1 + x2) / 2
            drone_y = (y1 + y2) / 2

            self.canvas.create_oval(
                drone_x - self.DRONE_RADIUS,
                drone_y - self.DRONE_RADIUS,
                drone_x + self.DRONE_RADIUS,
                drone_y + self.DRONE_RADIUS,
                fill="cyan",
                outline="black"
            )

            self.canvas.create_text(
                drone_x,
                drone_y,
                text=f"D{drone.drone_id}",
                fill="black",
                font=("Arial", 8, "bold")
            )

    def __zone_coords(self, zone: Zone) -> tuple[float, float]:
        x = (zone.x - self.min_x) * self.scale + self.PADDING
        y = (zone.y - self.min_y) * self.scale + self.PADDING

        return x, y

    def __get_zone_color(self, zone: Zone) -> str:
        if zone.is_start:
            return "#4CAF50"

        if zone.is_end:
            return "#F44336"

        if zone.zone_type == ZoneType.RESTRICTED:
            return "#FF9800"

        if zone.zone_type == ZoneType.BLOCKED:
            return "#616161"

        if zone.zone_type == ZoneType.PRIORITY:
            return "#03A9F4"

        return "#E0E0E0"
