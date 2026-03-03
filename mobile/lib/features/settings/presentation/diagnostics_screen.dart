import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/features/events/providers/events_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DiagnosticsScreen extends ConsumerWidget {
  const DiagnosticsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final bootstrap = ref.watch(sessionBootstrapProvider);
    final eventsStore = ref.watch(eventsLocalStoreProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Diagnostics')),
      body: FutureBuilder(
        future: eventsStore.readLastSyncAt(),
        builder: (context, snapshot) {
          final lastSync = snapshot.data;
          return ListView(
            padding: const EdgeInsets.all(24),
            children: [
              _DiagnosticRow(
                label: 'Base URL',
                value: bootstrap.baseUrl ?? 'Nicht gesetzt',
              ),
              const SizedBox(height: 12),
              _DiagnosticRow(
                label: 'Letzter Sync',
                value: lastSync == null
                    ? 'Noch kein Sync'
                    : _formatUtc(lastSync),
              ),
            ],
          );
        },
      ),
    );
  }

  String _formatUtc(DateTime value) {
    final date = value.toUtc();
    final year = date.year.toString().padLeft(4, '0');
    final month = date.month.toString().padLeft(2, '0');
    final day = date.day.toString().padLeft(2, '0');
    final hour = date.hour.toString().padLeft(2, '0');
    final minute = date.minute.toString().padLeft(2, '0');
    return '$year-$month-$day $hour:$minute UTC';
  }
}

class _DiagnosticRow extends StatelessWidget {
  const _DiagnosticRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: Theme.of(context).textTheme.labelMedium),
            const SizedBox(height: 6),
            SelectableText(
              value,
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ],
        ),
      ),
    );
  }
}
