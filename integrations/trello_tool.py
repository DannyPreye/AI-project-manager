from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from .trello import TrelloIntegration, TeamMember
from datetime import date, datetime
import json


# Initialize Trello Integration
trello_integration = TrelloIntegration()


# ================================ INPUT SCHEMAS ================================

class CreateBoardInput(BaseModel):
    """Input schema for creating a Trello board."""
    board_name: str = Field(..., description="Name of the board to create")
    description: str = Field(..., description="Description of the board")
    team_members_json: str = Field(
        default="[]",
        description="JSON string of team members array with fields: name, email, role, skills. Example: '[{\"name\":\"John\",\"email\":\"john@example.com\",\"role\":\"Developer\",\"skills\":[\"Python\"]}]'"
    )


class CreateListInput(BaseModel):
    """Input schema for creating a Trello list."""
    board_id: str = Field(..., description="The Trello board ID where the list will be created")
    list_name: str = Field(..., description="Name of the list (e.g., 'To Do', 'In Progress', 'Done')")
    position: int = Field(default=1, description="Position of the list on the board (1 = leftmost, higher numbers go right)")


class UpdateListInput(BaseModel):
    """Input schema for updating a Trello list."""
    list_id: str = Field(..., description="The Trello list ID to update")
    list_name: str = Field(..., description="New name for the list")


class DeleteListInput(BaseModel):
    """Input schema for deleting a Trello list."""
    list_id: str = Field(..., description="The Trello list ID to delete")


class CreateCardInput(BaseModel):
    """Input schema for creating a Trello card."""
    list_id: str = Field(..., description="The Trello list ID where the card will be created")
    card_name: str = Field(..., description="Name/title of the card")
    description: str = Field(..., description="Detailed description of the card/task")
    team_member_ids: str = Field(
        default="[]",
        description="JSON array of team member IDs to assign. Example: '[\"id1\",\"id2\"]'"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date in YYYY-MM-DD format (e.g., '2025-11-15')"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="Due date in YYYY-MM-DD format (e.g., '2025-12-01')"
    )


class UpdateCardInput(BaseModel):
    """Input schema for updating a Trello card."""
    card_id: str = Field(..., description="The Trello card ID to update")
    card_name: str = Field(..., description="New name/title of the card")
    description: str = Field(..., description="Updated description of the card")
    team_member_ids: str = Field(
        default="[]",
        description="JSON array of team member IDs. Example: '[\"id1\",\"id2\"]'"
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date in YYYY-MM-DD format"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="Due date in YYYY-MM-DD format"
    )


class DeleteCardInput(BaseModel):
    """Input schema for deleting a Trello card."""
    card_id: str = Field(..., description="The Trello card ID to delete")


class MoveCardInput(BaseModel):
    """Input schema for moving a card to another list."""
    card_id: str = Field(..., description="The Trello card ID to move")
    list_id: str = Field(..., description="The destination list ID")


class CreateChecklistInput(BaseModel):
    """Input schema for creating a checklist on a card."""
    card_id: str = Field(..., description="The Trello card ID to add checklist to")
    checklist_name: str = Field(..., description="Name of the checklist")


class UpdateChecklistInput(BaseModel):
    """Input schema for updating a checklist."""
    checklist_id: str = Field(..., description="The checklist ID to update")
    checklist_name: str = Field(..., description="New name for the checklist")


class DeleteChecklistInput(BaseModel):
    """Input schema for deleting a checklist."""
    checklist_id: str = Field(..., description="The checklist ID to delete")


class AddChecklistItemInput(BaseModel):
    """Input schema for adding an item to a checklist."""
    checklist_id: str = Field(..., description="The checklist ID to add item to")
    item_name: str = Field(..., description="Name of the checklist item")


class CreateLabelInput(BaseModel):
    """Input schema for creating a label."""
    card_id: str = Field(..., description="The card ID to create label on")
    label_name: str = Field(..., description="Name of the label")
    color: str = Field(
        default="blue",
        description="Color of the label (yellow, purple, blue, red, green, orange, black, sky, pink, lime)"
    )


