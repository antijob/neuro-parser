# telegram-subscriptions Specification

## Purpose

Telegram chats subscribed through the bot choose incident categories and geographies and receive notifications about newly predicted incidents that match those preferences.

## Requirements

### Requirement: Category selection

The bot SHALL let a user enable or disable incident categories for a subscribed chat and SHALL persist the selection as that chat's preferences.

#### Scenario: User enables a category

- **WHEN** a user enables an incident category for a chat through the bot keyboard
- **THEN** the category is saved as enabled in that chat's preferences

### Requirement: Geography filters

The bot SHALL let a user enable countries for each enabled category and, within a country, either all regions or a selected set of regions.

#### Scenario: User restricts a country to selected regions

- **WHEN** a user enables a country for a category and selects specific regions
- **THEN** only incidents from those regions of that country match the chat's preferences for that category

#### Scenario: User enables all regions of a country

- **WHEN** a user enables a country for a category with all regions
- **THEN** incidents from any region of that country match the chat's preferences for that category

### Requirement: Notification delivery for matching incidents

The system SHALL send a notification to every chat whose enabled category, country and regions match an incident created by the prediction pipeline, and SHALL NOT send it to non-matching chats.

#### Scenario: Matching incident is delivered

- **WHEN** the prediction pipeline creates an incident whose category, country and region match a chat's preferences
- **THEN** that chat receives a notification about the incident

#### Scenario: Non-matching incident is not delivered

- **WHEN** the prediction pipeline creates an incident whose category, country or region does not match a chat's preferences
- **THEN** that chat does not receive a notification about the incident

### Requirement: Delivery under Telegram rate limits

The system SHALL retry a notification with backoff when Telegram rejects it because of a rate limit, up to a bounded number of attempts.

#### Scenario: Rate-limited notification is retried

- **WHEN** Telegram rejects a notification with a rate-limit response
- **THEN** the notification is retried later with backoff until it is delivered or the retry limit is reached
