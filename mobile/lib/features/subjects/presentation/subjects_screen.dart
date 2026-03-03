import 'package:classly_mobile/features/events/providers/events_providers.dart';
import 'package:classly_mobile/shared/widgets/state_views.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SubjectsScreen extends ConsumerWidget {
  const SubjectsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final store = ref.watch(subjectsLocalStoreProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Faecher')),
      body: FutureBuilder(
        future: store.readAll(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const LoadingStateView();
          }

          final subjects = snapshot.data ?? const [];
          if (subjects.isEmpty) {
            return const EmptyStateView(
              title: 'Noch keine Faecher',
              message: 'Nach dem ersten Sync findest du hier deine Fachliste.',
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(24),
            itemCount: subjects.length,
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final subject = subjects[index];
              return Card(
                child: ListTile(
                  title: Text(subject.name),
                  subtitle: Text(subject.color ?? 'Keine Farbe'),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
