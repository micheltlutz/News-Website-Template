---
description: Manage Jira issues via Atlassian MCP using JQL (no Rovo Search). Search, create, update, transition status, and handle sprint tasks. Auto-detects workspace configuration. Use when user says "create a Jira ticket", "list my tasks", "check Jira status", "transition this issue", "search Jira with JQL", or "move ticket to done". Do NOT use for Confluence pages (use confluence-assistant).
name: jira-assistant-jql
---

# Jira Assistant (JQL)

You are an expert in using Atlassian MCP tools to interact with Jira.

**This variant uses JQL exclusively for searching issues.** Do NOT use the `search` tool (Rovo Search) — it returns 403 on instances without Rovo installed.

## When to Use

Use this skill when the user asks to:

- Search for Jira issues or tasks
- List issues by status, assignee, sprint, or priority
- Create new Jira issues (Tarefa, História, Epic, Subtask, Função, Bug)
- Update existing issues
- Transition issue status (BACKLOG → A fazer → Fazendo → Em análise → Feito)
- Add comments to issues
- Manage assignees
- Query issues with specific criteria

## Configuration

**Before any Jira operation, always read** `.cursor/rules/jira-config.mdc` (section `# JIRA Project Configuration`). Use `PROJECT_KEY`, `CLOUD_ID`, `BASE_URL`, `BROWSE_URL_TEMPLATE`, issue types and board workflow from that file.

**Project Detection Strategy (Automatic):**

1. **Check workspace rules first**: Read `.cursor/rules/jira-config.mdc` (`# JIRA Project Configuration`)
2. **If not found**: Use `getAccessibleAtlassianResources` and `getVisibleJiraProjects` via MCP
3. **If still unclear**: Ask user to specify project key
4. **Use detected values** for all Jira operations in this conversation

### Configuration Detection Workflow

When you activate this skill:

1. **Always** open `.cursor/rules/jira-config.mdc` and extract values under `# JIRA Project Configuration`
2. If found, use: Project Key, Cloud ID, URL, Board URL, issue type names (PT-BR), board status names
3. If not found:
   - Call `getAccessibleAtlassianResources()` to obtain `cloudId`
   - Call `getVisibleJiraProjects(cloudId="{CLOUD_ID}")` to list available projects
   - Present discovered projects to user
   - Ask: "Which Jira project should I use? (e.g., SEEBLE, KAN, PROJ)"
4. Store the configuration for this conversation and proceed with operations

**Note for skill users:** To configure this skill for your workspace, create `.cursor/rules/jira-config.mdc` with your project details. See `README.md` in this skill folder.

### Board workflow (SEEBLE)

Columns on the SEEBLE board (left → right):

| Order | Status (literal name) | statusCategory (JQL) | Use |
|-------|----------------------|----------------------|-----|
| 1 | `BACKLOG` | `"To Do"` | Backlog |
| 2 | `A fazer` | `"To Do"` | Ready to start |
| 3 | `Fazendo` | `"In Progress"` | In progress |
| 4 | `Em análise` | `"In Progress"` | Review / analysis |
| 5 | `Feito` | `Done` | Done |

- Prefer **`statusCategory`** for broad filters.
- Use **`status = "Fazendo"`** (etc.) when the exact column matters.
- `statusCategory = "To Do"` covers **BACKLOG** + **A fazer**.
- `statusCategory = "In Progress"` covers **Fazendo** + **Em análise**.

## Workflow

### 1. Finding Issues (Always Start Here)

**Always use `searchJiraIssuesUsingJql`** — never use `search` (Rovo Search).

```
searchJiraIssuesUsingJql(
  cloudId="{CLOUD_ID}",
  jql="project = {PROJECT_KEY} AND assignee = currentUser() AND statusCategory = \"To Do\"",
  maxResults=50
)
```

**⚠️ ALWAYS include `project = {PROJECT_KEY}` in JQL queries**

#### Natural language → JQL mapping

Translate user requests into JQL before calling the tool:

| User says | JQL |
|-----------|-----|
| backlog | `project = {PROJECT_KEY} AND status = "BACKLOG"` |
| a fazer / to-do | `project = {PROJECT_KEY} AND status = "A fazer"` or `statusCategory = "To Do"` |
| fazendo / em andamento | `project = {PROJECT_KEY} AND status = "Fazendo"` or `statusCategory = "In Progress"` |
| em análise / review | `project = {PROJECT_KEY} AND status = "Em análise"` |
| feito / done | `project = {PROJECT_KEY} AND status = "Feito"` or `statusCategory = Done` |
| "my to-do tasks" | `project = {PROJECT_KEY} AND assignee = currentUser() AND statusCategory = "To Do"` |
| "my in-progress tasks" | `project = {PROJECT_KEY} AND assignee = currentUser() AND statusCategory = "In Progress"` |
| "my done tasks" | `project = {PROJECT_KEY} AND assignee = currentUser() AND statusCategory = Done` |
| "all open bugs" | `project = {PROJECT_KEY} AND type = Bug AND statusCategory != Done` |
| "high priority tasks" | `project = {PROJECT_KEY} AND priority = High AND statusCategory != Done` |
| "recent issues" | `project = {PROJECT_KEY} AND created >= -7d ORDER BY created DESC` |
| "unassigned tasks" | `project = {PROJECT_KEY} AND assignee is EMPTY AND statusCategory = "To Do"` |

#### Status names vs statusCategory

Prefer **`statusCategory`** for broad filters; use literal **board column names** when the user names a column:

```jql
# ✅ Preferred — broad, locale-independent categories
statusCategory = "To Do"
statusCategory = "In Progress"
statusCategory = Done

# ✅ Exact column on SEEBLE board
status = "BACKLOG"
status = "A fazer"
status = "Fazendo"
status = "Em análise"
status = "Feito"
```

### 2. Searching with Specific Criteria

**Use `searchJiraIssuesUsingJql`** for all queries:

Examples (replace `{PROJECT_KEY}` with detected project key):

```jql
project = {PROJECT_KEY} AND status = "Fazendo"
project = {PROJECT_KEY} AND statusCategory = "In Progress"
project = {PROJECT_KEY} AND assignee = currentUser() AND created >= -7d
project = {PROJECT_KEY} AND type = "Epic" AND statusCategory != Done
project = {PROJECT_KEY} AND priority = High
project = {PROJECT_KEY} AND assignee = currentUser() AND status = "A fazer" ORDER BY priority DESC, updated DESC
```

Optional parameters:

- `maxResults`: 50–100 (default when omitted)
- `fields`: `["summary", "status", "priority", "assignee", "labels"]` for lighter responses
- `responseContentFormat`: `"markdown"` for readable descriptions

### 3. Getting Issue Details

Depending on what you have:

- **If you have issue key/id**: `getJiraIssue(cloudId, issueIdOrKey)`
- **If you have ARI**: `fetch(ari)` (only when an ARI is already known from a prior result)

### 4. Creating Issues

**ALWAYS use the detected `projectKey` and `cloudId` from configuration**

#### Step-by-step process:

```
a. View issue types:
   getJiraProjectIssueTypesMetadata(
     cloudId="{CLOUD_ID}",
     projectKey="{PROJECT_KEY}"
   )

b. View required fields:
   getJiraIssueTypeMetaWithFields(
     cloudId="{CLOUD_ID}",
     projectKey="{PROJECT_KEY}",
     issueTypeId="from-step-a"
   )

c. Create the issue:
   createJiraIssue(
     cloudId="{CLOUD_ID}",
     projectKey="{PROJECT_KEY}",
     issueTypeName="Tarefa",
     summary="Brief task description",
     description="## Context\n..."
   )
```

**Note:** Replace `{PROJECT_KEY}` and `{CLOUD_ID}` with values from detected configuration.

**Available issue types (literal names from jira-config.mdc):**

| Conceito | `issueTypeName` | Notes |
|----------|-----------------|-------|
| Task | `Tarefa` | default for ad-hoc work |
| Story | `História` | link parent via `parent: "{PROJECT_KEY}-XX"` |
| Epic | `Epic` | hierarchyLevel 1 |
| Sub-task | `Subtask` | requires `parent` with parent issue key |
| Feature | `Função` | feature / functionality |
| Bug | `Bug` | bugs |

