# Localization and Content Policy

## Supported languages

Only:
- English (`en`)
- Bahasa Indonesia (`id`)

Do not add other interface languages without a product decision.

## Defaults

- Default: English.
- User can select Bahasa Indonesia.
- Persist preference for authenticated users.
- Use browser locale only as an initial suggestion, not as a forced permanent choice.

## What must be localized

- Navigation and interface labels
- Forms and validation messages
- Empty states and error messages
- Query explanations
- AI responses
- Knowledge articles
- Professional tool guides
- Learning paths and exercises
- Emails and notifications
- Accessibility labels

## Technical language

Preserve standard technical terms where translation would reduce clarity. For example, SQL, index, query plan, tablespace, buffer pool, replication, failover, and deadlock may remain in English with Indonesian explanations.

## Content model

Store language as a first-class field. Link translations using a translation group ID. Do not assume every article has a complete translation.

Show a clear notice when a translation is unavailable.

## AI behavior

Pass the selected language explicitly to the AI orchestration layer. SQL syntax, identifiers, commands, and vendor terminology must not be translated. Explanations should follow the selected language.
