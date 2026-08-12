# Backend App Design

**login**

Handles OAuth authentication, separate from the user identity model. Contains `OAuthUser`, a wrapper around the base `User` that ties a user to an external platform UID (a `BigIntegerField`), and `AuthenticationRequest`, which models a single OAuth flow with a `state` UUID (primary key, used as CSRF protection), a `requested_at` timestamp, and a `challenge` string. Depends only on `users` (the wrapped user model). This app is purely the authentication layer; it stores no profile data itself.

**users**

Handles identity. Contains a custom `User` model extending Django's `AbstractUser`, storing `username`, `initials`, `display_name`, and `profile_photo` (a URL). A custom `UserManager` defines user and superuser creation, and a `UserPermissions` helper defines the custom permission set (`PARTICIPANT`, `MENTOR`, `IC_MEMBER`) used to gate actions like grading. This is the root dependency of the project, almost every other app references `User` (referenced through `settings.AUTH_USER_MODEL`).

**accounts**

A generic ledger system. Contains `Account` (a balance account, with the balance stored directly as a `PositiveIntegerField` and mutated atomically via `add_to_balance` / `subtract_from_balance` using `select_for_update` locks) and a `Transaction` hierarchy (a ledger). Unlike a pure event-sourced ledger, the balance is a stored field that each transaction commits to on `save()`; mistakes are corrected by appending `ReversedTransaction` entries with negated amounts (`reverse_transaction`), and transactions are never edited in place. Transaction behavior is expressed through subclassing rather than a type field: `GradingTransaction`, `ItemTransaction`, `ReversedTransaction`, and `AdminTransaction` each override `_retrieve_amount()` to decide how the amount is computed (for example, `ItemTransaction` reads the item price; `GradingTransaction` and `AdminTransaction` clamp negative amounts so the balance never goes below zero). `Account` is subclassed into `TeamAccount` (carries a `team` FK, used for the global points total) and `TournamentAccount` (carries `team`, `tournament`, and a `type` of `points` or `coins`, with a uniqueness constraint per team/tournament/type). The app depends on `teams` and `tournaments` only because the concrete account subclasses point back at them; it knows nothing about challenges, submissions, or stores.

**teams**

Manages teams of users. A `Team` has a name, a many-to-many relationship to `User` (`members`), and a many-to-many relationship to `Tournament` (`tournaments`), so the same team can enroll in multiple tournaments directly rather than through a join model. There is no `TournamentTeamEntry`; account scoping is done from the account side (`TeamAccount` and `TournamentAccount` carry the FKs). Provides accessor helpers (`get_main_account`, `get_tournament_points_account`, `get_tournament_coins_account`, `get_tournament_inventory`) and a `grade(tournament, amount)` method that creates three `GradingTransaction` records at once: the tournament points account, the tournament coins account, and the team-wide main points account. Depends on `users`, `accounts`, `tournaments`, and `stores` (for inventory lookups). Note that the per-team accounts and inventories are not created in `Team.save()`; they are provisioned through the team admin form.

**tournaments**

Manages scavenger hunt events. A `Tournament` has a name, slug, and an active time window (`active_from` / `active_until`), guarded by a check constraint that the start is not after the end. A `TournamentQueryset` plus `revealed` / `active` properties express visibility (revealed once the start time has passed, active until the end time). It acts as the top-level container, challenges and a store hang off a tournament, and team enrollments are the `Team.tournaments` M2M. Depends on nothing else (the relationships are declared from the other side). `store` has a one-to-one with a tournament representing the store for each tournament.

**challenges**

Manages the tasks that teams must complete. A `Challenge` belongs to a single tournament and has a name, slug, description, an optional `thumbnail` (FK to `files.File`), a `points` value, an optional active time window, an `enabled` flag (challenges are shown when enabled, not hidden by a separate disabled flag), and a `submission_visibility` setting (`Always visible` or `When accepted`). A `ChallengeQuerySet` and `is_revealed` / `is_active` properties express visibility, factoring in both the challenge's own window and the tournament's revealed state. Depends on `tournaments` and `files`. Challenges are referenced by `submissions`, each submission references exactly one challenge to indicate what task was completed.

