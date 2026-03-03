import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../data/auth_api.dart';
import '../data/auth_repository_impl.dart';
import '../data/session_storage.dart';
import '../domain/auth_repository.dart';

final dioProvider = Provider<Dio>((ref) => Dio());

final sessionStorageProvider = Provider<SessionStorage>((ref) {
  return SecureSessionStorage(const FlutterSecureStorage());
});

final authApiProvider = Provider<AuthApi>((ref) {
  return DioAuthApi(dio: ref.watch(dioProvider));
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepositoryImpl(
    authApi: ref.watch(authApiProvider),
    sessionStorage: ref.watch(sessionStorageProvider),
  );
});
