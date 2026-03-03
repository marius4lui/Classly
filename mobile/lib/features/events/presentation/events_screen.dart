import 'package:classly_mobile/features/events/presentation/event_card.dart';
import 'package:classly_mobile/features/events/providers/events_providers.dart';
import 'package:classly_mobile/shared/widgets/state_views.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class EventsScreen extends ConsumerWidget {
  const EventsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventsAsync = ref.watch(eventsStreamProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Events')),
      body: eventsAsync.when(
        data: (events) {
          if (events.isEmpty) {
            return const EmptyStateView(
              title: 'Keine Events im Cache',
              message:
                  'Sobald deine Instanz Daten liefert, erscheinen sie hier.',
            );
          }

          return ListView.separated(
            padding: const EdgeInsets.all(24),
            itemCount: events.length,
            separatorBuilder: (context, index) => const SizedBox(height: 14),
            itemBuilder: (context, index) {
              return EventCard(event: events[index]);
            },
          );
        },
        error: (error, _) => ErrorStateView(
          title: 'Events konnten nicht geladen werden',
          message: error.toString(),
        ),
        loading: () => const LoadingStateView(),
      ),
    );
  }
}
