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