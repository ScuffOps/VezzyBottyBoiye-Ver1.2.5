# Vezbot Commands

## Setup Commands

### `/setup`
Interactive setup wizard for configuring your server.
- **Permission**: Administrator
- **Description**: Guides you through channel selection, thread type, staff roles, and module configuration.

## Ticket Commands

### `/ticket-panel`
Create a ticket panel message with a button to create tickets.
- **Permission**: Manage Guild
- **Description**: Posts an embed with a button that opens a modal to create tickets.

## Embed Commands

### `/embed-create`
Create and post an embed message.
- **Permission**: Manage Guild
- **Parameters**:
  - `title`: Embed title
  - `description`: Embed description
  - `channel`: Target channel (optional, defaults to current channel)

### `/embed-save`
Save an embed as a template.
- **Permission**: Manage Guild
- **Parameters**:
  - `name`: Template name
  - `title`: Embed title
  - `description`: Embed description

## Poll Commands

### `/poll-create`
Create a poll.
- **Permission**: Manage Guild
- **Parameters**:
  - `question`: Poll question
  - `options`: Options separated by `|` (e.g., "Option 1|Option 2|Option 3")
  - `type`: "single" or "multi" (default: "single")
  - `channel`: Target channel (optional)
  - `closes_at`: ISO format date/time (optional)

## Reminder Commands

### `/reminder-set`
Set a personal reminder.
- **Parameters**:
  - `message`: Reminder message
  - `when`: ISO format date/time (e.g., "2024-01-01T12:00:00Z")
  - `channel`: Channel to remind in (optional, defaults to DM)

### `/timezone-set`
Set your timezone preference.
- **Parameters**:
  - `timezone`: IANA timezone (e.g., "America/New_York")

## Admin Commands

### `/ping`
Check bot latency.
- **Description**: Returns bot response time in milliseconds.

## Permissions Matrix

| Command         | Permission Required |
|-----------------|---------------------|
| `/setup`        | Administrator       |
| `/ticket-panel` | Manage Guild        |
| `/embed-create` | Manage Guild        |
| `/embed-save`   | Manage Guild        |
| `/poll-create`  | Manage Guild        |
| `/reminder-set` | None (all users)    |
| `/timezone-set` | None (all users)    |
| `/ping`         | None (all users)    |
