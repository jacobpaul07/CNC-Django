from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *


@dataclass
class EdgeDeviceProperties:
    Name: str
    Model: str
    Password: str
    Identity: str
    IPAddress: str
    TimeZone: str
    Description: str

    @staticmethod
    def from_dict(obj: Any) -> 'EdgeDeviceProperties':
        assert isinstance(obj, dict)
        Name = from_str(obj.get("Name"))
        Model = from_str(obj.get("Model"))
        Password = from_str(obj.get("Password"))
        Identity = from_str(obj.get("Identity"))
        IPAddress = from_str(obj.get("IP Address"))
        TimeZone = from_str(obj.get("Time Zone"))
        Description = from_str(obj.get("Description"))
        return EdgeDeviceProperties(Name, Model, Password, Identity, IPAddress, TimeZone, Description)

    def to_dict(self) -> dict:
        result: dict = {
            "Name": from_str(self.Name),
            "Model": from_str(self.Model),
            "Password": from_str(self.Password),
            "Identity": from_str(self.Identity),
            "IP Address": from_str(self.IPAddress),
            "Time Zone": from_str(self.TimeZone),
            "Description": from_str(self.Description)
            }
        return result
