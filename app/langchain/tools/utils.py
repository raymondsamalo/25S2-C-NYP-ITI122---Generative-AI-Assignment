""""Utility functions for tool output formatting and validation."""
import re

def format_tool_output(title, data):
    """Generic formatting template."""
    sections = [f"{title}", "=" * len(title), ""]

    for section_name, section_data in data.items():
        sections.append(f"{section_name}:")
        sections.append("-" * len(section_name))

        if isinstance(section_data, list):
            for item in section_data:
                sections.append(f"• {item}")
        elif isinstance(section_data, dict):
            for key, value in section_data.items():
                sections.append(f"  {key}: {value}")
        else:
            sections.append(f"  {section_data}")

        sections.append("")

    return "\n".join(sections).strip()

def format_policy_data(title, policy_data):
    """Format policy data into a table string."""
    header = policy_data.get("header", [])
    data = policy_data.get("data", [])

    sections = [f"{title}", "=" * len(title), ""]

    # Create table header
    header_line = "| " + " | ".join(header) + " |"
    separator_line = "| " + " | ".join(['-' * len(col) for col in header]) + " |"
    sections.append(header_line)
    sections.append(separator_line)

    # Create table rows
    for row in data:
        row_line = "| " + " | ".join(str(item) for item in row) + " |"
        sections.append(row_line)

    sections.append("")
    return "\n".join(sections).strip()

def format_tool_key_value_table(title,key_column, value_column, data):
    """Generic formatting template."""
    sections = [f"{title}", "=" * len(title), ""]
    sections.append(f"|{key_column} | {value_column}|")
    sections.append(f"|{'-' * len(key_column)} | {'-' * len(value_column)}|")
    for key, value in data.items():
        sections.append(f"|{key:10} | {value:15}|")
    sections.append("")
    return "\n".join(sections).strip()

def format_tool_error(error_message):
    """Format an error message for tool output."""
    return f"Error: {error_message}"

def is_valid_email(email: str) -> bool:
    """Check if the provided string is a valid email address."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def is_valid_customer_id(identifier: str) -> bool:
    """Check if the provided string is a valid customer ID (digits only)."""
    return identifier.strip().isdigit()

def is_valid_credit_score(score: str) -> bool:
    """Check if the provided string is a valid credit score (integer between 300 and 850)."""
    if not score.strip().isdigit():
        return False
    score_int = int(score.strip())
    return 300 <= score_int <= 850

def is_valid_account_status(status: str) -> bool:
    """Check if the provided string is a valid account status."""
    valid_statuses = {"Good-standing", "Delinquent", "Closed"}
    return status.strip().capitalize() in valid_statuses

def if_none(value, default_value):
    """Return default value if the input value is None."""
    if value is None:
        return default_value
    return value
