"""Static public roadmap content. No database records or unapproved features."""

from typing import NamedTuple


class DisplayItem(NamedTuple):
    index: str
    title: str
    description: str


VALUES = (
    DisplayItem("01", "Engage.", "Connect ideas and people"),
    DisplayItem("02", "Reason.", "Think with clarity and purpose"),
    DisplayItem("03", "Progress.", "Turn learning into impact"),
)

ECOSYSTEM = (
    DisplayItem(
        "01", "Developer Hub",
        "Engineering knowledge, reusable patterns and collaboration across technology stacks.",
    ),
    DisplayItem(
        "02", "Community",
        "Focused conversations, expert connections and valuable peer-to-peer learning.",
    ),
    DisplayItem(
        "03", "Learning Academy",
        "Structured paths, assessments and practical skills for career growth.",
    ),
    DisplayItem(
        "04", "Career Connections",
        "Opportunities and employer networks, with approved integrations when available.",
    ),
    DisplayItem(
        "05", "Solutions Marketplace",
        "Discover products, business solutions and independent expertise.",
    ),
    DisplayItem(
        "06", "Intelligent Advisory",
        "Human-reviewed architecture insight and evidence-led technology decisions.",
    ),
)

AI_FLOW = (
    DisplayItem("01", "Knowledge", "Discover context"),
    DisplayItem("02", "Reasoning", "Evaluate options"),
    DisplayItem("03", "Human review", "Validate decisions"),
    DisplayItem("04", "Progress", "Improve outcomes"),
)

ROADMAP = (
    DisplayItem("01", "Foundation", "Brand and secure website"),
    DisplayItem("02", "Connection", "Identity and community"),
    DisplayItem("03", "Opportunity", "Learning, developers and careers"),
    DisplayItem("04", "Intelligence", "Opt-in AI and integrations"),
)
