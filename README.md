# AI-Powered Project Manager with Trello Integration

An intelligent project management system that uses AI agents to conduct research, create detailed project plans, and automatically set up Trello boards with tasks, assignments, and timelines.

## 🚀 Features

- **AI Research Crew**: Conducts comprehensive industry research, project analysis, and team assessment
- **AI Planning Crew**: Breaks down projects into detailed tasks with timelines, assignments, and dependencies
- **AI Execution Crew**: Automatically creates and organizes Trello boards with cards, checklists, labels, and due dates
- **REST API**: Django REST Framework backend for managing organizations, projects, and team members
- **Authentication**: JWT-based authentication with email verification
- **Swagger Documentation**: Auto-generated API documentation

## 🏗️ Architecture

The system consists of three main components:

### 1. **Research Crew** (`crews/research_crew.py`)
- Industry Researcher: Analyzes market trends and competitive landscape
- Project Analyzer: Evaluates technical requirements and risks
- Team Assessor: Reviews team capabilities and skill gaps
- Research Synthesizer: Consolidates findings into actionable insights

### 2. **Planning Crew** (`crews/planning_crew.py`)
- Task Generator: Breaks down projects into 20-50 granular, actionable tasks
- Timeline Planner: Creates realistic schedules with milestones and critical paths
- Task Assigner: Matches tasks to team members based on skills and capacity
- Planning Synthesizer: Consolidates all planning outputs into execution-ready format

### 3. **Execution Crew** (`crews/execution_crew.py`)
- Board Manager: Creates organized Trello board structure
- Task Manager: Transforms tasks into detailed Trello cards with checklists
- Workflow Organizer: Ensures proper task flow and dependencies

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL
- Trello Account with API credentials
- OpenAI API Key

## 🔧 Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd project_manager_crew
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-django-secret-key
DEBUG=True

# Database Configuration
DB_NAME=project_manager_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Trello Configuration
TRELLO_API_KEY=your-trello-api-key
TRELLO_API_SECRET=your-trello-api-secret
TRELLO_TOKEN=your-trello-token

# JWT Configuration
ACCESS_TOKEN_LIFETIME=30  # minutes
REFRESH_TOKEN_LIFETIME=1  # days

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 5. Get Trello Credentials

1. Get your API Key: https://trello.com/app-key
2. Generate a token using the link on the API key page
3. Add both to your `.env` file

For detailed instructions, see `integrations/SETUP.md`

### 6. Set up the database

```bash
# Create PostgreSQL database
createdb project_manager_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

## 🤖 Running the AI Crews

### From Python Script

```bash
cd crews
python main.py
```

### From Django (Integration)

```python
from crews.main import run_flow
import asyncio

project_data = {
    "project_name": "E-Commerce Platform",
    "project_description": "A modern e-commerce platform with AI recommendations",
    "project_timeline": "2025-01-01 to 2025-06-30",
    "industry": "E-Commerce",
    "team_members": [
        {
            "name": "John Doe",
            "email": "john@example.com",
            "role": "Full Stack Developer",
            "skills": ["python", "django", "react", "postgresql"],
            "trello_member_id": "trello_id_here"
        },
        # ... more team members
    ]
}

asyncio.run(run_flow(project_data))
```

## 🔑 API Endpoints

### Authentication
- `POST /api/register/` - Register new user and organization
- `POST /api/login/` - Login and get JWT tokens
- `POST /api/verify-email/` - Verify email with code
- `POST /api/request-reset-password/` - Request password reset
- `POST /api/reset-password/` - Reset password with token

### Organizations
- `GET /api/organizations/` - List organizations
- `POST /api/organizations/` - Create organization
- `GET /api/organizations/{id}/` - Get organization details
- `PUT /api/organizations/{id}/` - Update organization
- `DELETE /api/organizations/{id}/` - Delete organization

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

## 🗂️ Project Structure

```
project_manager_crew/
├── crews/                      # AI agent crews
│   ├── research_crew.py       # Research and analysis agents
│   ├── planning_crew.py       # Task planning and scheduling agents
│   ├── execution_crew.py      # Trello board creation agents
│   └── main.py                # Main workflow orchestration
├── integrations/              # External service integrations
│   ├── trello.py              # Trello API wrapper
│   ├── trello_tool.py         # CrewAI tools for Trello
│   ├── index.py               # Abstract integration interface
│   └── SETUP.md               # Integration setup guide
├── organization/              # Organization and user management
│   ├── models.py              # User, Organization models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   └── urls.py                # URL routing
├── project/                   # Project management
│   ├── models.py              # Project, ProjectMember models
│   ├── views.py               # API views
│   └── tasks.py               # Background tasks
├── pm_master/                 # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .gitignore
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **Django 5.2** - Web framework
- **Django REST Framework** - REST API
- **PostgreSQL** - Database
- **JWT** - Authentication

### AI & Automation
- **CrewAI** - Multi-agent AI framework
- **OpenAI GPT-4** - Language model
- **LangChain** - AI tooling

### Integrations
- **Trello API** (via trello-py) - Project management
- **drf-yasg** - API documentation

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 How It Works

1. **Input**: Provide project details (name, description, timeline, industry, team members)

2. **Research Phase**:
   - AI agents research the industry and analyze project requirements
   - Team capabilities are assessed
   - Comprehensive research report is generated

3. **Planning Phase**:
   - Project is broken down into 20-50 detailed tasks
   - Realistic timeline with milestones is created
   - Tasks are assigned to team members based on skills
   - Complete execution plan is synthesized

4. **Execution Phase**:
   - Trello board is created automatically
   - Lists are set up (Backlog, To Do, In Progress, Review, Testing, Done)
   - Cards are created for each task with:
     - Detailed descriptions
     - Acceptance criteria checklists
     - Due dates
     - Team member assignments
     - Priority labels
     - Type labels (Feature, Bug, Documentation)

5. **Output**: A fully populated Trello board ready for your team to start working!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'crewai'`
- **Solution**: Make sure you've activated your virtual environment and installed dependencies

**Issue**: `pydantic_core._pydantic_core.ValidationError`
- **Solution**: Check that all required fields are provided in `project_data`

**Issue**: Trello API errors
- **Solution**: Verify your Trello API credentials in `.env` and ensure your token has write permissions

**Issue**: Database connection errors
- **Solution**: Make sure PostgreSQL is running and credentials in `.env` are correct

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the API documentation at `/swagger/`
- Review crew documentation in `crews/README.md`

## 🎯 Roadmap

- [ ] Add support for ClickUp integration
- [ ] Add support for Jira integration
- [ ] Real-time progress tracking
- [ ] Email notifications for task assignments
- [ ] Advanced analytics and reporting
- [ ] Mobile app integration
- [ ] Slack/Discord bot integration

---

Built with ❤️ using Django, CrewAI, and OpenAI

