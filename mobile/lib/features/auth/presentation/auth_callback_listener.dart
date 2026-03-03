import 'dart:async';

import 'package:app_links/app_links.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

class AuthCallbackListener extends StatefulWidget {
  const AuthCallbackListener({required this.child, super.key});

  final Widget child;

  @override
  State<AuthCallbackListener> createState() => _AuthCallbackListenerState();
}

class _AuthCallbackListenerState extends State<AuthCallbackListener> {
  StreamSubscription<Uri>? _subscription;
  bool _initialHandled = false;

  @override
  void initState() {
    super.initState();
    Future.microtask(() async {
      try {
        final appLinks = AppLinks();
        final initialUri = await appLinks.getInitialLink();
        if (initialUri != null) {
          _handleUri(initialUri);
        }

        if (!mounted) {
          return;
        }

        _subscription = appLinks.uriLinkStream.listen(_handleUri);
      } on MissingPluginException {
        // Ignore while the plugin is unavailable in tests or unsupported builds.
      } on PlatformException {
        // Ignore transient channel/bootstrap issues and keep the app usable.
      }
      _initialHandled = true;
      if (mounted) {
        setState(() {});
      }
    });
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }

  void _handleUri(Uri uri) {
    if (!_isAuthCallback(uri) || !mounted) {
      return;
    }

    final router = GoRouter.maybeOf(context);
    if (router == null) {
      return;
    }

    final target = Uri(
      path: '/auth/callback',
      queryParameters: uri.queryParameters.isEmpty ? null : uri.queryParameters,
    ).toString();

    router.go(target);
  }

  bool _isAuthCallback(Uri uri) {
    return uri.scheme == 'classly' &&
        uri.host == 'auth' &&
        uri.path == '/callback';
  }

  @override
  Widget build(BuildContext context) {
    if (!_initialHandled) {
      return widget.child;
    }

    return widget.child;
  }
}
