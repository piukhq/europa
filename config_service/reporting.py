import requests
from django.conf import settings


def teams_notify(message, summary, activity_title):
    """
    Sends `message` to the 'Prototype' channel on Microsoft Teams.
    """
    if not settings.TEAMS_WEBHOOK:
        return

    TEAMS_WEBHOOK_URL = settings.TEAMS_WEBHOOK
    template = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "1A1F71",
        "summary": summary,
        "Sections": [
            {
                "activityTitle": activity_title,
                "facts": [
                    {"name": "Message", "value": message},
                ],
                "markdown": False,
            }
        ],
    }
    return requests.post(TEAMS_WEBHOOK_URL, json=template)
