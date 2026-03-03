# Classly Flutter Mobile Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a new `mobile/` Flutter app for Classly that reuses the UI/UX language of `plane-mobile` without reusing its business logic, and ships the Phase 1 read-only mobile scope.

**Architecture:** Create a fresh Flutter codebase under `mobile/` with feature-based modules, Riverpod for state, GoRouter for routing, Dio for HTTP, and local offline persistence. Treat `plane-mobile` only as a design and interaction reference while deriving auth, event, subject, and sync logic strictly from Classly APIs and the updated product plan.

**Tech Stack:** Flutter 3+, Dart 3+, flutter_riverpod, go_router, dio, freezed, json_serializable, flutter_secure_storage, Drift or Isar, flutter_test

---

### Task 1: Create the mobile project shell

**Files:**
- Create: `mobile/pubspec.yaml`
- Create: `mobile/lib/main.dart`
- Create: `mobile/analysis_options.yaml`
- Create: `mobile/test/`

**Step 1: Create the Flutter app skeleton**

Run: `flutter create mobile`

Expected: a new standalone Flutter app exists under `mobile/`

**Step 2: Replace the generated dependencies with the Classly mobile stack**

Add dependencies for:
- `flutter_riverpod`
- `go_router`
- `dio`
- `freezed_annotation`
- `json_annotation`
- `flutter_secure_storage`
- one local database package

**Step 3: Add dev dependencies**

Add:
- `build_runner`
- `freezed`
- `json_serializable`
- `flutter_lints`

**Step 4: Verify the shell builds**

Run: `flutter analyze`

Expected: no analyzer errors in the fresh shell

**Step 5: Commit**

```bash
git add mobile
git commit -m "feat: scaffold classly mobile app"
```

### Task 2: Add app bootstrap, routing, and session guard

**Files:**
- Create: `mobile/lib/app/app.dart`
- Create: `mobile/lib/app/routing/app_router.dart`
- Create: `mobile/lib/app/bootstrap/bootstrap.dart`
- Create: `mobile/lib/features/auth/presentation/session_gate.dart`
- Test: `mobile/test/app/router_test.dart`

**Step 1: Write the failing router test**

Test cases:
- unauthenticated user lands on `InstanceSelect`
- authenticated user lands on `Kalender`

**Step 2: Run the router test**

Run: `flutter test mobile/test/app/router_test.dart`

Expected: FAIL because routing is not implemented yet

**Step 3: Implement minimal router and session bootstrap**

Add:
- app root widget
- GoRouter setup
- session bootstrap provider
- route guard

**Step 4: Run the router test again**

Run: `flutter test mobile/test/app/router_test.dart`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: add mobile bootstrap and guarded routing"
```

### Task 3: Build the design system foundation from the Plane reference

**Files:**
- Create: `mobile/lib/app/theme/app_theme.dart`
- Create: `mobile/lib/app/theme/app_colors.dart`
- Create: `mobile/lib/app/theme/app_typography.dart`
- Create: `mobile/lib/shared/widgets/primary_button.dart`
- Create: `mobile/lib/shared/widgets/app_text_field.dart`
- Create: `mobile/lib/shared/widgets/state_views.dart`
- Test: `mobile/test/theme/theme_smoke_test.dart`

**Step 1: Write the failing theme smoke test**

Test cases:
- app theme can be built
- primary button renders
- text field renders

**Step 2: Run the theme smoke test**

Run: `flutter test mobile/test/theme/theme_smoke_test.dart`

Expected: FAIL because theme and widgets do not exist yet

**Step 3: Implement the theme layer**

Build a fresh theme inspired by `plane-mobile`:
- spacing rhythm
- card surfaces
- button hierarchy
- form field styling
- loading, empty, error state primitives

**Step 4: Run the theme smoke test again**

Run: `flutter test mobile/test/theme/theme_smoke_test.dart`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: add classly mobile design system foundation"
```

### Task 4: Implement instance selection and auth domain contracts

