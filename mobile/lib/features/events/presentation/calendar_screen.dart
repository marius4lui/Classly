import 'package:classly_mobile/features/events/presentation/event_card.dart';
import 'package:classly_mobile/features/events/providers/events_providers.dart';
import 'package:classly_mobile/shared/widgets/state_views.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class CalendarScreen extends ConsumerWidget {
  const CalendarScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventsAsync = ref.watch(eventsStreamProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Kalender')),
      body: eventsAsync.when(
        data: (events) {
          if (events.isEmpty) {
            return const EmptyStateView(
              title: 'Kalender ist leer',
              message:
                  'Nach dem ersten Sync erscheinen hier deine naechsten Termine.',
            );
          }

          final grouped = <String, List<String>>{};
          for (final event in events) {
            final key = EventCard.formatDate(event.date);
            grouped.putIfAbsent(key, () => <String>[]).add(event.title);
          }

          return ListView(
            padding: const EdgeInsets.all(24),
            children: grouped.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(18),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          entry.key,
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 10),
                        ...entry.value.map(
                          (title) => Padding(
                            padding: const EdgeInsets.only(bottom: 6),
                            child: Text(title),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
          );
        },
        error: (error, _) => ErrorStateView(
          title: 'Kalender konnte nicht geladen werden',
          message: error.toString(),
        ),
        loading: () => const LoadingStateView(),
      ),
    );
  }
}