**file**

Handles the upload and media processing pipeline, supporting both local storage and direct-to-S3. `File` is a single model representing a stored file, with a UUID7 primary key, a `source`, an optional `thumbnail`, an `is_compressed` flag, MIME-type validation, storage-key bookkeeping, and `from_source` / `from_storage_key` factories plus `url` / `thumbnail_url` accessors that branch on local vs. S3 storage. `FileStorageRequest` tracks an in-progress presigned S3 upload so orphaned uploads can be cleaned up by a cron job. `CompressionRequest` and `ThumbnailRequest` each have a one-to-one to a `File` and record a pending AWS job (with a retry counter), polled by cron jobs. A `post_delete` signal deletes the underlying physical file. Depends on nothing else among the domain apps. Files are consumed by `submissions` (each submission has a one-to-one with a `File` proof photo or video) and also referenced as thumbnails by `challenges` and `stores`.

The compression pipeline seems overkill, but considering the code is already there in the reference codebase - we could just reuse that.

**submission**

The core workflow app. A `Submission` links a `Challenge`, `Tournament` (auto-filled from the challenge on save), `Team`, `File` (proof photo/video), and the submitting/last-updating `User` (`created_by` / `updated_by`). It tracks grading state through an `accepted` field (`None` = pending) and a `received_points` value, plus `is_viewed` / `viewed_at` for the admin review queue. Submissions themselves do not hold the transaction FKs; grading is performed in the grading API view, which guards against double-grading by fetching the submission with `accepted=None`, then calls `Team.grade(...)` (creating the points and coins transactions) and writes back `received_points` and `accepted` inside an atomic block. A `post_delete` signal deletes the attached file. Depends on `challenges`, `tournaments`, `teams`, `files`, and `users`. This is where most of the submission-side business logic lives, but the transaction creation itself is delegated to `teams` and `accounts`.

**store**

Manages the marketplace. A `Store` has a one-to-one relationship to a `Tournament` (one store per tournament) plus a name and description. `Item` represents a purchasable item with a store FK, name, description, price in coins, and an optional `thumbnail` (FK to `files.File`). `Purchase` records a team's purchase, linking the `Team`, the `Item`, and the resulting `Transaction`; its overridden `save()` resolves the team's coins account for the item's tournament, creates an `ItemTransaction` (raising on insufficient funds), and grants a `UsableItem` into the team's `Inventory`. `Inventory` is the per-team, per-tournament holder of purchased `UsableItem`s, and `UsedItemReceipt` records when an item is consumed (its `use()` deletes the `UsableItem` and writes a receipt). Depends on `tournaments`, `teams`, `accounts`, and `files`. The purchase flow mirrors the grading flow, both create transactions against an account, but store purchases debit the coins account while grading credits points and coins.

**core**

The Django project configuration. Contains split settings (`base` / `development` / `production`), URL routing, WSGI entry point, and shared utilities. Not a domain app. Contains no models.

## App dependency graph

```
users  ←──────────────────────────────────────────────┐
  ↑                                                     │
login                                                   │
                                                        │
accounts ──→ teams ──→ tournaments                      │
   ↑           │            ↑                           │
   │           ├────────────┤                           │
   │           ↓            │                           │
   │        stores ─────────┤                           │
   │           ↑            │                           │
   │        files ←── challenges ──→ tournaments        │
   │           ↑            ↑                           │
   └─────── submissions ────┴───→ teams, users ─────────┘
```

Edges point from an app to the apps it depends on. `users` is the root (referenced almost everywhere), `submissions` is the most dependency-heavy app, and `accounts` underpins all currency movement while staying ignorant of the domain apps that drive it.
