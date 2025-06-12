def format_emails_for_llm(emails):
    return "\n\n".join([
            f"""From: {email['from']}
    Subject: {email['subject']}
    Date: {email['date']}
    Snippet: {email['snippet']}"""
            for email in emails
        ])

def format_prompt(emails: list[dict]) -> str:
    formatted_emails = format_emails_for_llm(emails)

    prompt_context = (
        "You are an intelligent email assistant. Your task is to read a user's recent emails and extract actionable insights. "
        "Classify emails into one of four categories based on the content:\n\n"
        "1. \"meetings\": Emails that contain scheduled meetings, calendar invites, or time/location details.\n"
        "2. \"urgent\": Emails that require immediate attention or have deadlines within 48 hours.\n"
        "3. \"todos\": Emails that contain tasks, requests, or deliverables the user needs to follow up on.\n"
        "4. \"other\": Any emails that don't fit the above categories (e.g., FYI, newsletters).\n\n"
        "Each email contains the following fields:\n"
        "- From\n"
        "- Subject\n"
        "- Date\n"
        "- Snippet (short content preview)\n\n"
        "Here are the emails:\n"
        "===\n"
        f"{formatted_emails}\n"
        "===\n\n"
        "Return your response as a **strict JSON object** with only these four top-level keys: \"meetings\", \"urgent\", \"todos\", and \"other\". "
        "Each key should map to a list of email summaries (as short strings). "
        "Do not include any commentary, markdown, or extra explanation—**only raw JSON output**."
    )

    return prompt_context

def format_classification_prompt(emails: list[dict]) -> str:
    """
    Build an LLM prompt to classify emails into multiple categories.
    """
    formatted_emails = format_emails_for_llm(emails)

    prompt_context = (
        "You are an intelligent email assistant. Your task is to read a user's recent emails and classify them into one of eight categories based on the content:\n\n"
        "1. \"meetings\": Scheduled meetings, calendar invites, or time/location details.\n"
        "2. \"urgent\": Emails requiring immediate attention or deadlines within 48 hours.\n"
        "3. \"todos\": Emails containing tasks, requests, or deliverables.\n"
        "4. \"work\": Emails related to work topics (project updates, company announcements).\n"
        "5. \"school\": Emails related to school or academic courses (assignments, grades).\n"
        "6. \"bills\": Billing statements, invoices, or payment reminders.\n"
        "7. \"travel\": Travel itineraries, booking confirmations, trip details.\n"
        "8. \"other\": Any emails that don't fit the above categories (e.g., newsletters).\n\n"
        "Each email has these fields:\n"
        "- From\n"
        "- Subject\n"
        "- Date\n"
        "- Snippet\n\n"
        "Here are the emails to classify:\n"
        "===\n"
        f"{formatted_emails}\n"
        "===\n\n"
        "Return your response as a **strict JSON object** with exactly these eight keys: "
        "\"meetings\", \"urgent\", \"todos\", \"work\", \"school\", \"bills\", \"travel\", and \"other\". "
        "Each key should map to a list of email summaries (short strings). "
        "Do not include any commentary or extra explanation, **only raw JSON output.**"
    )

    return prompt_context