import 'package:classly_mobile/features/auth/data/auth_api.dart';
import 'package:classly_mobile/features/auth/data/auth_repository_impl.dart';
import 'package:classly_mobile/features/auth/data/session_storage.dart';
import 'package:classly_mobile/features/auth/domain/auth_repository.dart';
import 'package:classly_mobile/features/auth/domain/user_session.dart';
import 'package:classly_mobile/features/auth/presentation/callback_handler_screen.dart';
import 'package:classly_mobile/features/auth/providers/auth_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('callback parses code', () async {
    final storage = InMemorySessionStorage();
    final api = _FakeAuthApi();
    final repository = AuthRepositoryImpl(
      authApi: api,
      sessionStorage: storage,
    );

    await repository.completeOAuthCallback(
      Uri.parse('classly://auth/callback?code=abc123'),
      baseUrl: 'https://classly.site',
    );

    expect(api.exchangedCode, 'abc123');
  });

  test('token exchange success stores session', () async {
    final storage = InMemorySessionStorage();
    final api = _FakeAuthApi();
    final repository = AuthRepositoryImpl(
      authApi: api,
      sessionStorage: storage,
    );

    final session = await repository.completeOAuthCallback(
      Uri.parse('classly://auth/callback?code=abc123'),
      baseUrl: 'https://classly.site',
    );

    final restored = await storage.readSession();

    expect(session.accessToken, 'token-123');
    expect(restored?.accessToken, 'token-123');
    expect(restored?.userInfo?.name, 'Max Mustermann');
  });

  testWidgets('invalid callback yields error state', (tester) async {
    final repository = _ThrowingAuthRepository();
    final container = ProviderContainer(
      overrides: [authRepositoryProvider.overrideWithValue(repository)],
    );
    addTearDown(container.dispose);

    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: MaterialApp(
          home: CallbackHandlerScreen(
            callbackUri: Uri.parse(
              'classly://auth/callback?error=access_denied',
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Anmeldung fehlgeschlagen'), findsOneWidget);
  });
}

class _FakeAuthApi implements AuthApi {
  String? exchangedCode;

  @override
  Future<UserInfo> fetchUserInfo({
    required String accessToken,
    required String baseUrl,
  }) async {
    return const UserInfo(
      id: 'user-1',
      name: 'Max Mustermann',
      role: 'member',
      classId: 'class-1',
      className: '10b',
      email: 'max@example.com',
      isRegistered: true,
    );
  }

  @override
  Future<OAuthTokenResponse> exchangeAuthorizationCode({
    required String baseUrl,
    required String code,
  }) async {
    exchangedCode = code;
    return const OAuthTokenResponse(
      accessToken: 'token-123',
      tokenType: 'bearer',
      scope: 'read:events',
      classId: 'class-1',
    );
  }
}

class _ThrowingAuthRepository implements AuthRepository {
  @override
  Uri buildAuthorizeUri({required String baseUrl}) {
    return Uri.parse(baseUrl);
  }

  @override
  Future<void> clearSession() async {}

  @override
  Future<UserSession> completeOAuthCallback(
    Uri callbackUri, {
    String? baseUrl,
  }) {
    throw const AuthFlowException('invalid callback');
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
