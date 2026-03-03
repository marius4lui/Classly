import 'package:classly_mobile/features/auth/domain/user_session.dart';

abstract class AuthRepository {
  Future<String?> getSavedBaseUrl();

  Future<void> saveBaseUrl(String baseUrl);

  Uri buildAuthorizeUri({required String baseUrl});

  Future<UserSession> completeOAuthCallback(Uri callbackUri, {String? baseUrl});

  Future<void> saveSession(UserSession session);

  Future<UserSession?> restoreSession();

  Future<void> clearSession({bool clearBaseUrl = false});
}

class AuthFlowException implements Exception {
  const AuthFlowException(this.message);

  final String message;

  @override
  String toString() => message;
}
