from dotenv import load_dotenv
from os import getenv
from trello import TrelloApi
from pydantic import BaseModel
from typing import Optional
from datetime import date
load_dotenv()


class TeamMember(BaseModel):
    id:Optional[str] = None
    name: str
    email: str
    role: str
    skills: list[str]


trello = TrelloApi(getenv("TRELLO_API_KEY"))

class TrelloIntegration:
    def create_board(self, board_name: str, description, team_members: list[TeamMember]):
        board = trello.boards.new(name=board_name, desc=description)
        # Invite all team members to the board
        # for member in team_members:
        #    memeber=  trello.boards.new_member(board.id, email=member.email, type="normal")
        # update the database model with the member id
        return board

    def update_board(self, board_id:str, board_name:str, description:str):
        board = trello.boards.update(board_id, name=board_name, desc=description)
        return board
    def delete_board(self, board_id:str):
       board = trello.boards.delete(board_id)
       return board

    def create_list(self, board_id: str, list_name: str):
        list = trello.lists.new(name=list_name, idBoard=board_id)
        return list
    def update_list(self, list_id:str, list_name:str):
        list = trello.lists.update(list_id, name=list_name)
        return list
    def delete_list(self, list_id:str):
        trello.lists.delete(list_id)

    def create_card(self, list_id:str, card_name:str, description:str, team_member_ids:list[str], start_date:date, end_date:date):
        card = trello.cards.new(name=card_name, desc=description, idList=list_id, due=end_date)
        return card
    def update_card(self, card_id:str, card_name:str, description:str, team_member_ids:list[str], start_date:date, end_date:date):
        card = trello.cards.update(card_id, name=card_name, desc=description, due=end_date)
        return card
    def delete_card(self, card_id:str):
        trello.cards.delete(card_id)
    def create_label(self, card_id:str, label_name:str, color:str):
        label = trello.cards.new_label(card_id, name=label_name, color=color)
        return label
    def update_label(self, label_id:str, label_name:str, color:str):
        label = trello.cards.update_label(label_id, name=label_name, color=color)
        return label
    def delete_label(self, label_id:str):
        trello.cards.delete_label(label_id)
    def add_label_to_card(self, card_id:str, label_id:str):
        trello.cards.add_label(card_id, label_id)
    def remove_label_from_card(self, card_id:str, label_id:str):
        trello.cards.remove_label(card_id, label_id)

    def move_card_to_list(self, card_id:str, list_id:str):
      return  trello.cards.move_to_list(card_id, list_id)
