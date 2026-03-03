import 'package:classly_mobile/app/routing/app_router.dart';
import 'package:classly_mobile/app/theme/app_theme.dart';
import 'package:classly_mobile/features/auth/presentation/auth_callback_listener.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ClasslyApp extends ConsumerWidget {
  const ClasslyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'Classly',
      routerConfig: router,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      builder: (context, child) {
        if (child == null) {
          return const SizedBox.shrink();
        }

        return AuthCallbackListener(child: child);
      },
    );
  }
}
