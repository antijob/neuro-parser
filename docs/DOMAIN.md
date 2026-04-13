# Domain

## Core Entities

- IncidentType: category definition and classifier target
- MediaIncident: prediction result linked to source article and lifecycle status
- Source: external media endpoint used for discovery and crawling
- Article: fetched and parsed content unit used for prediction
- Country and Region: geo classifiers for filtering and routing
- Channel: Telegram destination with category and geography preferences

## Incident Lifecycle

Typical status progression:

1. Unprocessed
2. In progress
3. Processed and accepted or processed and rejected
4. Communication and completion states for downstream handling
5. Deleted when removed from active handling

## Classification Model

- Incident types are active/inactive and shape prediction scope.
- Predictions output confidence/rate used for acceptance decisions.
- Accepted incidents are used for notifications and API consumers.

## Domain Rules

- Source parsing and article parsing are distinct concerns.
- Duplicate article handling happens before incident planning.
- Notification eligibility depends on incident type and subscriber preferences.

## See Also

- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- API contracts: [API.md](API.md)
- Bot routing: [BOT.md](BOT.md)
