import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/features/auth/application/auth_flow_launcher.dart';
import 'package:classly_mobile/features/auth/domain/auth_repository.dart';
import 'package:classly_mobile/features/auth/domain/user_session.dart';
import 'package:classly_mobile/features/auth/presentation/login_screen.dart';
import 'package:classly_mobile/features/auth/providers/auth_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  setUp(() {
    TestWidgetsFlutterBinding.ensureInitialized();
  });

  testWidgets('login starts without custom instance form visible', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(430, 1400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    final container = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(_FakeAuthRepository()),
      ],
    );
    addTearDown(container.dispose);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    expect(find.text('Mit Classly anmelden'), findsOneWidget);
    expect(find.text('Advanced'), findsOneWidget);
    expect(find.text('Instanz speichern'), findsNothing);
    expect(find.text(defaultClasslyBaseUrl), findsOneWidget);
  });

  testWidgets('login button launches oauth in external browser', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(430, 1400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    final launcher = _FakeAuthFlowLauncher();
    final container = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(_FakeAuthRepository()),
        authFlowLauncherProvider.overrideWithValue(launcher),
      ],
    );
    addTearDown(container.dispose);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    await tester.tap(find.text('OAuth im Browser starten'));
    await tester.pumpAndSettle();

    expect(launcher.lastBaseUrl, defaultClasslyBaseUrl);
  });

  testWidgets('advanced section validates custom https url', (tester) async {
    tester.view.physicalSize = const Size(430, 1400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    final container = ProviderContainer(
      overrides: [
        authRepositoryProvider.overrideWithValue(_FakeAuthRepository()),
      ],
    );
    addTearDown(container.dispose);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    await tester.tap(find.text('Advanced'));
    await tester.pumpAndSettle();
    expect(find.text('Eigene Instanz'), findsOneWidget);
    await tester.enterText(find.byType(TextFormField), 'http://classly.local');
    await tester.tap(find.text('Instanz speichern'));
    await tester.pump();

    expect(
      find.text('Bitte eine gueltige https:// URL eingeben'),
      findsOneWidget,
    );
  });

  testWidgets('saved base url is forwarded into auth bootstrap', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(430, 1400);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.reset);

    final repository = _FakeAuthRepository();
    final container = ProviderContainer(
      overrides: [authRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    await tester.tap(find.text('Advanced'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextFormField), 'https://classly.site');
    await tester.tap(find.text('Instanz speichern'));
    await tester.pumpAndSettle();

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
  Future<void> clearSession({bool clearBaseUrl = false}) async {}

  @override
  Future<void> saveBaseUrl(String baseUrl) async {
    savedBaseUrl = baseUrl;
  }

  @override
  Future<UserSession?> restoreSession() async => null;

  @override
  Future<void> saveSession(UserSession session) async {}
}

class _FakeAuthFlowLauncher implements AuthFlowLauncher {
  String? lastBaseUrl;

  @override
  Future<void> startLogin(String baseUrl) async {
    lastBaseUrl = baseUrl;
  }
}
