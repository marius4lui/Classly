import 'package:dio/dio.dart';

import '../domain/user_session.dart';

abstract class AuthApi {
  Future<OAuthTokenResponse> exchangeAuthorizationCode({
    required String baseUrl,
    required String code,
  });

  Future<UserInfo> fetchUserInfo({
    required String accessToken,
    required String baseUrl,
  });
}

class DioAuthApi implements AuthApi {
  DioAuthApi({required Dio dio}) : _dio = dio;

  static const String clientId = String.fromEnvironment(
    'CLASSLY_OAUTH_CLIENT_ID',
    defaultValue: 'classly-mobile',
  );
  static const String redirectUri = String.fromEnvironment(
    'CLASSLY_OAUTH_REDIRECT_URI',
    defaultValue: 'classly://auth/callback',
  );
  static const String scope = String.fromEnvironment(
    'CLASSLY_OAUTH_SCOPE',
    defaultValue: 'read:events',
  );
  static const String clientSecret = String.fromEnvironment(
    'CLASSLY_OAUTH_CLIENT_SECRET',
    defaultValue: '',
  );

  final Dio _dio;

  @override
  Future<OAuthTokenResponse> exchangeAuthorizationCode({
    required String baseUrl,
    required String code,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '$baseUrl/api/oauth/token',
      data: {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': clientId,
        'redirect_uri': redirectUri,
        if (clientSecret.isNotEmpty) 'client_secret': clientSecret,
      },
      options: Options(contentType: Headers.formUrlEncodedContentType),
    );

    return OAuthTokenResponse.fromJson(response.data ?? const {});
  }

  @override
  Future<UserInfo> fetchUserInfo({
    required String accessToken,
    required String baseUrl,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '$baseUrl/api/oauth/userinfo',
      options: Options(headers: {'Authorization': 'Bearer $accessToken'}),
    );

    return UserInfo.fromJson(response.data ?? const {});
  }
}

class OAuthTokenResponse {
  const OAuthTokenResponse({
    required this.accessToken,
    required this.tokenType,
    this.expiresAt,
    this.scope,
    this.classId,
  });

  final String accessToken;
  final String tokenType;
  final String? expiresAt;
  final String? scope;
  final String? classId;

  factory OAuthTokenResponse.fromJson(Map<String, dynamic> json) {
    return OAuthTokenResponse(
      accessToken: json['access_token'] as String? ?? '',
      tokenType: json['token_type'] as String? ?? 'bearer',
      expiresAt: json['expires_at'] as String?,
      scope: json['scope'] as String? ?? json['scopes'] as String?,
      classId: json['class_id'] as String?,
    );
  }
}
