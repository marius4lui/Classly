import 'package:classly_mobile/features/auth/application/logout_use_case.dart';
import 'package:classly_mobile/features/settings/presentation/diagnostics_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final logoutUseCase = ref.watch(logoutUseCaseProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Einstellungen')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          Card(
            child: Column(
              children: [
                ListTile(
                  title: const Text('Logout'),
                  subtitle: const Text('Session beenden, Instanz behalten'),
                  onTap: logoutUseCase.logout,
                ),
                const Divider(height: 1),
                ListTile(
                  title: const Text('Instanz wechseln'),
                  subtitle: const Text('Session und aktive Base URL entfernen'),
                  onTap: logoutUseCase.switchInstance,
                ),
                const Divider(height: 1),
                ListTile(
                  title: const Text('Cache leeren'),
                  subtitle: const Text('Lokale Event- und Fachdaten entfernen'),
                  onTap: logoutUseCase.clearCache,
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              title: const Text('Diagnostics'),
              subtitle: const Text('Sync-Zeit und aktive Instanz anzeigen'),
              onTap: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const DiagnosticsScreen()),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
