import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/features/auth/presentation/session_gate.dart';
import 'package:flutter/material.dart';
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
        builder: (context, state) =>
            const _RoutePlaceholderScreen(title: 'Instanz waehlen'),
      ),
      GoRoute(
        path: '/calendar',
        builder: (context, state) =>
            const _RoutePlaceholderScreen(title: 'Kalender'),
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
        return session.isAuthenticated ? '/calendar' : '/instance';
      }

      if (!session.isAuthenticated && isCalendar) {
        return '/instance';
      }

      if (session.isAuthenticated && isInstance) {
        return '/calendar';
      }

      return null;
    },
  );
});

class _RoutePlaceholderScreen extends StatelessWidget {
  const _RoutePlaceholderScreen({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: Center(child: Text(title)));
  }
}
