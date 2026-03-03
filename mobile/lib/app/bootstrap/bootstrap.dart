import 'package:flutter_riverpod/flutter_riverpod.dart';

enum SessionStatus { loading, unauthenticated, authenticated }

class SessionBootstrapState {
  const SessionBootstrapState._(this.status);

  const SessionBootstrapState.loading() : this._(SessionStatus.loading);

  const SessionBootstrapState.unauthenticated()
    : this._(SessionStatus.unauthenticated);

  const SessionBootstrapState.authenticated()
    : this._(SessionStatus.authenticated);

  final SessionStatus status;

  bool get isAuthenticated => status == SessionStatus.authenticated;
  bool get isLoading => status == SessionStatus.loading;
}

final sessionBootstrapProvider = Provider<SessionBootstrapState>((ref) {
  return const SessionBootstrapState.unauthenticated();
});
