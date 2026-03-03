import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/features/auth/domain/auth_repository.dart';
import 'package:classly_mobile/features/auth/domain/user_session.dart';
import 'package:classly_mobile/features/auth/presentation/instance_select_screen.dart';
import 'package:classly_mobile/features/auth/providers/auth_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('base url field validates valid https url', (tester) async {
    final container = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(_FakeAuthRepository()),
      ],
    );
    addTearDown(container.dispose);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: InstanceSelectScreen()),
      ),
    );

    await tester.enterText(find.byType(TextFormField), 'http://classly.local');
    await tester.tap(find.text('Weiter'));
    await tester.pump();

    expect(
      find.text('Bitte eine gueltige https:// URL eingeben'),
      findsOneWidget,
    );

    await tester.enterText(find.byType(TextFormField), 'https://classly.site');
    await tester.tap(find.text('Weiter'));
    await tester.pump();

    expect(
      find.text('Bitte eine gueltige https:// URL eingeben'),
      findsNothing,
    );
  });

  testWidgets('saved base url is forwarded into auth bootstrap', (
    tester,
  ) async {
    final repository = _FakeAuthRepository();
    final container = ProviderContainer(
      overrides: [authRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: InstanceSelectScreen()),
      ),
    );

    await tester.enterText(find.byType(TextFormField), 'https://classly.site');
    await tester.tap(find.text('Weiter'));
    await tester.pump();

    expect(repository.savedBaseUrl, 'https://classly.site');
    expect(
      container.read(sessionBootstrapProvider).baseUrl,
      'https://classly.site',
    );
  });
}

class _FakeAuthRepository implements AuthRepository {
  String? savedBaseUrl;

  @override
  Uri buildAuthorizeUri({required String baseUrl}) {
    return Uri.parse('$baseUrl/api/oauth/authorize');
  }

  @override
  Future<String?> getSavedBaseUrl() async => savedBaseUrl;

  @override
  Future<UserSession> completeOAuthCallback(
    Uri callbackUri, {
    String? baseUrl,
  }) {
    throw UnimplementedError();
  }

  @override
  Future<void> clearSession() async {}

  @override
  Future<void> saveBaseUrl(String baseUrl) async {
    savedBaseUrl = baseUrl;
  }

  @override
  Future<UserSession?> restoreSession() async => null;

  @override
  Future<void> saveSession(UserSession session) async {}
}