**Files:**
- Create: `mobile/lib/features/auth/domain/user_session.dart`
- Create: `mobile/lib/features/auth/domain/auth_repository.dart`
- Create: `mobile/lib/features/auth/presentation/instance_select_screen.dart`
- Create: `mobile/lib/features/auth/presentation/login_screen.dart`
- Test: `mobile/test/features/auth/instance_select_test.dart`

**Step 1: Write the failing instance selection test**

Test cases:
- base URL field validates valid https URL
- saved base URL is forwarded into auth bootstrap

**Step 2: Run the auth screen test**

Run: `flutter test mobile/test/features/auth/instance_select_test.dart`

Expected: FAIL because the screen and contracts do not exist yet

**Step 3: Implement minimal auth contracts and screens**

Add:
- `UserSession`
- `AuthRepository` interface
- `InstanceSelectScreen`
- `LoginScreen` shell with Classly wording and OAuth CTA

**Step 4: Run the auth screen test again**

Run: `flutter test mobile/test/features/auth/instance_select_test.dart`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: add instance selection and auth contracts"
```

### Task 5: Implement OAuth callback handling and secure session storage

**Files:**
- Create: `mobile/lib/features/auth/data/auth_api.dart`
- Create: `mobile/lib/features/auth/data/auth_repository_impl.dart`
- Create: `mobile/lib/features/auth/data/session_storage.dart`
- Create: `mobile/lib/features/auth/presentation/callback_handler_screen.dart`
- Test: `mobile/test/features/auth/oauth_callback_test.dart`

**Step 1: Write the failing callback test**

Test cases:
- callback parses `code`
- token exchange success stores session
- invalid callback yields error state

**Step 2: Run the callback test**

Run: `flutter test mobile/test/features/auth/oauth_callback_test.dart`

Expected: FAIL because callback flow is not implemented yet

**Step 3: Implement the minimal OAuth flow**

Add:
- authorize URL builder
- callback parsing
- token exchange client
- secure storage for token
- session restore logic

**Step 4: Run the callback test again**

Run: `flutter test mobile/test/features/auth/oauth_callback_test.dart`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: implement classly oauth mobile session flow"
```

### Task 6: Implement event and subject domain models

**Files:**
- Create: `mobile/lib/features/events/domain/event.dart`
- Create: `mobile/lib/features/subjects/domain/subject.dart`
- Create: `mobile/lib/features/events/data/event_dto.dart`
- Create: `mobile/lib/features/subjects/data/subject_dto.dart`
- Test: `mobile/test/features/events/event_mapping_test.dart`

**Step 1: Write the failing mapping test**

Test cases:
- API event JSON maps into domain event
- API subject JSON maps into domain subject

**Step 2: Run the mapping test**

Run: `flutter test mobile/test/features/events/event_mapping_test.dart`

Expected: FAIL because DTOs and domain types are missing

**Step 3: Implement the models and mappers**

Add:
- domain entities
- DTOs
- JSON serialization
- mapping helpers

**Step 4: Run the mapping test again**

Run: `flutter test mobile/test/features/events/event_mapping_test.dart`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: add event and subject domain mapping"
```

### Task 7: Implement read-only sync and local cache

**Files:**
- Create: `mobile/lib/shared/http/classly_dio.dart`
- Create: `mobile/lib/features/events/domain/events_repository.dart`
- Create: `mobile/lib/features/events/data/events_repository_impl.dart`
- Create: `mobile/lib/features/events/data/events_local_store.dart`
- Create: `mobile/lib/features/subjects/data/subjects_local_store.dart`
- Test: `mobile/test/features/events/sync_events_test.dart`

**Step 1: Write the failing sync test**

Test cases:
- initial sync stores remote events
- delta sync upserts changed events
- cached events are returned before refresh completes

**Step 2: Run the sync test**

Run: `flutter test mobile/test/features/events/sync_events_test.dart`

Expected: FAIL because sync infrastructure does not exist yet

**Step 3: Implement minimal sync flow**

Add:
- Dio client
- auth interceptor
- repository implementation
- local cache interface
- stale-while-revalidate sync method

**Step 4: Run the sync test again**

Run: `flutter test mobile/test/features/events/sync_events_test.dart`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: add read only event sync and cache"
```

