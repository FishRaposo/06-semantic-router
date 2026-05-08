"""Mock business tools for testing and development."""

from pydantic import BaseModel, Field
from typing import Any, Callable, Coroutine


class InvoiceResult(BaseModel):
    """Result schema for invoice lookup tool."""

    invoice_id: str = Field(..., description="The invoice identifier")
    status: str = Field(default="paid", description="Payment status")
    amount: float = Field(default=0.0, description="Invoice amount")
    due_date: str = Field(default="", description="Due date for payment")


class SupportTicketResult(BaseModel):
    """Result schema for support ticket creation tool."""

    ticket_id: str = Field(..., description="The created ticket identifier")
    status: str = Field(default="open", description="Ticket status")
    priority: str = Field(default="medium", description="Ticket priority level")


class RefundResult(BaseModel):
    """Result schema for refund request tool."""

    refund_id: str = Field(..., description="The refund request identifier")
    status: str = Field(default="pending", description="Refund status")
    estimated_days: int = Field(default=5, description="Estimated processing days")


class PolicyResult(BaseModel):
    """Result schema for policy question tool."""

    question: str = Field(..., description="The policy question asked")
    answer: str = Field(default="", description="The policy answer")
    source: str = Field(default="knowledge_base", description="Answer source")


class SalesLeadResult(BaseModel):
    """Result schema for sales lead capture tool."""

    lead_id: str = Field(..., description="The lead identifier")
    status: str = Field(default="new", description="Lead status")
    assigned_to: str = Field(default="sales_team", description="Assigned team or person")


async def invoice_lookup(query: str, context: dict) -> dict[str, Any]:
    """Look up invoice details based on a query.

    Args:
        query: The user's query about an invoice.
        context: Additional context for the lookup.

    Returns:
        A dictionary with invoice details.
    """
    result = InvoiceResult(invoice_id="INV-001", status="paid", amount=150.00, due_date="2025-02-01")
    return result.model_dump()


async def support_ticket(query: str, context: dict) -> dict[str, Any]:
    """Create a support ticket from a user query.

    Args:
        query: The user's support request.
        context: Additional context for ticket creation.

    Returns:
        A dictionary with ticket details.
    """
    result = SupportTicketResult(ticket_id="TKT-001", status="open", priority="medium")
    return result.model_dump()


async def refund_request(query: str, context: dict) -> dict[str, Any]:
    """Process a refund request.

    Args:
        query: The user's refund request description.
        context: Additional context for the refund.

    Returns:
        A dictionary with refund details.
    """
    result = RefundResult(refund_id="REF-001", status="pending", estimated_days=5)
    return result.model_dump()


async def policy_question(query: str, context: dict) -> dict[str, Any]:
    """Answer a policy question.

    Args:
        query: The user's policy question.
        context: Additional context for the lookup.

    Returns:
        A dictionary with the policy answer.
    """
    result = PolicyResult(
        question=query,
        answer="According to our policy, all refunds must be requested within 30 days of purchase.",
        source="knowledge_base",
    )
    return result.model_dump()


async def sales_lead(query: str, context: dict) -> dict[str, Any]:
    """Capture a sales lead from a user inquiry.

    Args:
        query: The user's sales inquiry.
        context: Additional context for lead capture.

    Returns:
        A dictionary with lead details.
    """
    result = SalesLeadResult(lead_id="LEAD-001", status="new", assigned_to="sales_team")
    return result.model_dump()


MOCK_TOOLS: dict[str, Callable[..., Coroutine[Any, Any, dict[str, Any]]]] = {
    "invoice_lookup": invoice_lookup,
    "support_ticket": support_ticket,
    "refund_request": refund_request,
    "policy_question": policy_question,
    "sales_lead": sales_lead,
}