class UpdateLabelInput(BaseModel):
    """Input schema for updating a label."""
    label_id: str = Field(..., description="The label ID to update")
    label_name: str = Field(..., description="New name for the label")
    color: str = Field(..., description="New color for the label")


class DeleteLabelInput(BaseModel):
    """Input schema for deleting a label."""
    label_id: str = Field(..., description="The label ID to delete")


class AddLabelToCardInput(BaseModel):
    """Input schema for adding a label to a card."""
    card_id: str = Field(..., description="The card ID")
    label_id: str = Field(..., description="The label ID to add")


class RemoveLabelFromCardInput(BaseModel):
    """Input schema for removing a label from a card."""
    card_id: str = Field(..., description="The card ID")
    label_id: str = Field(..., description="The label ID to remove")


# ================================ TOOLS ================================

# class TrelloCreateBoardTool(BaseTool):
#     name: str = "Create Trello Board"
#     description: str = """Creates a new Trello board and invites team members.
#     Returns the board object with board ID. Use this to set up a new project workspace."""
#     args_schema: Type[BaseModel] = CreateBoardInput

#     def _run(self, board_name: str, description: str, team_members_json: str = "[]") -> str:
#         try:
#             # Parse team members JSON
#             team_members_data = json.loads(team_members_json)
#             team_members = [TeamMember(**member) for member in team_members_data]

#             board = trello_integration.create_board(
#                 board_name=board_name,
#                 description=description,
#                 team_members=team_members
#             )
#             return f"✅ Successfully created board '{board_name}' (ID: {board['id']}). Team members invited."
#         except Exception as e:
#             return f"❌ Error creating board: {str(e)}"


class TrelloCreateListTool(BaseTool):
    name: str = "Create Trello List"
    description: str = """Creates a new list on a Trello board.
    Use this to create workflow stages like 'To Do', 'In Progress', 'Review', 'Done'."""
    args_schema: Type[BaseModel] = CreateListInput

    def _run(self, board_id: str, list_name: str, position: int = 1) -> str:
        try:
            list_obj = trello_integration.create_list(board_id=board_id, list_name=list_name, position=position)
            return f"✅ Successfully created list '{list_name}' (ID: {list_obj['id']}) on board {board_id}"
        except Exception as e:
            return f"❌ Error creating list: {str(e)}"


class TrelloUpdateListTool(BaseTool):
    name: str = "Update Trello List"
    description: str = """Updates the name of an existing Trello list."""
    args_schema: Type[BaseModel] = UpdateListInput

    def _run(self, list_id: str, list_name: str) -> str:
        try:
            list_obj = trello_integration.update_list(list_id=list_id, list_name=list_name)
            return f"✅ Successfully updated list {list_id} to '{list_name}'"
        except Exception as e:
            return f"❌ Error updating list: {str(e)}"


class TrelloDeleteListTool(BaseTool):
    name: str = "Delete Trello List"
    description: str = """Deletes a Trello list. Use with caution as this is permanent."""
    args_schema: Type[BaseModel] = DeleteListInput

    def _run(self, list_id: str) -> str:
        try:
            trello_integration.delete_list(list_id=list_id)
            return f"✅ Successfully deleted list {list_id}"
        except Exception as e:
            return f"❌ Error deleting list: {str(e)}"


