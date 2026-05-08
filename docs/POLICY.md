# Policy Engine

## Overview

The policy engine enforces access control, approval triggers, and route restrictions. It runs *after* semantic matching and *before* tool execution.

## Policy Rules

### Blocked Routes

Entire routes can be blocked regardless of user permissions:

```yaml
blocked_routes:
  - refund_request
```

### Required Permissions

Each route declares required permissions. The policy engine checks the user's permissions against these requirements:

```yaml
permission_map:
  invoice_lookup: ["billing.read"]
  refund_request: ["billing.write", "finance.approve"]
  support_ticket: ["support.read"]
```

### Approval Triggers

Routes can require additional approval when certain conditions are met:

```yaml
approval_required:
  - route: refund_request
    condition: "amount > 500"
    message: "Refunds over $500 require manager approval"
```

## Policy Evaluation Flow

```
Selected Route + User Context
        │
        ▼
  ┌─────────────┐
  │ Is route     │──Yes──▶ REJECT: "Route is blocked"
  │ blocked?     │
  └──────┬──────┘
         │ No
         ▼
  ┌─────────────┐
  │ Has required │──No───▶ REJECT: "Missing permissions: [...]"
  │ permissions? │
  └──────┬──────┘
         │ Yes
         ▼
  ┌─────────────┐
  │ Approval     │──Yes──▶ REJECT: "Requires approval: <message>"
  │ triggered?   │
  └──────┬──────┘
         │ No
         ▼
       ALLOW
```

## PolicyDecision Model

```python
class PolicyDecision(BaseModel):
    allowed: bool
    reason: str | None = None
    required_action: str | None = None
    missing_permissions: list[str] = []
```

## Integration with Routing

The policy engine is called by the `RouteSelector` after semantic matching. If the top match is blocked, the selector tries the next best match before falling back to the `FallbackHandler`.
