import yaml
from typing import List, Dict, Optional

# Define the structure of the parsed config
class SMTPConfig:
    def __init__(
        self,
        host: str,
        port: int,
        authentication: bool,
        auth_type: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        credentials: Optional[List[Dict[str, str]]] = None,
        tls: bool = True,
        allow_relay: bool = False,
    ):
        self.host = host
        self.port = port
        self.authentication = authentication
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.credentials = credentials or []
        self.tls = tls
        self.allow_relay = allow_relay

    def __str__(self):
        return (
            f"SMTPConfig(host={self.host}, port={self.port}, "
            f"authentication={self.authentication}, tls={self.tls}, "
            f"allow_relay={self.allow_relay})"
        )


# Load the YAML file
def load_config(file_path: str) -> List[SMTPConfig]:
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)

    smtp_configs = []
    for input_config in config["inputs"]:
        if input_config["type"] == "smtp":
            smtp_configs.append(SMTPConfig(**input_config))
    return smtp_configs