### 5. Updating and Transitioning Issues

#### Edit fields:

```
editJiraIssue(cloudId, issueKey, fields)
```

#### Change status:

Always resolve transition IDs dynamically — do not hardcode them.

```
1. Get available transitions:
   getTransitionsForJiraIssue(cloudId, issueKey)

2. Pick the transition whose name/target matches the board column
   (e.g. "Fazendo", "Em análise", "Feito")

3. Apply transition:
   transitionJiraIssue(cloudId, issueKey, transitionId)
```

Examples of user intent → target status:

| User says | Target status |
|-----------|---------------|
| "mover para Fazendo" / "start working" | `Fazendo` |
| "mover para Em análise" / "send to review" | `Em análise` |
| "mover para Feito" / "mark done" | `Feito` |
| "voltar para A fazer" | `A fazer` |
| "colocar no BACKLOG" | `BACKLOG` |

#### Add comment:

```
addCommentToJiraIssue(cloudId, issueKey, comment)
```

## Default Task Template

**ALWAYS use this template** in the `description` field when creating issues:

```markdown
## Context

[Brief explanation of the problem or need]

## Objective

[What needs to be accomplished]

## Technical Requirements

[This is high level, it doesn't mention which class or file, but the technical high level objective]

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Acceptance Criteria

- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3

## Technical Notes

[Don't include file paths as they can change overtime]
[Technical considerations, dependencies, relevant links]

## Estimate

[Time estimate or story points, if applicable]
```

## Best Practices

### ✅ DO

- **Always read** `.cursor/rules/jira-config.mdc` (`# JIRA Project Configuration`) first
- **Always use the detected project key** in all operations
- **Always use Markdown** in the `description` field
- **Always use JQL** via `searchJiraIssuesUsingJql` for searching issues
- **Prefer `statusCategory`** for broad filters; use board column names (`Fazendo`, `Feito`, …) when exact
- **Translate natural language** into JQL before querying (see mapping table above)
- **Follow the task template** for consistency
- **Avoid file paths** in descriptions (they change over time)
- **Keep summaries brief** and descriptions detailed
- **Format search results** as a table with key, summary, status, priority, and browse URL

### ❌ DON'T

- **Do NOT use `search` (Rovo Search)** — it fails with 403 when Rovo is not installed on the instance
- **Do NOT invent status names** like `"To Do"` as literal `status` — on SEEBLE use `BACKLOG`, `A fazer`, `Fazendo`, `Em análise`, `Feito` (exact casing)
- **Do NOT invent issue type names** — use the literal names from `jira-config.mdc` (`Tarefa`, `História`, `Epic`, `Subtask`, `Função`, `Bug`)

### ⚠️ IMPORTANT

- **Issue ID** is numeric (internal)
- **Issue Key** is "{PROJECT_KEY}-123" format (user-facing)
- **To create subtasks**: Use the `parent` field with parent issue key
- **CloudId** can be URL or UUID - both work
- **Use detected configuration values** from workspace rules or user input
- **getJiraIssue** parameter is `issueIdOrKey`, not `issueKey`

## Examples

### Example 1: List my to-do tasks

```
User: "Liste minhas tarefas em A fazer"

searchJiraIssuesUsingJql(
  cloudId="{CLOUD_ID}",
  jql="project = {PROJECT_KEY} AND assignee = currentUser() AND status = \"A fazer\" ORDER BY priority DESC, updated DESC",
  maxResults=50
)
```

Present results as:

| Chave | Título | Prioridade | Status |
|-------|--------|------------|--------|
| {PROJECT_KEY}-1 | Summary here | High | A fazer |

### Example 2: Create a Task

```
User: "Create a task to implement user authentication"

createJiraIssue(
  cloudId="{CLOUD_ID}",
  projectKey="{PROJECT_KEY}",
  issueTypeName="Tarefa",
  summary="Implement user authentication endpoint",
  description="## Context
We need to secure our API endpoints with user authentication.

## Objective
Implement JWT-based authentication for API access.

## Technical Requirements
- [ ] Create authentication middleware
- [ ] Implement JWT token generation
- [ ] Add token validation
- [ ] Secure existing endpoints

## Acceptance Criteria
- [ ] Users can login with credentials
- [ ] JWT tokens are generated on successful login
- [ ] Protected endpoints validate tokens
- [ ] Invalid tokens return 401

## Technical Notes
Use bcrypt for password hashing, JWT for tokens, and implement refresh token logic.

## Estimate
5 story points"
)
```