### Task 8: Build the Events and Kalender UI

**Files:**
- Create: `mobile/lib/features/events/presentation/events_screen.dart`
- Create: `mobile/lib/features/events/presentation/event_card.dart`
- Create: `mobile/lib/features/events/presentation/event_detail_screen.dart`
- Create: `mobile/lib/features/events/presentation/calendar_screen.dart`
- Test: `mobile/test/features/events/events_screen_test.dart`

**Step 1: Write the failing widget test**

Test cases:
- cached events render in list form
- event card shows type, title, subject, date
- empty state renders when there are no events

**Step 2: Run the events widget test**

Run: `flutter test mobile/test/features/events/events_screen_test.dart`

Expected: FAIL because the screens do not exist yet

**Step 3: Implement the MVP event UI**

Add:
- `EventsScreen`
- `CalendarScreen`
- `EventCard`
- `EventDetailScreen`

Use the Plane-inspired card rhythm, spacing, and hierarchy without importing Plane logic.

**Step 4: Run the events widget test again**

Run: `flutter test mobile/test/features/events/events_screen_test.dart`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: add event list and calendar screens"
```

### Task 9: Build subjects, filters, and search

**Files:**
- Create: `mobile/lib/features/subjects/presentation/subjects_screen.dart`
- Create: `mobile/lib/features/events/presentation/filter_sheet.dart`
- Create: `mobile/lib/features/events/presentation/search_controller.dart`
- Test: `mobile/test/features/events/filtering_test.dart`

**Step 1: Write the failing filtering test**

Test cases:
- filter by event type
- filter by subject
- search matches title and subject name

**Step 2: Run the filtering test**

Run: `flutter test mobile/test/features/events/filtering_test.dart`

Expected: FAIL because filtering logic is not implemented yet

**Step 3: Implement filtering and search**

Add:
- subject list screen
- bottom filter sheet
- search state and filter composition

**Step 4: Run the filtering test again**

Run: `flutter test mobile/test/features/events/filtering_test.dart`

Expected: PASS

**Step 5: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: add event filtering search and subjects screen"
```

### Task 10: Build settings, logout, diagnostics, and app hardening

**Files:**
- Create: `mobile/lib/features/settings/presentation/settings_screen.dart`
- Create: `mobile/lib/features/settings/presentation/diagnostics_screen.dart`
- Create: `mobile/lib/features/auth/application/logout_use_case.dart`
- Test: `mobile/test/features/settings/settings_test.dart`

**Step 1: Write the failing settings test**

Test cases:
- logout clears session
- switch instance clears active session context
- diagnostics exposes last sync and current base URL

**Step 2: Run the settings test**

Run: `flutter test mobile/test/features/settings/settings_test.dart`

Expected: FAIL because settings logic is incomplete

**Step 3: Implement settings and diagnostics**

Add:
- settings screen
- logout use case
- instance switch
- cache clear action
- lightweight diagnostics view

**Step 4: Run the settings test again**

Run: `flutter test mobile/test/features/settings/settings_test.dart`

Expected: PASS

**Step 5: Run the project checks**

Run:
- `flutter analyze`
- `flutter test`

Expected: PASS

**Step 6: Commit**

```bash
git add mobile/lib mobile/test
git commit -m "feat: finalize classly mobile mvp settings and diagnostics"
```

### Task 11: Sync docs and version artifacts

**Files:**
- Modify: `versions/Plans/v1.1/Flutter_App.md`
- Create: `versions/v1.1/Commit.md`
- Create: `versions/v1.1/Readme.md`

**Step 1: Update the product plan**

Ensure the old Flutter plan reflects:
- Plane as UI-only reference
- new mobile architecture
- MVP scope

**Step 2: Add version notes**

Write:
- intended commit summary
- changelog summary

**Step 3: Verify repository state**

Run: `python tests/verify_repo.py`

Expected: PASS if backend code remains unaffected

**Step 4: Commit**

```bash
git add versions docs/plans
git commit -m "docs: add classly mobile implementation planning"
```
