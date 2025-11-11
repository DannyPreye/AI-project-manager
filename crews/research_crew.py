from crewai import Crew, Agent, Task, LLM
from dotenv import load_dotenv
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
import os

load_dotenv()

llm = LLM(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

scrape_website_tool = ScrapeWebsiteTool()
serper_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# ================================ Agents ================================
industry_researcher = Agent(
    role="Industry Research Specialist",
    goal="Conduct comprehensive industry analysis with actionable insights and data-driven recommendations",
    backstory="""You are a senior market research analyst with 12+ years of experience in technology
            and business intelligence. You don't just gather surface-level information - you dive deep into
            market dynamics, competitive positioning, emerging trends, and industry-specific challenges.
            You always back your findings with concrete examples, statistics, and real-world case studies.
            You identify both opportunities and threats with equal rigor.""",
    tools=[
        scrape_website_tool,
        serper_tool,
    ],
    llm=llm,
    verbose=True,
)

project_analyzer = Agent(
    role="Project Scope Analyst",
    goal="Perform exhaustive project analysis identifying every deliverable, risk, dependency, and constraint",
    backstory="""Senior technical project analyst with 15+ years managing complex software projects across
    multiple industries. You have a gift for breaking down ambiguous requirements into crystal-clear
    specifications. You anticipate problems before they happen and identify hidden dependencies that others
    miss. You think in terms of technical architecture, data flows, integration points, and potential
    bottlenecks. You NEVER leave requirements vague - everything must be specific and measurable.""",
    llm=llm,
    verbose=True,
)

team_assessor = Agent(
    role="Team Capability Assessor",
    goal="Conduct thorough skills assessment and create optimal team composition recommendations",
    backstory="""Expert technical recruiter and team lead with 10+ years building high-performing
    engineering teams. You understand not just what skills are listed, but how those skills translate
    to actual project capabilities. You assess skill levels (junior/mid/senior), identify knowledge
    gaps, recommend training needs, and flag potential team dynamics issues. You consider workload
    capacity, collaboration needs, and skill overlap when making recommendations.""",
    llm=llm,
    verbose=True,
)

project_research_summarize = Agent(
    role="Project Research Synthesizer",
    goal="Create a comprehensive, structured research report that serves as the definitive project foundation",
    backstory="""Master synthesizer who takes complex research from multiple sources and creates clear,
    actionable intelligence reports. You have worked with Fortune 500 companies helping them launch major
    initiatives. Your reports are known for being thorough yet readable, with clear sections, specific
    findings, and actionable recommendations. You NEVER summarize by omitting important details - you
    synthesize by organizing information logically and highlighting key insights.""",
    llm=llm,
    verbose=True,
)

# ================================ Tasks ================================
industry_research_task = Task(
    description="""
                Conduct comprehensive industry research for: {project_name}
                Industry: {industry}

                Your research MUST cover the following in depth:

                1. **Market Overview & Size**:
                   - Current market size and growth rate (with numbers/percentages)
                   - Key market segments and their characteristics
                   - Geographic distribution and opportunities
                   - Market maturity stage and trajectory

                2. **Industry Trends** (identify at least 5-7 current trends):
                   - Emerging technologies being adopted
                   - Changing customer behaviors and expectations
                   - Regulatory or compliance changes
                   - Innovation patterns and disruption threats
                   - Provide specific examples and timeframes

                3. **Competitive Landscape**:
                   - Identify 5-10 major competitors (with company names)
                   - Their market positioning and unique value propositions
                   - Their strengths and weaknesses
                   - Market share estimates where available
                   - Recent product launches or strategic moves
                   - Pricing strategies and business models

                4. **Common Challenges & Pitfalls**:
                   - Technical challenges specific to this industry
                   - Common reasons projects fail in this space
                   - Scalability and performance concerns
                   - Security and compliance requirements
                   - Integration challenges with existing systems
                   - Provide real examples of failures and their causes

                5. **Best Practices & Success Factors**:
                   - Proven approaches that lead to success
                   - Technology stacks commonly used
                   - Architecture patterns that work well
                   - User experience expectations in this industry
                   - Development methodologies that fit best
                   - Case studies of successful implementations

                6. **Opportunities & Threats**:
                   - Market gaps or underserved niches
                   - Emerging opportunities from new technologies
                   - Potential threats from competitors or market shifts
                   - Risk factors to monitor

                Use web search to find recent articles, reports, and real-world examples.
                Back every claim with sources or examples. Be specific with numbers, dates, and names.
                """,
    agent=industry_researcher,
    expected_output="""Detailed industry research report (1500-2500 words) with:
                - Market overview with statistics
                - 5-7 specific trends with examples
                - Competitive analysis of 5-10 players
                - List of common challenges with real examples
                - Best practices with case studies
                - SWOT-style opportunities and threats analysis
                All findings should be specific, recent (within last 2 years), and actionable.""",
)

project_analysis_task = Task(
    description="""
                Perform exhaustive project scope analysis for:
                Name: {project_name}
                Description: {project_description}
                Timeline: {project_timeline}

                Your analysis MUST be extremely detailed and specific:

                1. **Key Deliverables Breakdown** (identify 10-30 deliverables):
                   - List EVERY major feature and component
                   - For each deliverable specify:
                     * What exactly needs to be built
                     * Technical specifications
                     * User-facing vs backend components
                     * Integration requirements
                     * Quality and performance criteria
                   - Organize by priority (Must-have / Should-have / Nice-to-have)
                   - Include deliverables for: MVP, documentation, testing, deployment

                2. **Technical Architecture Requirements**:
                   - System architecture patterns needed (microservices, monolith, serverless, etc.)
                   - Technology stack recommendations (languages, frameworks, databases)
                   - Infrastructure requirements (servers, cloud services, CDN, etc.)
                   - Third-party services/APIs needed
                   - Data storage and database design considerations
                   - API design approach (REST, GraphQL, gRPC)
                   - Authentication and authorization approach
                   - Frontend architecture (SPA, SSR, mobile apps)

                3. **Comprehensive Risk Assessment** (identify 15-25 risks):
                   - Technical risks (scalability, performance, security, tech debt)
                   - Resource risks (team skills, availability, budget)
                   - Schedule risks (timeline, dependencies, unknowns)
                   - Business risks (market changes, competition, requirements changes)
                   - Integration risks (third-party APIs, legacy systems)
                   - For EACH risk provide:
                     * Likelihood (High/Medium/Low)
                     * Impact (High/Medium/Low)
                     * Specific mitigation strategy
                     * Contingency plan

                4. **Dependencies Analysis**:
                   - Component dependencies (what must be built first)
                   - Data dependencies (data flows between systems)
                   - External dependencies (third-party services, APIs)
                   - Team dependencies (who needs to work with whom)
                   - Infrastructure dependencies (deployment order)
                   - Create a dependency map/hierarchy

                5. **Critical Path Identification**:
                   - Identify the critical path through the project
                   - List items that cannot be parallelized
                   - Highlight bottleneck tasks or resources
                   - Estimate impact of delays on critical path items

                6. **Resource Requirements** (be specific):
                   - Development resources (hours/weeks per role)
                   - Infrastructure costs (hosting, services, tools)
                   - Software licenses and subscriptions needed
                   - External services or consultants required
                   - Testing environments and tools
                   - Monitoring and analytics tools

                7. **Non-Functional Requirements**:
                   - Performance targets (response times, throughput)
                   - Scalability requirements (expected users, growth)
                   - Security requirements (compliance, data protection)
                   - Availability and uptime targets
                   - Browser/device compatibility
                   - Accessibility requirements

                8. **Success Criteria & KPIs**:
                   - Define measurable success metrics
                   - Technical KPIs (performance, uptime, bug rate)
                   - Business KPIs (user adoption, conversion, engagement)
                   - Quality metrics (test coverage, code quality)

                Based on industry research context, incorporate industry-specific best practices and challenges.
                """,
    agent=project_analyzer,
    expected_output="""Comprehensive project analysis document (2000-3000 words) containing:
                - 10-30 specific deliverables with technical specs
                - Complete technology stack and architecture recommendations
                - 15-25 risks with likelihood, impact, and mitigation strategies
                - Detailed dependency map with clear relationships
                - Critical path analysis
                - Specific resource requirements with estimates
                - Non-functional requirements with measurable targets
                - Success criteria and KPIs
                Must be actionable and specific enough to start project planning immediately.""",
    context=[industry_research_task],
)

team_assessment_task = Task(
    description="""
                Conduct comprehensive team capability assessment for:
                Team members: {team_members}

                For EACH team member, provide detailed analysis:

                1. **Individual Skill Assessment**:
                   - List all skills mentioned and categorize them:
                     * Programming languages and frameworks
                     * Frontend technologies
                     * Backend technologies
                     * Database expertise
                     * DevOps and infrastructure
                     * Design and UX skills
                     * Soft skills (PM, writing, communication)
                   - Estimate skill level based on role (Junior/Mid/Senior)
                   - Identify their primary strengths (top 3-5 skills)
                   - Note any specialized or unique capabilities

                2. **Project Role Suitability**:
                   - Based on project requirements, suggest their best role(s)
                   - What parts of the project are they best suited for?
                   - Can they be a lead/owner for certain components?
                   - Backup roles they could handle if needed

                3. **Skills Gap Analysis**:
                   - Compare team skills against ALL project requirements
                   - Identify missing or weak skills for:
                     * Critical project technologies
                     * Architecture patterns needed
                     * Specific tools or frameworks
                     * Domain knowledge requirements
                   - Prioritize gaps (Critical / Important / Nice-to-have)
                   - Suggest solutions for each gap:
                     * Training/upskilling existing team members
                     * Hiring recommendations (specific roles/skills)
                     * External contractors or consultants
                     * Alternative technical approaches

                4. **Team Composition Analysis**:
                   - Overall team balance (frontend vs backend vs full-stack)
                   - Skill overlap and redundancy (good for resilience)
                   - Single points of failure (only one person knows X)
                   - Team size adequacy for project scope
                   - Collaboration and communication structure

                5. **Capacity and Workload Estimation**:
                   - Estimate realistic capacity per team member
                   - Consider: meetings, code reviews, planning, unknowns
                   - Typical productive hours per day (usually 5-6 hours)
                   - Any mentioned constraints or availability issues
                   - Calculate total team capacity vs project needs

                6. **Recommended Task Distribution Strategy**:
                   - Suggest which team members should work on which areas
                   - Identify natural pairings for collaboration
                   - Recommend mentor/mentee relationships for upskilling
                   - Flag any workload imbalance concerns
                   - Suggest team lead or technical leads

                7. **Risk Assessment**:
                   - Team-related risks (skills, capacity, turnover)
                   - Dependencies on specific individuals
                   - Learning curve for new technologies
                   - Communication or coordination challenges
                   - Mitigation strategies for team risks

                8. **Recommendations**:
                   - Should any new roles be hired? (specific skills)
                   - What training should be prioritized?
                   - How should the team be organized?
                   - Any process or tooling recommendations?

                Be specific and actionable. Use the project analysis context to understand exact requirements.
                """,
    agent=team_assessor,
    expected_output="""Comprehensive team assessment report (1500-2500 words) containing:
                - Individual analysis for each team member with skills categorized
                - Detailed skills gap analysis with prioritized list of gaps
                - Specific hiring recommendations if needed (roles and skills)
                - Training recommendations with priorities
                - Optimal team structure and task distribution strategy
                - Team capacity analysis (total hours available vs needed)
                - Risk assessment for team-related issues
                - Actionable recommendations for team optimization
                Include a summary matrix showing: [Team Member | Primary Skills | Best Suited For | Skill Level]""",
    context=[project_analysis_task, industry_research_task],
)

project_research_summary_task = Task(
    description="""
    Synthesize ALL research findings into a comprehensive, well-structured project foundation document.

    This document will be THE definitive reference for project planning, so it must be complete and detailed.

    Structure your report with these sections (do NOT omit any details):

    ## EXECUTIVE SUMMARY
    - Project overview in 2-3 paragraphs
    - Key findings and critical insights
    - Top 5-7 recommendations
    - Major risks and mitigation approaches
    - Go/No-Go assessment with justification

    ## 1. INDUSTRY & MARKET ANALYSIS
    Synthesize all industry research findings:
    - Market size, trends, and opportunities
    - Competitive landscape summary (key players and their positioning)
    - Industry-specific challenges this project will face
    - Best practices from successful similar projects
    - Technology trends relevant to this project
    - Strategic recommendations based on market analysis

    ## 2. PROJECT SCOPE & ARCHITECTURE
    Consolidate all project analysis findings:
    - Complete list of deliverables (organized by priority)
    - Recommended technical architecture and stack
    - System design considerations
    - Integration requirements
    - Non-functional requirements (performance, security, scalability)
    - Success criteria and KPIs
    - Scope boundaries (what's in, what's out)

    ## 3. COMPREHENSIVE RISK ANALYSIS
    Combine all identified risks into prioritized list:
    - Group risks by category (Technical, Resource, Schedule, Business)
    - For each HIGH-priority risk include:
      * Description and potential impact
      * Likelihood and severity
      * Mitigation strategy
      * Contingency plan
      * Risk owner/responsibility
    - Overall project risk level assessment

    ## 4. DEPENDENCIES & CRITICAL PATH
    Map out all critical dependencies:
    - Technical dependencies (component ordering)
    - Resource dependencies (team coordination needs)
    - External dependencies (third-party services, APIs)
    - Preliminary critical path identification
    - Potential bottlenecks and constraints

    ## 5. TEAM ASSESSMENT & RECOMMENDATIONS
    Synthesize team analysis findings:
    - Team composition summary with skill breakdown
    - Individual team member strengths and best-fit roles
    - Skills gap analysis (what's missing)
    - Hiring recommendations (if any, with specific roles)
    - Training needs (prioritized)
    - Recommended team structure and leadership
    - Team capacity vs project requirements
    - Team-related risks and mitigation

    ## 6. RESOURCE REQUIREMENTS
    Consolidate all resource needs:
    - Development resources (hours/weeks by role)
    - Infrastructure and hosting requirements
    - Tools, software licenses, and subscriptions
    - Third-party services and APIs
    - External consultants or contractors (if needed)
    - Budget implications (high-level)

    ## 7. PROJECT READINESS ASSESSMENT
    - Are requirements clear enough? (gaps to clarify)
    - Is the team capable? (with or without additions)
    - Is the timeline realistic? (preliminary assessment)
    - Are there any blocking issues?
    - What needs to be addressed before starting?

    ## 8. RECOMMENDATIONS & NEXT STEPS
    - Top 10 recommendations for project success
    - Suggested project approach and methodology
    - Phase 1 priorities
    - Quick wins and early deliverables
    - What to do in the first week
    - Key decisions that need to be made

    IMPORTANT INSTRUCTIONS:
    - Do NOT summarize by removing details - include all important findings
    - Keep specific numbers, dates, names, and examples from the research
    - Organize information logically but comprehensively
    - Use bullet points and clear structure for readability
    - This should be a 3000-5000 word document
    - Cross-reference between sections where findings relate
    - Highlight critical insights and must-know information
    """,
    agent=project_research_summarize,
    expected_output="""Complete project foundation document (3000-5000 words) with all 8 sections:
    1. Executive summary with go/no-go assessment
    2. Full industry analysis with market insights
    3. Complete project scope with 10-30 deliverables
    4. Comprehensive risk analysis (15-25 risks) with mitigation strategies
    5. Dependencies and critical path mapping
    6. Detailed team assessment with gaps and recommendations
    7. Complete resource requirements
    8. Project readiness assessment with top 10 recommendations

    This document must be detailed enough to immediately start detailed project planning and task breakdown.
    Include all specific findings, numbers, recommendations, and actionable insights from all research.""",
    context=[industry_research_task, project_analysis_task, team_assessment_task],
)

# ================================ Crew ================================
research_crew = Crew(
    agents=[
        industry_researcher,
        project_analyzer,
        team_assessor,
        project_research_summarize,
    ],
    tasks=[
        industry_research_task,
        project_analysis_task,
        team_assessment_task,
        project_research_summary_task,
    ],
    verbose=True,
)
