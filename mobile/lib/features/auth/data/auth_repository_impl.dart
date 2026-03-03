import 'package:classly_mobile/features/auth/domain/auth_repository.dart';
import 'package:classly_mobile/features/auth/domain/user_session.dart';

import 'auth_api.dart';
import 'session_storage.dart';

class AuthRepositoryImpl implements AuthRepository {
  AuthRepositoryImpl({
    required AuthApi authApi,
    required SessionStorage sessionStorage,
  }) : _authApi = authApi,
       _sessionStorage = sessionStorage;

  final AuthApi _authApi;
  final SessionStorage _sessionStorage;

  @override
  Uri buildAuthorizeUri({required String baseUrl}) {
    return Uri.parse('$baseUrl/api/oauth/authorize').replace(
      queryParameters: {
        'client_id': DioAuthApi.clientId,
        'redirect_uri': DioAuthApi.redirectUri,
        'scope': DioAuthApi.scope,
        'response_type': 'code',
      },
    );
  }

  @override
  Future<void> clearSession() {
    return _sessionStorage.clearSession();
  }

  @override
  Future<UserSession> completeOAuthCallback(
    Uri callbackUri, {
    String? baseUrl,
  }) async {
    final code = callbackUri.queryParameters['code'];
    final callbackError = callbackUri.queryParameters['error'];
    final callbackErrorDescription =
        callbackUri.queryParameters['error_description'];

    if (callbackError != null) {
      throw AuthFlowException(callbackErrorDescription ?? callbackError);
    }

    if (code == null || code.isEmpty) {
      throw const AuthFlowException('Authorization code fehlt im Callback.');
    }

    final resolvedBaseUrl = baseUrl ?? await getSavedBaseUrl();
    if (resolvedBaseUrl == null || resolvedBaseUrl.isEmpty) {
      throw const AuthFlowException('Keine Classly-Instanz ausgewaehlt.');
    }

    final token = await _authApi.exchangeAuthorizationCode(
      baseUrl: resolvedBaseUrl,
      code: code,
    );
    final userInfo = await _authApi.fetchUserInfo(
      accessToken: token.accessToken,
      baseUrl: resolvedBaseUrl,
    );

    final session = UserSession(
      baseUrl: resolvedBaseUrl,
      accessToken: token.accessToken,
      scope: token.scope,
      classId: token.classId,
      userInfo: userInfo,
    );

    await saveSession(session);
    return session;
  }

  @override
  Future<String?> getSavedBaseUrl() {
    return _sessionStorage.readBaseUrl();
  }

  @override
  Future<UserSession?> restoreSession() {
    return _sessionStorage.readSession();
  }

  @override
  Future<void> saveBaseUrl(String baseUrl) {
    return _sessionStorage.saveBaseUrl(baseUrl);
  }

  @override
  Future<void> saveSession(UserSession session) {
    return _sessionStorage.saveSession(session);
  }
}
