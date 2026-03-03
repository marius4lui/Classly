import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/shared/widgets/primary_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bootstrap = ref.watch(sessionBootstrapProvider);
    final baseUrl = bootstrap.baseUrl ?? 'Noch keine Instanz ausgewaehlt';
    final canLogin = bootstrap.baseUrl != null;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Anmeldung')),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 440),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Mit Classly anmelden',
                        style: theme.textTheme.headlineMedium,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Die App verwendet den Classly OAuth-Flow im System-Browser. '
                        'Deine aktive Instanz ist unten hinterlegt.',
                        style: theme.textTheme.bodyMedium,
                      ),
                      const SizedBox(height: 24),
                      Text(
                        'Aktive Instanz',
                        style: theme.textTheme.labelMedium,
                      ),
                      const SizedBox(height: 6),
                      SelectableText(
                        baseUrl,
                        style: theme.textTheme.titleMedium,
                      ),
                      const SizedBox(height: 24),
                      PrimaryButton(
                        label: 'OAuth im Browser starten',
                        onPressed: canLogin ? () {} : null,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
