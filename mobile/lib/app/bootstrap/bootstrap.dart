import 'package:classly_mobile/features/auth/domain/user_session.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

enum SessionStatus { loading, unauthenticated, authenticated }

const defaultClasslyBaseUrl = 'https://classly.site';

class SessionBootstrapState {
  const SessionBootstrapState._({
    required this.status,
    this.baseUrl,
    this.session,
  });

  const SessionBootstrapState.loading({String? baseUrl, UserSession? session})
    : this._(status: SessionStatus.loading, baseUrl: baseUrl, session: session);

  const SessionBootstrapState.unauthenticated({
    String? baseUrl,
    UserSession? session,
  }) : this._(
         status: SessionStatus.unauthenticated,
         baseUrl: baseUrl,
         session: session,
       );

  const SessionBootstrapState.authenticated({
    String? baseUrl,
    UserSession? session,
  }) : this._(
         status: SessionStatus.authenticated,
         baseUrl: baseUrl,
         session: session,
       );

  final SessionStatus status;
  final String? baseUrl;
  final UserSession? session;

  bool get isAuthenticated => status == SessionStatus.authenticated;
  bool get isLoading => status == SessionStatus.loading;

  SessionBootstrapState copyWith({
    SessionStatus? status,
    String? baseUrl,
    UserSession? session,
    bool clearSession = false,
  }) {
    return SessionBootstrapState._(
      status: status ?? this.status,
      baseUrl: baseUrl ?? this.baseUrl,
      session: clearSession ? null : session ?? this.session,
    );
  }
}

class SessionBootstrapController extends Notifier<SessionBootstrapState> {
  @override
  SessionBootstrapState build() {
    return const SessionBootstrapState.unauthenticated(
      baseUrl: defaultClasslyBaseUrl,
    );
  }

  void setBaseUrl(String baseUrl) {
    state = state.copyWith(baseUrl: baseUrl);
  }

  void setLoading() {
    state = SessionBootstrapState.loading(
      baseUrl: state.baseUrl,
      session: state.session,
    );
  }

  void setAuthenticated(UserSession session) {
    state = SessionBootstrapState.authenticated(
      baseUrl: session.baseUrl,
      session: session,
    );
  }

  void clearSession({bool clearBaseUrl = false}) {
    state = SessionBootstrapState.unauthenticated(
      baseUrl: clearBaseUrl ? defaultClasslyBaseUrl : state.baseUrl,
    );
  }
}

final sessionBootstrapControllerProvider =
    NotifierProvider<SessionBootstrapController, SessionBootstrapState>(
      SessionBootstrapController.new,
    );

final sessionBootstrapProvider = Provider<SessionBootstrapState>((ref) {
  return ref.watch(sessionBootstrapControllerProvider);
});
