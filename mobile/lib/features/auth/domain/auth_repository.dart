import 'package:flutter_riverpod/flutter_riverpod.dart';

abstract class AuthRepository {
  Future<String?> getSavedBaseUrl();

  Future<void> saveBaseUrl(String baseUrl);

  Uri buildAuthorizeUri({required String baseUrl});
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  throw UnimplementedError('AuthRepository provider must be overridden.');
});
