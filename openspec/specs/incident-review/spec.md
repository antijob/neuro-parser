# incident-review Specification

## Purpose

Analysts review incidents created by the prediction pipeline, set their lifecycle status explicitly, and assess source quality and classifier outcomes.

## Requirements

### Requirement: Incident review access

The system SHALL let an analyst list, search and filter incidents in the admin interface by status and incident type.

#### Scenario: Analyst filters incidents

- **WHEN** an analyst filters incidents by status or incident type in the admin interface
- **THEN** only matching incidents are listed, each with its title, incident type, creation date, status and the related article's prediction rate

### Requirement: Explicit status transitions

The system SHALL create predicted incidents with the unprocessed status and SHALL change an incident's status only through an explicit action, such as an analyst accepting or rejecting it.

#### Scenario: New incident awaits review

- **WHEN** the prediction pipeline creates an incident
- **THEN** the incident has the unprocessed status

#### Scenario: Analyst rejects an incident

- **WHEN** an analyst sets a processed incident's status to rejected
- **THEN** the incident keeps the rejected status until it is changed explicitly

### Requirement: Subscriber feedback

The system SHALL record downvotes that subscribers give to notified incidents and SHALL let analysts filter incidents by a minimum number of downvotes.

#### Scenario: Analyst reviews downvoted incidents

- **WHEN** an analyst filters incidents by a minimum number of downvotes in the admin interface
- **THEN** only incidents with at least that many downvotes are listed

### Requirement: Source quality monitoring

The system SHALL let an analyst inspect fetched articles with their processing flags (downloaded, parsed, duplicate, redirect, incorrect) and prediction rate.

#### Scenario: Analyst inspects articles

- **WHEN** an analyst opens the article list in the admin interface
- **THEN** each article is shown with its processing flags and prediction rate
