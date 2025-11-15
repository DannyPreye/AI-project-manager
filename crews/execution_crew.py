from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from integrations.trello_tool import get_all_trello_tools
from pydantic import BaseModel
import os

class Label(BaseModel):
   name: str
   color: str

class CardSpecification(BaseModel):
   list_id: str
   card_name: str
   description: str
   start_date: str
   end_date: str
   labels: list[Label]
   checklist_items: list[str]

load_dotenv()

llm = LLM(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# Get all Trello tools
trello_tools = get_all_trello_tools()

# ================================ Agents ================================

trello_card_creator = Agent(
    role="Trello Card Creator",
    goal="Create ONE Trello card with complete details (card, checklist, labels)",
    backstory="""You are a focused task creator who creates one complete Trello card at a time.

    Your process for EACH card:
    1. Create the card using provided specifications
    2. Extract the card ID from the success message
    3. Create checklist on that card
    4. Extract checklist ID
    5. Add ALL checklist items one by one
    6. Create ALL labels on the card

    You complete the ENTIRE workflow for the single card before finishing.
    You use EXACT specifications provided - no modifications.""",
    tools=trello_tools,
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# ================================ Tasks ================================

create_single_card_task = Task(
    description="""
    Create Trello card with all details from the specification.

    Card Specification: {card_specification}

    STEP 1: CREATE THE CARD
    Use "Create Trello Card" tool with:
    - list_id: spec.list_id
    - card_name: spec.card_name
    - description: spec.description
    - team_member_ids: "[]"
    - start_date: spec.start_date
    - end_date: spec.end_date

    STEP 2: EXTRACT CARD ID
    From success message: "✅ Successfully created card 'X' (ID: 673abc123)"
    Card ID: 673abc123

    STEP 3: CREATE CHECKLIST
    Use "Create Checklist on Card" tool:
    - card_id: [from step 2]
    - checklist_name: "Acceptance Criteria"

    STEP 4: EXTRACT CHECKLIST ID
    From success message: "✅ Successfully created checklist 'X' (ID: abc123)"
    Checklist ID: abc123

    STEP 5: ADD ALL CHECKLIST ITEMS
    For EACH item in card_specification.checklist_items:
    Use "Add Item to Checklist" tool:
    - checklist_id: [from step 4]
    - item_name: [checklist item text]

    STEP 6: CREATE ALL LABELS
    For EACH label in card_specification.labels:
    Use "Create Label" tool:
    - card_id: [from step 2]
    - label_name: label.name
    - color: label.color

    FINAL OUTPUT - Return JSON:
    {{
        "card_id": "[extracted from step 2]",
        "card_name": "[from specification]",
        "checklist_created": true/false,
        "checklist_items_added": X,
        "labels_created": Y,
        "status": "completed" or "failed",
        "error_message": "[if failed, explain why]"
    }}

    CRITICAL: Complete ALL steps before finishing. Do not skip checklist or labels.
    """,
    agent=trello_card_creator,
    expected_output="""JSON object with:
    - card_id: the created card's ID
    - card_name: name of the card
    - checklist_created: boolean
    - checklist_items_added: count
    - labels_created: count
    - status: "completed" or "failed"
    - error_message: optional, if failed"""
)

# ================================ Crew ================================

execution_crew = Crew(
    agents=[trello_card_creator],
    tasks=[create_single_card_task],
    verbose=True,
    memory=False,
    cache=False
)
