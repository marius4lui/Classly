import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../domain/user_session.dart';

abstract class SessionStorage {
  Future<void> saveBaseUrl(String baseUrl);

  Future<String?> readBaseUrl();

  Future<void> saveSession(UserSession session);

  Future<UserSession?> readSession();

  Future<void> clearSession();
}

class SecureSessionStorage implements SessionStorage {
  SecureSessionStorage(this._storage);

  static const _baseUrlKey = 'classly.base_url';
  static const _sessionKey = 'classly.session';

  final FlutterSecureStorage _storage;

  @override
  Future<void> clearSession() async {
    await _storage.delete(key: _sessionKey);
  }

  @override
  Future<String?> readBaseUrl() {
    return _storage.read(key: _baseUrlKey);
  }

  @override
  Future<UserSession?> readSession() async {
    final raw = await _storage.read(key: _sessionKey);
    if (raw == null || raw.isEmpty) {
      return null;
    }

    return UserSession.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  @override
  Future<void> saveBaseUrl(String baseUrl) {
    return _storage.write(key: _baseUrlKey, value: baseUrl);
  }

  @override
  Future<void> saveSession(UserSession session) async {
    await saveBaseUrl(session.baseUrl);
    await _storage.write(key: _sessionKey, value: jsonEncode(session.toJson()));
  }
}

class InMemorySessionStorage implements SessionStorage {
  String? _baseUrl;
  UserSession? _session;

  @override
  Future<void> clearSession() async {
    _session = null;
  }

  @override
  Future<String?> readBaseUrl() async => _baseUrl;

  @override
  Future<UserSession?> readSession() async => _session;

  @override
  Future<void> saveBaseUrl(String baseUrl) async {
    _baseUrl = baseUrl;
  }

  @override
  Future<void> saveSession(UserSession session) async {
    _baseUrl = session.baseUrl;
    _session = session;
  }
}
