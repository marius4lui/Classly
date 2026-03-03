import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/features/auth/providers/auth_providers.dart';
import 'package:classly_mobile/features/events/providers/events_providers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LogoutUseCase {
  const LogoutUseCase(this._ref);

  final Ref _ref;

  Future<void> logout() async {
    await _ref.read(authRepositoryProvider).clearSession();
    _ref.read(sessionBootstrapControllerProvider.notifier).clearSession();
  }

  Future<void> switchInstance() async {
    await _clearCaches();
    await _ref.read(authRepositoryProvider).clearSession(clearBaseUrl: true);
    _ref
        .read(sessionBootstrapControllerProvider.notifier)
        .clearSession(clearBaseUrl: true);
  }

  Future<void> clearCache() async {
    await _clearCaches();
  }

  Future<void> _clearCaches() async {
    await _ref.read(eventsLocalStoreProvider).clear();
    await _ref.read(subjectsLocalStoreProvider).clear();
  }
}

final logoutUseCaseProvider = Provider<LogoutUseCase>((ref) {
  return LogoutUseCase(ref);
});
