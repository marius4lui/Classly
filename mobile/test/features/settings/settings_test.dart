import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/features/auth/application/logout_use_case.dart';
import 'package:classly_mobile/features/auth/domain/auth_repository.dart';
import 'package:classly_mobile/features/auth/domain/user_session.dart';
import 'package:classly_mobile/features/auth/providers/auth_providers.dart';
import 'package:classly_mobile/features/events/data/events_local_store.dart';
import 'package:classly_mobile/features/events/providers/events_providers.dart';
import 'package:classly_mobile/features/settings/presentation/diagnostics_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('logout clears session', () async {
    final repository = _FakeAuthRepository();
    final container = ProviderContainer(
      overrides: [authRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    container
        .read(sessionBootstrapControllerProvider.notifier)
        .setAuthenticated(
          const UserSession(
            baseUrl: 'https://classly.site',
            accessToken: 'token-123',
          ),
        );

    await container.read(logoutUseCaseProvider).logout();

    expect(repository.clearSessionCalls, [false]);
    expect(container.read(sessionBootstrapProvider).isAuthenticated, isFalse);
    expect(
      container.read(sessionBootstrapProvider).baseUrl,
      'https://classly.site',
    );
  });

  test('switch instance clears active session context', () async {
    final repository = _FakeAuthRepository();
    final container = ProviderContainer(
      overrides: [authRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    container
        .read(sessionBootstrapControllerProvider.notifier)
        .setAuthenticated(
          const UserSession(
            baseUrl: 'https://classly.site',
            accessToken: 'token-123',
          ),
        );

    await container.read(logoutUseCaseProvider).switchInstance();

    expect(repository.clearSessionCalls, [true]);
    expect(container.read(sessionBootstrapProvider).baseUrl, isNull);
    expect(container.read(sessionBootstrapProvider).isAuthenticated, isFalse);
  });

  testWidgets('diagnostics exposes last sync and current base url', (
    tester,
  ) async {
    final eventsStore = InMemoryEventsLocalStore();
    await eventsStore.saveLastSyncAt(DateTime.utc(2026, 3, 3, 12, 30));

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          eventsLocalStoreProvider.overrideWithValue(eventsStore),
          sessionBootstrapProvider.overrideWithValue(
            const SessionBootstrapState.authenticated(
              baseUrl: 'https://classly.site',
              session: UserSession(
                baseUrl: 'https://classly.site',
                accessToken: 'token-123',
              ),
            ),
          ),
        ],
        child: const MaterialApp(home: DiagnosticsScreen()),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('https://classly.site'), findsOneWidget);
    expect(find.text('2026-03-03 12:30 UTC'), findsOneWidget);
  });
}

class _FakeAuthRepository implements AuthRepository {
  final List<bool> clearSessionCalls = [];

  @override
  Uri buildAuthorizeUri({required String baseUrl}) => Uri.parse(baseUrl);

  @override
  Future<void> clearSession({bool clearBaseUrl = false}) async {
    clearSessionCalls.add(clearBaseUrl);
  }

  @override
  Future<UserSession> completeOAuthCallback(
    Uri callbackUri, {
    String? baseUrl,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<String?> getSavedBaseUrl() async => null;

  @override
  Future<UserSession?> restoreSession() async => null;

  @override
  Future<void> saveBaseUrl(String baseUrl) async {}

  @override
  Future<void> saveSession(UserSession session) async {}
}