### Example 3: Search and Update Issue

```
User: "Find my in-progress tasks and update the first one"

1. searchJiraIssuesUsingJql(
     cloudId="{CLOUD_ID}",
     jql="project = {PROJECT_KEY} AND assignee = currentUser() AND statusCategory = \"In Progress\""
   )

2. editJiraIssue(
     cloudId="{CLOUD_ID}",
     issueKey="{PROJECT_KEY}-123",
     fields={ "description": "## Context\nUpdated context..." }
   )
```

### Example 4: Transition Issue Status

```
User: "Mover {PROJECT_KEY}-456 para Feito"

1. getTransitionsForJiraIssue(cloudId="{CLOUD_ID}", issueKey="{PROJECT_KEY}-456")

2. Find transition targeting Feito (or named accordingly)

3. transitionJiraIssue(
     cloudId="{CLOUD_ID}",
     issueKey="{PROJECT_KEY}-456",
     transitionId="transition-id-for-feito"
   )
```

Other transition examples:

```
User: "Mover {PROJECT_KEY}-456 para Fazendo"
User: "Mover {PROJECT_KEY}-456 para Em análise"
```

Same flow: `getTransitionsForJiraIssue` → match target column → `transitionJiraIssue`.

### Example 5: Create Subtask

```
User: "Create a subtask for {PROJECT_KEY}-789"

createJiraIssue(
  cloudId="{CLOUD_ID}",
  projectKey="{PROJECT_KEY}",
  issueTypeName="Subtask",
  parent="{PROJECT_KEY}-789",
  summary="Implement validation logic",
  description="## Context\nSubtask for implementing input validation..."
)
```

## Common JQL Patterns

All queries **MUST** include `project = {PROJECT_KEY}` (use detected project key):

```jql
# By board column (SEEBLE)
project = {PROJECT_KEY} AND status = "BACKLOG"
project = {PROJECT_KEY} AND status = "A fazer"
project = {PROJECT_KEY} AND status = "Fazendo"
project = {PROJECT_KEY} AND status = "Em análise"
project = {PROJECT_KEY} AND status = "Feito"

# Broad categories
project = {PROJECT_KEY} AND assignee = currentUser() AND statusCategory = "To Do"
project = {PROJECT_KEY} AND assignee = currentUser() AND statusCategory = "In Progress"
project = {PROJECT_KEY} AND statusCategory = Done

# Recent issues
project = {PROJECT_KEY} AND created >= -7d ORDER BY created DESC

# High priority bugs
project = {PROJECT_KEY} AND type = Bug AND priority = High

# Epics without completion
project = {PROJECT_KEY} AND type = "Epic" AND statusCategory != Done

# Unassigned in backlog / to-do columns
project = {PROJECT_KEY} AND assignee is EMPTY AND statusCategory = "To Do"

# Issues updated this week
project = {PROJECT_KEY} AND updated >= startOfWeek() ORDER BY updated DESC

# All open issues (any status except Done / Feito)
project = {PROJECT_KEY} AND statusCategory != Done ORDER BY priority DESC
```

**Note:** Replace `{PROJECT_KEY}` with the actual project key from detected configuration.

## Important Notes

- **Project key is mandatory** — Always include `project = {PROJECT_KEY}` in JQL queries
- **Use detected configuration** — Read from `.cursor/rules/jira-config.mdc` (`# JIRA Project Configuration`) or ask user
- **Use Markdown** in descriptions — Not HTML or plain text
- **Follow the template** — Maintains consistency across issues
- **JQL only for search** — Never fall back to `search` (Rovo Search)
- **Prefer statusCategory** for broad filters; use SEEBLE column names when exact
- **Avoid file paths** — They change and become outdated
- **Keep technical notes high-level** — Focus on approach, not implementation details
- **Story points are optional** — Include estimates when relevant
