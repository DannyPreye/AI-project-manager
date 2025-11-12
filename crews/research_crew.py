from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
import os

load_dotenv()

llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Tools - will only be used when needed
scrape_website_tool = ScrapeWebsiteTool()
serper_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# ================================ Agents ================================

research_coordinator = Agent(
    role="Research Coordinator",
    goal="Analyze project description and determine what additional research is actually needed",
    backstory="""You are an expert at evaluating project descriptions and determining
    what information is missing or needs clarification. You AVOID unnecessary web searches
    by first thoroughly analyzing what information is already provided.

    You only recommend web research when:
    1. Project description lacks specific technical details
    2. Industry trends/competitors need to be identified
    3. Best practices for the domain are not mentioned
    4. Team skills need to be matched against market requirements

    If the project description is detailed and complete, you say NO web research needed.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

industry_researcher = Agent(
    role="Industry Research Specialist",
    goal="Conduct targeted industry research ONLY when gaps are identified",
    backstory="""You are a senior market research analyst who conducts efficient,
    focused research. You ONLY use web search tools when explicitly told to research
    specific topics. You don't search just because you can - you search because
    there's a real information gap to fill.

    When research is needed, you focus on:
    - Specific competitors in the space
    - Recent industry trends (last 6-12 months)
    - Technical challenges unique to the domain
    - Best practices that aren't obvious""",
    tools=[scrape_website_tool, serper_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

project_analyzer = Agent(
    role="Project Scope Analyst",
    goal="Analyze project requirements and fill gaps with targeted research if needed",
    backstory="""Senior technical project analyst who thoroughly analyzes project
    descriptions. You work with what's provided first, and only request additional
    research when critical information is missing.

    You extract maximum value from existing information before asking for more.""",
    tools=[scrape_website_tool, serper_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

team_assessor = Agent(
    role="Team Capability Assessor",
    goal="Assess team capabilities against project needs, researching only when skills are unclear",
    backstory="""Expert technical recruiter and team lead who evaluates team fit.
    You understand common technical skills and only research when:
    - Unfamiliar technologies are mentioned
    - New frameworks or tools need investigation
    - Industry-specific skills need clarification""",
    tools=[serper_tool],  # Only search tool, no scraping
    llm=llm,
    verbose=True,
    allow_delegation=False
)

research_synthesizer = Agent(
    role="Research Synthesizer",
    goal="Consolidate all findings into comprehensive foundation document",
    backstory="""Master synthesizer who creates clear, actionable project foundation
    documents. You work with whatever information is available - whether from detailed
    project descriptions or from web research - and create complete, well-organized plans.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# ================================ Tasks ================================

evaluate_research_needs_task = Task(
    description="""
    Analyze the project description and determine what research is actually needed.

    Project Name: {project_name}
    Project Description: {project_description}
    Industry: {industry}
    Team Members: {team_members}

    EVALUATE INFORMATION COMPLETENESS:

    1. **Project Description Analysis**:
       - Is the tech stack specified? (Frontend, Backend, Database, etc.)
       - Are features and requirements clearly listed?
       - Are non-functional requirements mentioned? (Performance, Security, etc.)
       - Is the scope well-defined?

    2. **Industry Information**:
       - Is the industry standard or well-known? (e.g., "E-commerce", "SaaS")
       - Does the description mention competitors or market positioning?
       - Are industry-specific challenges mentioned?

    3. **Technical Details**:
       - Are technologies and frameworks specified?
       - Is the architecture approach mentioned?
       - Are integrations/APIs listed?

    4. **Team Information**:
       - Are team members' skills clearly listed?
       - Are roles well-defined?
       - Are there obvious skill gaps?

    DECISION CRITERIA:

    **NO WEB RESEARCH NEEDED** if:
    - Project description is 200+ words with specific technical details
    - Tech stack is fully specified
    - Industry is standard/well-known
    - Team skills are clearly listed
    - Requirements are detailed with acceptance criteria

    **LIMITED RESEARCH NEEDED** if:
    - Industry is mentioned but competitors/trends not covered
    - Some technical details missing
    - Need to verify best practices for specified tech stack

    **FULL RESEARCH NEEDED** if:
    - Project description is vague or < 100 words
    - Industry is unclear or emerging/niche
    - No tech stack specified
    - Team skills don't match project needs clearly

    OUTPUT FORMAT (must be JSON):
    {{
        "research_recommendation": "none" | "limited" | "full",
        "reasoning": "Why this level of research is needed",
        "information_gaps": [
            "List specific gaps that need research"
        ],
        "research_topics": [
            "Specific topics to research (empty if none needed)"
        ],
        "estimated_completeness": "Percentage of info already available (e.g., '80%')"
    }}

    CRITICAL: Be conservative - if 70%+ of information is available, recommend "none" or "limited" research.
    """,
    agent=research_coordinator,
    expected_output="JSON object with research_recommendation, reasoning, information_gaps, research_topics, and estimated_completeness"
)

conditional_industry_research_task = Task(
    description="""
    Based on the research coordinator's recommendation, conduct targeted industry research.

    Research Recommendation: {{output from evaluate_research_needs_task}}
    Industry: {industry}
    Project Description: {project_description}

    INSTRUCTIONS:

    1. **If research_recommendation is "none"**:
       - DO NOT use any search tools
       - Output: "No industry research needed. Project description is sufficiently detailed."

    2. **If research_recommendation is "limited"**:
       - Use search tools ONLY for the specific topics listed in research_topics
       - Keep research focused and brief (2-3 searches maximum)
       - Focus on recent trends (last 6 months) and top 3 competitors

    3. **If research_recommendation is "full"**:
       - Conduct comprehensive research as originally specified
       - Cover market size, trends, competitors, challenges, best practices

    OUTPUT FORMAT:

    For "none":
    "RESEARCH SKIPPED: Project description is detailed (X% complete). No additional industry research required."

    For "limited":
    "LIMITED RESEARCH CONDUCTED:
    - Topic 1: [findings]
    - Topic 2: [findings]
    Based on [X] focused searches."

    For "full":
    "COMPREHENSIVE RESEARCH:
    [Full industry analysis as before]"

    IMPORTANT: Only use web search when research_recommendation is NOT "none".
    """,
    agent=industry_researcher,
    expected_output="Industry research findings or statement that research was skipped",
    context=[evaluate_research_needs_task]
)

conditional_project_analysis_task = Task(
    description="""
    Analyze project scope, using web research only if critical gaps exist.

    Research Recommendation: {{output from evaluate_research_needs_task}}
    Project Description: {project_description}
    Project Timeline: {project_timeline}
    Industry Research: {{output from conditional_industry_research_task}}

    WORK WITH WHAT'S PROVIDED:

    1. **Extract from Project Description**:
       - List all mentioned features and requirements
       - Identify specified technologies
       - Note any architecture details provided
       - Document stated constraints or requirements

    2. **Use Web Search ONLY If**:
       - Research recommendation includes specific technical topics
       - Need to verify best practices for unfamiliar tech stack
       - Critical technical information is missing

    3. **Analysis Requirements**:
       - Deliverables breakdown (from description)
       - Technical architecture (specified or recommended)
       - Risk assessment (based on provided info + limited research if needed)
       - Dependencies (from requirements)
       - Resource requirements (estimated from scope)

    OUTPUT FORMAT:

    Start with: "PROJECT ANALYSIS [Using: Project Description {{"+ Web Research" if searches used}}]"

    Then provide:
    - Key deliverables (10-30 items)
    - Technical architecture recommendations
    - Risk assessment (15-25 risks)
    - Dependencies
    - Resource requirements
    - Success criteria

    IMPORTANT: Most information should come from the project description.
    Only search if research_recommendation indicates critical gaps.
    """,
    agent=project_analyzer,
    expected_output="Comprehensive project analysis based primarily on project description, with targeted research only if needed",
    context=[evaluate_research_needs_task, conditional_industry_research_task]
)

team_assessment_task = Task(
    description="""
    Assess team capabilities, researching unfamiliar technologies only when necessary.

    Team Members: {team_members}
    Project Requirements: {{output from conditional_project_analysis_task}}
    Research Recommendation: {{output from evaluate_research_needs_task}}

    TEAM ANALYSIS:

    1. **Skills Inventory**:
       - List each member's skills and experience level
       - Match skills to project requirements
       - Identify coverage (who can do what)

    2. **Gap Analysis**:
       - Compare team skills to project needs
       - Identify missing capabilities
       - Prioritize gaps (Critical/Important/Nice-to-have)

    3. **Research ONLY If**:
       - Unfamiliar technology mentioned in project (e.g., "We need Elixir experts")
       - New framework that team hasn't used (check if training is feasible)
       - Industry-specific skills that need clarification

    4. **Recommendations**:
       - Task distribution based on skills
       - Training needs
       - Hiring recommendations (if any)
       - Team structure

    OUTPUT FORMAT:

    "TEAM ASSESSMENT [Using: Team Info {{"+ Tech Research" if searches used}}]"

    Then provide:
    - Individual skill analysis
    - Skills gap analysis with priorities
    - Capacity analysis
    - Recommendations

    DO NOT search for common technologies (React, Node.js, Python, etc.)
    ONLY research truly unfamiliar or cutting-edge technologies.
    """,
    agent=team_assessor,
    expected_output="Team capability assessment with skills gaps, capacity analysis, and recommendations",
    context=[evaluate_research_needs_task, conditional_project_analysis_task]
)

research_synthesis_task = Task(
    description="""
    Synthesize all findings into comprehensive project foundation document.

    Research Recommendation: {{output from evaluate_research_needs_task}}
    Industry Research: {{output from conditional_industry_research_task}}
    Project Analysis: {{output from conditional_project_analysis_task}}
    Team Assessment: {{output from team_assessment_task}}

    Create complete project foundation document with these sections:

    ## EXECUTIVE SUMMARY
    - Project overview
    - Information sources used (project description, limited research, or full research)
    - Key findings
    - Top recommendations
    - Go/No-Go assessment

    ## 1. INDUSTRY & MARKET ANALYSIS
    (Include whatever research was conducted - or state "Based on project description")

    ## 2. PROJECT SCOPE & ARCHITECTURE
    (Comprehensive scope from project description + any research)

    ## 3. COMPREHENSIVE RISK ANALYSIS
    (15-25 risks prioritized by likelihood/impact)

    ## 4. DEPENDENCIES & CRITICAL PATH
    (All identified dependencies)

    ## 5. TEAM ASSESSMENT & RECOMMENDATIONS
    (Complete team analysis)

    ## 6. RESOURCE REQUIREMENTS
    (Development, infrastructure, tools)

    ## 7. PROJECT READINESS ASSESSMENT
    (Clear requirements? Capable team? Realistic timeline?)

    ## 8. RECOMMENDATIONS & NEXT STEPS
    (Top 10 recommendations, Phase 1 priorities, first week checklist)

    IMPORTANT:
    - Note in Executive Summary what level of research was conducted
    - If minimal research used, emphasize that analysis is based on detailed project description
    - Make document just as comprehensive regardless of research level
    - Synthesize ALL available information effectively

    OUTPUT: Complete 2000-4000 word foundation document
    """,
    agent=research_synthesizer,
    expected_output="Complete project foundation document with all 8 sections, noting research level used",
    context=[
        evaluate_research_needs_task,
        conditional_industry_research_task,
        conditional_project_analysis_task,
        team_assessment_task
    ]
)

# ================================ Crew ================================
research_crew= Crew(
    agents=[
        research_coordinator,
        industry_researcher,
        project_analyzer,
        team_assessor,
        research_synthesizer
    ],
    tasks=[
        evaluate_research_needs_task,
        conditional_industry_research_task,
        conditional_project_analysis_task,
        team_assessment_task,
        research_synthesis_task
    ],
    verbose=True,
    memory=False,
    cache=False
)
