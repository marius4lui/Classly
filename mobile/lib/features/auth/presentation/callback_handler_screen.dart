import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/shared/widgets/state_views.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../domain/auth_repository.dart';
import '../providers/auth_providers.dart';

class CallbackHandlerScreen extends ConsumerStatefulWidget {
  const CallbackHandlerScreen({required this.callbackUri, super.key});

  final Uri callbackUri;

  @override
  ConsumerState<CallbackHandlerScreen> createState() =>
      _CallbackHandlerScreenState();
}

class _CallbackHandlerScreenState extends ConsumerState<CallbackHandlerScreen> {
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    Future.microtask(_handleCallback);
  }

  Future<void> _handleCallback() async {
    try {
      final bootstrap = ref.read(sessionBootstrapProvider);
      final session = await ref
          .read(authRepositoryProvider)
          .completeOAuthCallback(
            widget.callbackUri,
            baseUrl: bootstrap.baseUrl,
          );

      ref
          .read(sessionBootstrapControllerProvider.notifier)
          .setAuthenticated(session);

      if (!mounted) {
        return;
      }

      final router = GoRouter.maybeOf(context);
      if (router != null) {
        router.go('/calendar');
      }
    } on AuthFlowException catch (error) {
      if (!mounted) {
        return;
      }
      setState(() {
        _errorMessage = error.message;
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _errorMessage = 'Der OAuth-Flow konnte nicht abgeschlossen werden.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_errorMessage != null) {
      return Scaffold(
        body: ErrorStateView(
          title: 'Anmeldung fehlgeschlagen',
          message: _errorMessage!,
        ),
      );
    }

    return const Scaffold(
      body: LoadingStateView(label: 'Session wird eingerichtet'),
    );
  }
}
