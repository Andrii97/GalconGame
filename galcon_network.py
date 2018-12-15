class GalconNetwork():
    def __init__(self):
        pass


class Packet():
    def __init__(self, json_data):
        type, arguments = self.parse_json(json_data)
        self.command = Command(type, arguments)

    def parse_json(self, data):
        pass


class Command():
    def __init__(self, type, arguments):
        self.type = type
        self.arguments = arguments
