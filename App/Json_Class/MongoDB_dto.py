from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class mongodb:
    connectionString: str
    DataBase: str

    @staticmethod
    def from_dict(obj: Any) -> 'mongodb':
        assert isinstance(obj, dict)
        connectionString = from_str(obj.get("connectionString"))
        DataBase = from_str(obj.get("DataBase"))

        return mongodb(connectionString, DataBase)

    def to_dict(self) -> dict:
        result: dict = {
            "connectionString": from_str(self.connectionString),
            "DataBase": from_str(self.DataBase),
            }
        return result
