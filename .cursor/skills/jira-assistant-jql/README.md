# jira-assistant-jql — Setup e configuração

Skill do Cursor para operar o Jira via **Atlassian MCP** usando **somente JQL** (sem Rovo Search). A configuração do projeto fica em uma **Cursor Rule** compartilhada, não dentro da skill.

| Arquivo | Papel |
|---------|--------|
| [`.cursor/rules/jira-config.mdc`](../../rules/jira-config.mdc) | Fonte da verdade: `PROJECT_KEY`, `CLOUD_ID`, URLs, tipos de issue, workflow do board |
| [`SKILL.md`](./SKILL.md) | Como o agente busca, cria, atualiza e transiciona issues |
| Este `README.md` | Como configurar o mdc e garantir uso no **Cursor** e no **Claude** |

---

## 1. Configurar `.cursor/rules/jira-config.mdc`

Crie (ou edite) o arquivo no **raiz do workspace**:

```text
.cursor/rules/jira-config.mdc
```

### Frontmatter obrigatório

```yaml
---
alwaysApply: true
description: JIRA Project Configuration
---
```

- **`description: JIRA Project Configuration`** — o agente e a skill procuram esse título/descrição.
- **`alwaysApply: true`** — injeta a regra em toda conversa do Cursor Agent (recomendado para não depender só da skill).

### Corpo: seção `# JIRA Project Configuration`

O título em markdown **deve** ser exatamente:

```markdown
# JIRA Project Configuration
```

Preencha no mínimo:

| Campo | Exemplo | Onde usar |
|-------|---------|-----------|
| `PROJECT_KEY` | `"SEEBLE"` | JQL `project = SEEBLE`, chaves `SEEBLE-123` |
| `PROJECT_NAME` | `"SEEBLE"` | Exibição / confirmação |
| `CLOUD_ID` | `900e44cd-292f-4782-971c-1fe9ef793176` | Parâmetro `cloudId` das tools MCP |
| `BASE_URL` | `https://hubinsider.atlassian.net/` | Site Atlassian |
| `BROWSE_URL_TEMPLATE` | `https://hubinsider.atlassian.net/browse/{issue_id}` | Links nas respostas |
| `BOARD_URL` | `https://hubinsider.atlassian.net/jira/software/projects/SEEBLE/boards/2` | Referência do board |

Documente também:

1. **Issue types** — nomes **literais** no Jira (PT-BR se o projeto for next-gen em português), IDs se souber, e como criar (`issueTypeName`, `parent`).
2. **Workflow do board** — nomes **literais das colunas** + mapeamento para `statusCategory` (`"To Do"` / `"In Progress"` / `Done`).

Modelo mínimo (adapte ao seu projeto):

```markdown
---
alwaysApply: true
description: JIRA Project Configuration
---

# JIRA Project Configuration

This workspace uses the following Jira configuration:

- **PROJECT_KEY:** "SEEBLE"
- **PROJECT_NAME:** "SEEBLE"
- **CLOUD_ID:** 900e44cd-292f-4782-971c-1fe9ef793176
- **BASE_URL:** "https://hubinsider.atlassian.net/"
- **BROWSE_URL_TEMPLATE:** "https://hubinsider.atlassian.net/browse/{issue_id}"
- **BOARD_URL:** "https://hubinsider.atlassian.net/jira/software/projects/SEEBLE/boards/2"

> **Origem do `CLOUD_ID`:** ver seção abaixo (`/_edge/tenant_info`).

## Issue Types (nomes literais)

| Conceito | Nome no Jira | Uso |
|----------|--------------|-----|
| Task | **Tarefa** | `issueTypeName: "Tarefa"` |
| … | … | … |

## Workflow do board

| Ordem | Status no board | statusCategory |
|-------|-----------------|----------------|
| 1 | `BACKLOG` | `"To Do"` |
| 2 | `A fazer` | `"To Do"` |
| 3 | `Fazendo` | `"In Progress"` |
| 4 | `Em análise` | `"In Progress"` |
| 5 | `Feito` | `Done` |
```

Neste repositório o arquivo já está preenchido para o projeto **SEEBLE**.

---

## 2. Obter o `CLOUD_ID` via `tenant_info`

O `CLOUD_ID` é o UUID do tenant Atlassian Cloud. Sem ele as tools MCP não sabem em qual site operar.

### Passo a passo