class TrelloCreateCardTool(BaseTool):
    name: str = "Create Trello Card"
    description: str = """Creates a new card (task) on a Trello list with details, assignees, and due date.
    This is the main tool for creating individual tasks in your project."""
    args_schema: Type[BaseModel] = CreateCardInput

    def _run(
        self,
        list_id: str,
        card_name: str,
        description: str,
        team_member_ids: str = "[]",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        try:
            # Parse team member IDs
            member_ids = json.loads(team_member_ids)

            # Parse dates
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

            card = trello_integration.create_card(
                list_id=list_id,
                card_name=card_name,
                description=description,
                team_member_ids=member_ids,
                start_date=start_date_obj,
                end_date=end_date_obj
            )
            return f"✅ Successfully created card '{card_name}' (ID: {card['id']}) in list {list_id}"
        except Exception as e:
            return f"❌ Error creating card: {str(e)}"


class TrelloUpdateCardTool(BaseTool):
    name: str = "Update Trello Card"
    description: str = """Updates an existing Trello card's details, assignees, or due date."""
    args_schema: Type[BaseModel] = UpdateCardInput

    def _run(
        self,
        card_id: str,
        card_name: str,
        description: str,
        team_member_ids: str = "[]",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        try:
            member_ids = json.loads(team_member_ids)
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

            card = trello_integration.update_card(
                card_id=card_id,
                card_name=card_name,
                description=description,
                team_member_ids=member_ids,
                start_date=start_date_obj,
                end_date=end_date_obj
            )
            return f"✅ Successfully updated card '{card_name}' (ID: {card_id})"
        except Exception as e:
            return f"❌ Error updating card: {str(e)}"


class TrelloDeleteCardTool(BaseTool):
    name: str = "Delete Trello Card"
    description: str = """Deletes a Trello card. Use with caution as this is permanent."""
    args_schema: Type[BaseModel] = DeleteCardInput

    def _run(self, card_id: str) -> str:
        try:
            trello_integration.delete_card(card_id=card_id)
            return f"✅ Successfully deleted card {card_id}"
        except Exception as e:
            return f"❌ Error deleting card: {str(e)}"


class TrelloMoveCardTool(BaseTool):
    name: str = "Move Trello Card"
    description: str = """Moves a card from one list to another (e.g., from 'To Do' to 'In Progress').
    Use this to update task status in the workflow."""
    args_schema: Type[BaseModel] = MoveCardInput

    def _run(self, card_id: str, list_id: str) -> str:
        try:
            card = trello_integration.move_card_to_list(card_id=card_id, list_id=list_id)
            return f"✅ Successfully moved card {card_id} to list {list_id}"
        except Exception as e:
            return f"❌ Error moving card: {str(e)}"


class TrelloCreateChecklistTool(BaseTool):
    name: str = "Create Checklist on Card"
    description: str = """Creates a checklist on a Trello card. Use this to break down a task into sub-tasks."""
    args_schema: Type[BaseModel] = CreateChecklistInput

    def _run(self, card_id: str, checklist_name: str) -> str:
        try:
            checklist = trello_integration.create_checklist(card_id=card_id, checklist_name=checklist_name)
            return f"✅ Successfully created checklist '{checklist_name}' (ID: {checklist['id']}) on card {card_id}"
        except Exception as e:
            return f"❌ Error creating checklist: {str(e)}"


class TrelloUpdateChecklistTool(BaseTool):
    name: str = "Update Checklist"
    description: str = """Updates the name of an existing checklist."""
    args_schema: Type[BaseModel] = UpdateChecklistInput

    def _run(self, checklist_id: str, checklist_name: str) -> str:
        try:
            checklist = trello_integration.update_checklist(checklist_id=checklist_id, checklist_name=checklist_name)
            return f"✅ Successfully updated checklist {checklist_id} to '{checklist_name}'"
        except Exception as e:
            return f"❌ Error updating checklist: {str(e)}"


class TrelloDeleteChecklistTool(BaseTool):
    name: str = "Delete Checklist"
    description: str = """Deletes a checklist from a card."""
    args_schema: Type[BaseModel] = DeleteChecklistInput

    def _run(self, checklist_id: str) -> str:
        try:
            trello_integration.delete_checklist(checklist_id=checklist_id)
            return f"✅ Successfully deleted checklist {checklist_id}"
        except Exception as e:
            return f"❌ Error deleting checklist: {str(e)}"


class TrelloAddChecklistItemTool(BaseTool):
    name: str = "Add Item to Checklist"
    description: str = """Adds a new item to an existing checklist on a card."""
    args_schema: Type[BaseModel] = AddChecklistItemInput

    def _run(self, checklist_id: str, item_name: str) -> str:
        try:
            trello_integration.add_item_to_checklist(checklist_id=checklist_id, item_name=item_name)
            return f"✅ Successfully added item '{item_name}' to checklist {checklist_id}"
        except Exception as e:
            return f"❌ Error adding checklist item: {str(e)}"


class TrelloCreateLabelTool(BaseTool):
    name: str = "Create Label"
    description: str = """Creates a new label on a card. Use labels to categorize tasks (e.g., 'Bug', 'Feature', 'High Priority')."""
    args_schema: Type[BaseModel] = CreateLabelInput

    def _run(self, card_id: str, label_name: str, color: str = "blue") -> str:
        try:
            label = trello_integration.create_label(card_id=card_id, label_name=label_name, color=color)
            return f"✅ Successfully created {color} label '{label_name}' (ID: {label['id']}) on card {card_id}"
        except Exception as e:
            return f"❌ Error creating label: {str(e)}"


class TrelloUpdateLabelTool(BaseTool):
    name: str = "Update Label"
    description: str = """Updates an existing label's name or color."""
    args_schema: Type[BaseModel] = UpdateLabelInput

    def _run(self, label_id: str, label_name: str, color: str) -> str:
        try:
            label = trello_integration.update_label(label_id=label_id, label_name=label_name, color=color)
            return f"✅ Successfully updated label {label_id} to '{label_name}' ({color})"
        except Exception as e:
            return f"❌ Error updating label: {str(e)}"


class TrelloDeleteLabelTool(BaseTool):
    name: str = "Delete Label"
    description: str = """Deletes a label."""
    args_schema: Type[BaseModel] = DeleteLabelInput

    def _run(self, label_id: str) -> str:
        try:
            trello_integration.delete_label(label_id=label_id)
            return f"✅ Successfully deleted label {label_id}"
        except Exception as e:
            return f"❌ Error deleting label: {str(e)}"


class TrelloAddLabelToCardTool(BaseTool):
    name: str = "Add Label to Card"
    description: str = """Adds an existing label to a card."""
    args_schema: Type[BaseModel] = AddLabelToCardInput

    def _run(self, card_id: str, label_id: str) -> str:
        try:
            trello_integration.add_label_to_card(card_id=card_id, label_id=label_id)
            return f"✅ Successfully added label {label_id} to card {card_id}"
        except Exception as e:
            return f"❌ Error adding label to card: {str(e)}"


class TrelloRemoveLabelFromCardTool(BaseTool):
    name: str = "Remove Label from Card"
    description: str = """Removes a label from a card."""
    args_schema: Type[BaseModel] = RemoveLabelFromCardInput

    def _run(self, card_id: str, label_id: str) -> str:
        try:
            trello_integration.remove_label_from_card(card_id=card_id, label_id=label_id)
            return f"✅ Successfully removed label {label_id} from card {card_id}"
        except Exception as e:
            return f"❌ Error removing label from card: {str(e)}"


# ================================ CONVENIENCE FUNCTIONS ================================

def get_all_trello_tools():
    """
    Returns all Trello tools as a list for easy assignment to agents.

    Usage:
        from integrations.trello_tool import get_all_trello_tools

        agent = Agent(
            role="Project Manager",
            tools=get_all_trello_tools()
        )
    """
    return [
        # TrelloCreateBoardTool(),
        TrelloCreateListTool(),
        TrelloUpdateListTool(),
        TrelloDeleteListTool(),
        TrelloCreateCardTool(),
        TrelloUpdateCardTool(),
        TrelloDeleteCardTool(),
        TrelloMoveCardTool(),
        TrelloCreateChecklistTool(),
        TrelloUpdateChecklistTool(),
        TrelloDeleteChecklistTool(),
        TrelloAddChecklistItemTool(),
        TrelloCreateLabelTool(),
        TrelloUpdateLabelTool(),
        TrelloDeleteLabelTool(),
        TrelloAddLabelToCardTool(),
        TrelloRemoveLabelFromCardTool(),
    ]


def get_essential_trello_tools():
    """
    Returns only the most essential Trello tools for basic project management.

    Usage:
        from integrations.trello_tool import get_essential_trello_tools

        agent = Agent(
            role="Project Manager",
            tools=get_essential_trello_tools()
        )
    """
    return [
        # TrelloCreateBoardTool(),
        TrelloCreateListTool(),
        TrelloCreateCardTool(),
        TrelloMoveCardTool(),
        TrelloCreateChecklistTool(),
        TrelloAddChecklistItemTool(),
    ]
