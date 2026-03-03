import 'package:classly_mobile/features/events/domain/event.dart';
import 'package:classly_mobile/features/events/presentation/event_card.dart';
import 'package:flutter/material.dart';

class EventDetailScreen extends StatelessWidget {
  const EventDetailScreen({required this.event, super.key});

  final Event event;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Event')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          EventCard(event: event),
          const SizedBox(height: 20),
          Text('Fach', style: theme.textTheme.labelMedium),
          const SizedBox(height: 6),
          Text(event.subjectName, style: theme.textTheme.titleMedium),
          const SizedBox(height: 16),
          Text('Termin', style: theme.textTheme.labelMedium),
          const SizedBox(height: 6),
          Text(
            EventCard.formatDate(event.date),
            style: theme.textTheme.titleMedium,
          ),
          if (event.topics.isNotEmpty) ...[
            const SizedBox(height: 20),
            Text('Themen', style: theme.textTheme.labelMedium),
            const SizedBox(height: 8),
            ...event.topics.map(
              (topic) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text(topic.content, style: theme.textTheme.bodyLarge),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
