import glob
import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError


class PlaybookStep(BaseModel):
    action: str
    params: Dict[str, Any]
    timeout_seconds: int = 30
    on_failure: str = "rollback"  # abort | continue | rollback


class PlaybookTriggers(BaseModel):
    severity: Optional[List[str]] = None
    ttp: Optional[List[str]] = None


class Playbook(BaseModel):
    name: str
    version: str
    description: str
    triggers: PlaybookTriggers
    risk_level: str
    requires_approval: bool
    timeout_seconds: int
    steps: List[PlaybookStep]
    rollback: List[PlaybookStep]


class PlaybookLoader:

    def __init__(self, path: str = "playbooks"):
        self.path = path
        self.playbooks: Dict[str, Playbook] = {}

    def load(self) -> Dict[str, Playbook]:
        files = glob.glob(f"{self.path}/**/*.yaml", recursive=True)

        for file in files:
            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)

                playbook = Playbook(**data)
                self.playbooks[playbook.name] = playbook

                print(f"Loaded playbook: {playbook.name}")

            except ValidationError as e:
                print(f"Invalid playbook {file}: {e}")

            except Exception as e:
                print(f"Error loading {file}: {e}")

        return self.playbooks