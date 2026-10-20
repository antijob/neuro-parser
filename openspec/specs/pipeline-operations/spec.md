# pipeline-operations Specification

## Purpose

Operators keep the crawling, parsing, prediction and notification pipeline healthy by monitoring background tasks, inspecting failures and managing media sources.

## Requirements

### Requirement: Pipeline health visibility

The system SHALL expose the state of scheduled and running background tasks to operators through a task monitoring interface.

#### Scenario: Operator checks pipeline health

- **WHEN** an operator opens the task monitoring interface
- **THEN** the operator sees which pipeline tasks are running, succeeded or failed

### Requirement: Failure inspection

The system SHALL keep failed background tasks and their error details available to operators.

#### Scenario: Operator inspects a failed task

- **WHEN** a pipeline task fails
- **THEN** the operator can see the failure and its error details in the task monitoring interface or logs

### Requirement: Source management

The system SHALL let an operator add, activate and deactivate media sources through the admin interface, and SHALL crawl only active sources.

#### Scenario: Operator deactivates a source

- **WHEN** an operator deactivates a media source
- **THEN** that source is not crawled in subsequent scheduled runs

#### Scenario: Operator adds several sources at once

- **WHEN** an operator creates a source entry containing several whitespace-separated URLs
- **THEN** a separate source is created for each URL that does not already exist

### Requirement: Article reprocessing

The system SHALL let an operator force selected articles to be parsed again.

#### Scenario: Operator forces a reparse

- **WHEN** an operator applies the force-parse action to selected articles
- **THEN** those articles are marked as not parsed and are processed again by the pipeline