1. Faça login no Jira no browser.
2. Abra (troque o domínio pelo do seu site):

   ```text
   https://seu-dominio.atlassian.net/_edge/tenant_info
   ```

   Exemplo deste projeto:

   ```text
   https://hubinsider.atlassian.net/_edge/tenant_info
   ```

3. A resposta é JSON. Localize o identificador do tenant — em geral o campo **`cloudId`** (UUID no formato `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
4. Cole o valor em **`CLOUD_ID`** no `jira-config.mdc` (com ou sem aspas; o importante é o UUID completo).

### Alternativa via MCP

Se a URL `tenant_info` não estiver acessível, com o MCP Atlassian autenticado:

1. Chame `getAccessibleAtlassianResources`.
2. Use o `cloudId` (ou `id`) retornado no recurso do site desejado.
3. Grave o mesmo valor em `CLOUD_ID` no mdc para as próximas sessões.

O mdc **não autentica** o MCP — só fornece IDs e URLs. Cursor e Claude ainda precisam do servidor MCP Atlassian conectado e autorizado.

---

## 3. Garantir uso no Cursor e no Claude

A skill e a regra trabalham juntas: a **regra** carrega os IDs; a **skill** define o comportamento (JQL, transitions, template).

### Cursor Agent

| Mecanismo | O que fazer |
|-----------|-------------|
| **Rule sempre ativa** | Em `jira-config.mdc`, use `alwaysApply: true` e `description: JIRA Project Configuration`. Assim o bloco `# JIRA Project Configuration` entra em toda conversa. |
| **Skill sob demanda** | Mantenha esta pasta em `.cursor/skills/jira-assistant-jql/`. O agente ativa a skill em pedidos de Jira e **deve** ler o mdc primeiro (ver `SKILL.md` → Configuration). |
| **Só skill, sem alwaysApply** | Funciona se o agente carregar a skill; é mais frágil. Prefira `alwaysApply: true` para config de projeto. |

### Claude Code

O Claude Code **não** injeta `.cursor/rules/*.mdc` automaticamente.

Para garantir o uso da configuração:

1. **Ponteiro em `CLAUDE.md`** (recomendado) — adicione algo como:

   ```markdown
   ## Jira

   Em operações Jira, ler `.cursor/rules/jira-config.mdc` (seção `# JIRA Project Configuration`)
   e seguir a skill `.cursor/skills/jira-assistant-jql/SKILL.md`.
   Não usar Rovo Search; apenas JQL via MCP Atlassian.
   ```

2. **Skill no Claude** (opcional) — copie ou faça symlink:

   ```bash
   mkdir -p .claude/skills
   ln -s ../../.cursor/skills/jira-assistant-jql .claude/skills/jira-assistant-jql
   ```

   Assim o Claude Code descobre a skill no caminho padrão `.claude/skills/`.

3. **MCP Atlassian** — configure o mesmo servidor MCP no Claude Code; sem ele a skill não executa tools.

### Resumo

```text
Cursor  → alwaysApply: true no mdc  +  skill em .cursor/skills/
Claude  → ponteiro em CLAUDE.md     +  (opcional) skill em .claude/skills/
Ambos   → MCP Atlassian autenticado +  CLOUD_ID correto no mdc
```

---

## 4. Checklist rápido

- [ ] Existe `.cursor/rules/jira-config.mdc` com `# JIRA Project Configuration`
- [ ] `alwaysApply: true` e `description: JIRA Project Configuration`
- [ ] `PROJECT_KEY`, `CLOUD_ID`, `BASE_URL`, `BROWSE_URL_TEMPLATE` preenchidos
- [ ] `CLOUD_ID` obtido de `https://seu-dominio.atlassian.net/_edge/tenant_info` (ou MCP)
- [ ] Workflow do board documentado (nomes literais + `statusCategory`)
- [ ] Issue types com nomes literais do Jira (PT-BR se aplicável)
- [ ] MCP Atlassian autenticado no Cursor (e no Claude, se usar)
- [ ] Skill presente em `.cursor/skills/jira-assistant-jql/`
- [ ] (Claude) Ponteiro em `CLAUDE.md` e/ou skill em `.claude/skills/`
- [ ] Teste JQL: `project = SEEBLE AND statusCategory != Done` (troque a key se for outro projeto)

---

## 5. Workflow SEEBLE (referência deste repo)

Colunas do board:

`BACKLOG` → `A fazer` → `Fazendo` → `Em análise` → `Feito`

Detalhes e exemplos JQL: [`.cursor/rules/jira-config.mdc`](../../rules/jira-config.mdc) e [`SKILL.md`](./SKILL.md).
