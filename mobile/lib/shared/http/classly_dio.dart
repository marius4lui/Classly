import 'package:classly_mobile/features/auth/data/session_storage.dart';
import 'package:classly_mobile/features/auth/providers/auth_providers.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AuthHeaderInterceptor extends Interceptor {
  AuthHeaderInterceptor(this._sessionStorage);

  final SessionStorage _sessionStorage;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final session = await _sessionStorage.readSession();
    if (session?.accessToken != null && session!.accessToken!.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer ${session.accessToken}';
    }

    handler.next(options);
  }
}

final classlyDioProvider = Provider<Dio>((ref) {
  final dio = Dio();
  dio.interceptors.add(
    AuthHeaderInterceptor(ref.watch(sessionStorageProvider)),
  );
  return dio;
});
