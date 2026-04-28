from src import Zone


class Connection:
    def __init__(self, zone1: Zone, zone2: Zone, max_capacity: int = 1):
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_capacity = max_capacity
