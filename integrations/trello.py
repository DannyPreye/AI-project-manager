from dotenv import load_dotenv
from os import getenv
from trello import TrelloApi
from pydantic import BaseModel
from typing import Optional
from datetime import date

from project.models import ProjectMember

load_dotenv()


class TeamMember(BaseModel):
    id:Optional[str] = None
    name: str
    email: str
    role: str
    skills: list[str]


trello = TrelloApi(getenv("TRELLO_API_KEY"))
trello.set_token(getenv("TRELLO_API_TOKEN"))

class TrelloIntegration:
    def create_board(self, board_name: str, description, team_members: list[TeamMember]):
        board = trello.boards.new(name=board_name, desc=description,defaultLists=None)
        # Invite all team members to the board
        # for member in team_members:
        #    memeber=  trello.boards.new_member(board.id, email=member.email, type="normal")
        # update the database model with the member id
        return board

    def invite_team_members(self, board_id:str, team_members: list[TeamMember]):
        """
        Invites team members to a Trello board and returns their Trello member IDs.
        Returns a dict mapping email to trello_member_id for later use.
        """
        member_mapping = {}

        for member in team_members:
            result = trello.boards.update_member(board_id, email=member["email"], fullName=member["name"], type="normal")

            # Get the members list from the result
            result_members = result["members"]
            print(f"Board members after adding {member['name']}:", result_members, "\n")

            # Find the current member in the result
            find_current_member = next(
                (x for x in result_members if x["fullName"] == member["name"]),
                None
            )

            if find_current_member:
                # Store the mapping of email to Trello member ID
                member_mapping[member["email"]] = find_current_member["id"]
                print(f"✅ Successfully invited {member['name']} with Trello ID: {find_current_member['id']}")
            else:
                print(f"⚠️ Warning: Could not find member {member['name']} in Trello board members")
                member_mapping[member["email"]] = None

        return member_mapping
    def get_team_members(self, board_id:str):
        members = trello.boards.get_members(board_id)




        return members
    def update_board(self, board_id:str, board_name:str, description:str):
        board = trello.boards.update(board_id, name=board_name, desc=description)
        return board
    def delete_board(self, board_id:str):
       board = trello.boards.delete(board_id)
       return board

    def create_list(self, board_id: str, list_name: str, position:int):
        list = trello.lists.new(name=list_name, idBoard=board_id, pos=position)
        print("list created: ", list)
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

    def create_checklist(self, card_id:str, checklist_name:str):
        checklist = trello.cards.new_checklist(card_id, name=checklist_name)
        return checklist
    def update_checklist(self, checklist_id:str, checklist_name:str):
        checklist = trello.cards.update_checklist(checklist_id, name=checklist_name)
        return checklist
    def delete_checklist(self, checklist_id:str):
        trello.cards.delete_checklist(checklist_id)
    def add_item_to_checklist(self, checklist_id:str, item_name:str):
        """Add an item to an existing checklist"""
        item = trello.checklists.new_checkitem(checklist_id, name=item_name)
        return item

