from abc import ABC, abstractmethod
from pydantic import BaseModel


class TeamMember(BaseModel):
    name: str
    email: str
    role: str
    skills: list[str]


class Project(BaseModel):
    name: str
    description: str
    timeline: str
    team_members: list[TeamMember]


class Card(BaseModel):
    name: str
    description: str
    due_date: str
    assignee: TeamMember


class List(BaseModel):
    name: str
    cards: list[Card]


class Integration(ABC):
    def __init__(self, api_key: str, workspace_id: str = None):
        self.api_key = api_key
        self.workspace_id = workspace_id

    @abstractmethod
    def create_project(
        self,
        project_name: str,
        project_description: str,
        project_timeline: str,
        team_members: list[TeamMember],
    ):
        pass

    @abstractmethod
    def create_list(self, project_id: str, list_name: str):
        pass

    @abstractmethod
    def create_card(
        self,
        list_id: str,
        card_name: str,
        card_description: str,
        card_due_date: str,
        card_assignee: TeamMember,
    ):
        pass

    @abstractmethod
    def get_project(self, project_id: str) -> Project:
        pass

    @abstractmethod
    def get_list(self, list_id: str) -> List:
        pass

    @abstractmethod
    def get_card(self, card_id: str) -> Card:
        pass
