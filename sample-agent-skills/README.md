# Sample agent skills

Three portable skill packages for an existing agent: `data-retrieval`,
`calculator`, and `api-lookup`. All helpers use the Python 3 standard library.

Status: local examples and tests prepared. Remote Git publication, cluster fetch,
agentregistry import, and agent execution have not been verified. A repository URL,
installed versions, and access to the target environment are needed to finish those checks.

## 1. Check your installed versions first

Run on the machine that manages your cluster:

```sh
arctl version
arctl --help
helm list -A
kubectl api-resources --api-group=kagent.dev
```

Use the command family exposed by your installed CLI:

| Component | Integration |
| --- | --- |
| Older arctl, including v0.3.3 | `arctl skill publish`, `arctl skill list`, `arctl skill pull` |
| Current declarative arctl | `arctl apply`, `arctl get skills`, `arctl pull skill` |
| kagent 0.x Agent with Git skill support | `spec.skills.gitRefs` |
| kagent 1.x alpha AgentTemplate | `spec.skills[]` with an immutable source |

The adjacent `gvisor-kagent` PoC records that its kagent 0.9.9 Substrate
SandboxAgent path rejects skills. If that is your existing agent, stop at registry
validation until you choose a compatible runtime/version. Do not attach an Agent
snippet to a SandboxAgent or AgentTemplate without checking its installed schema.

## 2. Understand the repository and schema

```text
skills/
  calculator/
  data-retrieval/
  api-lookup/
    SKILL.md
    scripts/lookup.py
    references/input.schema.json
    assets/config.json
tests/test_skills.py
README.md
```

Each skill has its own `SKILL.md`, script, and input contract. Retrieval also
bundles fictional catalog data. API lookup bundles a timeout configuration.

The standard discovery format is YAML frontmatter followed by Markdown:

```markdown
---
name: calculator
description: Perform arithmetic when the user needs a numerical result.
compatibility: Requires Python 3 and script execution.
metadata:
  version: "1.0.0"
---

Instructions for invoking the bundled helper and interpreting its output.
```

`name` and `description` are required. Use a lowercase, hyphenated name matching
the directory, at most 64 characters, without leading/trailing or repeated hyphens.
Keep the description within 1024 characters and say when to use the skill.
`compatibility` and string-valued `metadata` are optional. `metadata.version`
documents this package; it does not automatically publish a registry version.

The Markdown body is the skill prompt. The JSON Schema files here document helper
arguments; they are a repository convention, not automatic MCP tool registration.
Installing a skill does not provision Python, an execution tool, or a remote API.
The existing agent must be able to run its bundled scripts. If it only supports
MCP tools, expose these operations through an MCP server and attach that server
separately using the configuration supported by your kagent version.

## 3. Test locally

From this repository root:

```sh
python3 -m unittest discover -s tests -v
python3 skills/calculator/scripts/calculate.py multiply 12.5 8
python3 skills/data-retrieval/scripts/retrieve.py P100
python3 skills/api-lookup/scripts/lookup.py kagent-dev kagent
```

Expected: `100.0`, a fictional notebook priced at USD 4.50, and public repository
metadata respectively. The unit test mocks the API; the last command is a separate
live network check. A successful mocked test does not prove cluster egress.

## 4. Publish this Git repository

Create an empty repository in your Git provider under the intended organization.
Choose visibility according to your team's requirements. This sample is already
initialized locally; if copying it without `.git`, first run `git init -b main`.

```sh
git add .
git commit -m "Add three sample agent skills and onboarding guide"
git remote add origin https://github.com/YOUR_ORG/sample-agent-skills.git
git push -u origin main
git rev-parse HEAD
```

Save the resulting full commit SHA as the skill revision. For older arctl's Git
publish path, use GitHub unless your exact version documents another supported
host; v0.3.3 has a documented GitLab limitation. Never put tokens in Git URLs.

## 5. Import each skill into agentregistry

### Older command family

Connect arctl to your existing registry using its configured endpoint/authentication.
Inspect `arctl skill publish --help` for the flags your release supports. Then:

```sh
SKILL_REPO_URL='https://github.com/YOUR_ORG/sample-agent-skills'
SKILL_REVISION='REPLACE_WITH_FULL_COMMIT_SHA'
for skill in calculator data-retrieval api-lookup; do
  arctl skill publish "./skills/$skill" \
    --git "$SKILL_REPO_URL/tree/$SKILL_REVISION/skills/$skill" \
    --version 1.0.0
done
arctl skill list
arctl skill pull calculator ./pulled/calculator --version 1.0.0
arctl skill pull data-retrieval ./pulled/data-retrieval --version 1.0.0
arctl skill pull api-lookup ./pulled/api-lookup --version 1.0.0
```

Use a commit SHA accepted by your release's Git URL parser; if your release only
accepts a branch or tag, record that it is mutable and verify pulled contents.

### Declarative command family

Generate `skill.yaml` using your installed release, outside the sample folders,
so its native schema is authoritative:

```sh
mkdir -p generated
cd generated
arctl init skill calculator
arctl init skill data-retrieval
arctl init skill api-lookup
cd ..
```

