from dataclasses import dataclass
from App.Json_Class.DtoUtilities import *

@dataclass
class EdgeDeviceProperties:
    Name: str
    Mode1: str
    Password: str
    Identity: str
    IPAddress: str
    TimeZone: str
    Description: str

    @staticmethod
    def from_dict(obj: Any) -> 'EdgeDeviceProperties':
        assert isinstance(obj, dict)
        Name = from_str(obj.get("Name"))
        Mode1 = from_str(obj.get("Mode1"))
        Password = from_str(obj.get("Password"))
        Identity = from_str(obj.get("Identity"))
        IPAddress = from_str(obj.get("IP Address"))
        TimeZone = from_str(obj.get("Time Zone"))
        Description = from_str(obj.get("Description"))
        return EdgeDeviceProperties(Name, Mode1, Password, Identity, IPAddress, TimeZone, Description)

    def to_dict(self) -> dict:
        result: dict = {}
        result["Name"] = from_str(self.Name)
        result["Mode1"] = from_str(self.Mode1)
        result["Password"] = from_str(self.Password)
        result["Identity"] = from_str(self.Identity)
        result["IP Address"] = from_str(self.IPAddress)
        result["Time Zone"] = from_str(self.TimeZone)
        result["Description"] = from_str(self.Description)
        return result