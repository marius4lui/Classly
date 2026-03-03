import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/features/auth/presentation/callback_handler_screen.dart';
import 'package:classly_mobile/features/auth/presentation/instance_select_screen.dart';
import 'package:classly_mobile/features/auth/presentation/login_screen.dart';
import 'package:classly_mobile/features/auth/presentation/session_gate.dart';
import 'package:classly_mobile/features/events/presentation/calendar_screen.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final session = ref.watch(sessionBootstrapProvider);

  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (context, state) => const SessionGate()),
      GoRoute(
        path: '/instance',
        builder: (context, state) => const InstanceSelectScreen(),
      ),
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(
        path: '/auth/callback',
        builder: (context, state) =>
            CallbackHandlerScreen(callbackUri: state.uri),
      ),
      GoRoute(
        path: '/calendar',
        builder: (context, state) => const CalendarScreen(),
      ),
    ],
    redirect: (context, state) {
      final isRoot = state.matchedLocation == '/';
      final isInstance = state.matchedLocation == '/instance';
      final isCalendar = state.matchedLocation == '/calendar';

      if (session.isLoading) {
        return isRoot ? null : '/';
      }

      if (isRoot) {
        return session.isAuthenticated ? '/calendar' : '/login';
      }

      if (!session.isAuthenticated && isCalendar) {
        return '/login';
      }

      if (session.isAuthenticated && isInstance) {
        return '/calendar';
      }

      return null;
    },
  );
});