For each generated `skill.yaml`, retain its `apiVersion: ar.dev/v1alpha1`,
`kind: Skill`, and matching `metadata.name`; set the title and description.
Configure `spec.source.repository` to reference your Git repository, with its full
`commit` and `subfolder` (for example `skills/calculator`). Check the exact
repository URL field against your release's schema or generated examples; this
guide intentionally does not invent an unverified full manifest for an unknown version.
Register the real Git source, not the generated starter skill.

```sh
arctl apply -f generated/calculator/skill.yaml
arctl apply -f generated/data-retrieval/skill.yaml
arctl apply -f generated/api-lookup/skill.yaml
arctl get skills
arctl pull skill calculator ./pulled/calculator
arctl pull skill data-retrieval ./pulled/data-retrieval
arctl pull skill api-lookup ./pulled/api-lookup
```

Compare the downloaded `SKILL.md`, scripts, references, and assets with the source
revision. Listing a catalog entry alone is insufficient evidence that it can be fetched.

## 6. Attach skills to your existing agent

Registry import and runtime attachment are separate steps. Direct Git attachment
below loads the same source without relying on an automatic registry-to-agent sync.
Merge the appropriate fields into your existing manifest; preserve existing skills.

For a compatible **kagent 0.x Agent**, inspect first:

```sh
kubectl explain agent.spec.skills --api-version=kagent.dev/v1alpha2
```

Then add under `spec` (repeat the repository entry for each skill):

```yaml
skills:
  gitRefs:
    - url: https://github.com/YOUR_ORG/sample-agent-skills.git
      ref: REPLACE_WITH_FULL_COMMIT_SHA
      path: skills/calculator
    - url: https://github.com/YOUR_ORG/sample-agent-skills.git
      ref: REPLACE_WITH_FULL_COMMIT_SHA
      path: skills/data-retrieval
    - url: https://github.com/YOUR_ORG/sample-agent-skills.git
      ref: REPLACE_WITH_FULL_COMMIT_SHA
      path: skills/api-lookup
```

For a **kagent 1.x alpha AgentTemplate**, the shape is different:

```yaml
skills:
  - name: calculator
    source:
      git:
        url: https://github.com/YOUR_ORG/sample-agent-skills.git
        commit: REPLACE_WITH_FULL_COMMIT_SHA
      path: skills/calculator
```

Add two more entries with the other names and paths. This API requires full
immutable commit identifiers. Updating a template does not update skills in
already-running agent instances; start an instance from the new revision.

For 0.x private Git access, the documented `skills.gitAuthSecretRef.name` selects
a Secret in the agent namespace with a `token` key for HTTPS authentication.
Provision that Secret through your existing secret-management flow. Configure
registry fetch credentials separately if needed; it does not inherit the agent's
Secret automatically. For 1.x, use that release's source authentication schema.

Validate the complete edited manifest before applying:

```sh
kubectl apply --dry-run=server -f YOUR_EXISTING_AGENT_FILE.yaml
kubectl diff -f YOUR_EXISTING_AGENT_FILE.yaml
kubectl apply -f YOUR_EXISTING_AGENT_FILE.yaml
```

Add a brief instruction to your agent's existing system prompt: "Use the attached
calculator, data-retrieval, and api-lookup skills for their matching requests.
Run the bundled helpers and report observed output. Identify catalog data as fictional."

## 7. Verify cluster access and execution

Check the actual skill-fetch workload's events and logs, using the names produced
by your deployment. Successful cloning from a laptop does not prove cluster access.
Verify DNS, HTTPS egress, CA trust, and repository authentication from that runtime.
For Pod-based agents, inspect the skill init-container logs; for Substrate use its
runtime diagnostics. Confirm the pinned revision and all three skill files loaded.

Send these prompts to your existing agent and retain tool traces:

| Prompt | Pass condition |
| --- | --- |
| Use calculator to multiply 12.5 by 8. | Helper executed; result is 100 |
| Use calculator to divide 1 by 0. | Explicit error; no fabricated result |
| Retrieve sample product P100. | Helper executed; fictional notebook, USD 4.50 |
| Retrieve sample product DOES-NOT-EXIST. | Not found |
| Look up public GitHub repository kagent-dev/kagent. | Actual API response, source URL, observation time |

Acceptance evidence to attach to the story:

- Remote repository URL and full commit SHA; successful fetch from the actual cluster runtime.
- Three parsed skill entries in agentregistry plus successful pulls matching that revision.
- Agent configuration and runtime version; traces showing helper execution and expected results.

## Add another skill

Create `skills/<name>/SKILL.md`, write a clear trigger description and procedure,
bundle any scripts/data inside that directory, and document helper inputs if needed.
Test success and failure behavior. Commit and push, register the new revision,
attach it explicitly, and repeat the pull and execution checks.

## References

- [Agent Skills format](https://agentskills.io/specification)
- [Agentregistry publish workflow](https://aregistry.ai/docs/skills/publish/)
- [Agentregistry pull and source pinning](https://aregistry.ai/docs/skills/pull/)
- [Older arctl v0.3.3 skill commands](https://pkg.go.dev/github.com/agentregistry-dev/agentregistry@v0.3.3/internal/cli/skill)
- [kagent 0.x Git skills](https://www.kagent.dev/docs/kagent/0.x/concepts/agents/)
- [kagent 1.x alpha skills](https://kagent.dev/docs/kagent/1.x/skills-and-mcp/skills/)

CC - Ashok Manda
