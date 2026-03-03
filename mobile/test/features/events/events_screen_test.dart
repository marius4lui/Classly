import 'package:classly_mobile/features/events/domain/event.dart';
import 'package:classly_mobile/features/events/presentation/events_screen.dart';
import 'package:classly_mobile/features/events/providers/events_providers.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('cached events render in list form', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          eventsStreamProvider.overrideWith((ref) => Stream.value(_events)),
        ],
        child: const MaterialApp(home: EventsScreen()),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.byType(ListView), findsOneWidget);
    expect(find.text('Deutsch Analyse'), findsOneWidget);
    expect(find.text('Mathematik KA'), findsOneWidget);
  });

  testWidgets('event card shows type, title, subject, date', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          eventsStreamProvider.overrideWith((ref) => Stream.value(_events)),
        ],
        child: const MaterialApp(home: EventsScreen()),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('HA'), findsOneWidget);
    expect(find.text('Deutsch Analyse'), findsOneWidget);
    expect(find.text('Deutsch'), findsOneWidget);
    expect(find.text('04.03.2026'), findsOneWidget);
  });

  testWidgets('empty state renders when there are no events', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          eventsStreamProvider.overrideWith((ref) => Stream.value(const [])),
        ],
        child: const MaterialApp(home: EventsScreen()),
      ),
    );

    await tester.pump();
    await tester.pump(const Duration(milliseconds: 10));

    expect(find.text('Keine Events im Cache'), findsOneWidget);
  });
}

final _events = <Event>[
  Event(
    id: 'event-1',
    classId: 'class-1',
    type: 'HA',
    priority: 'HIGH',
    subjectId: 'subject-1',
    subjectName: 'Deutsch',
    title: 'Deutsch Analyse',
    date: DateTime.utc(2026, 3, 4),
    createdAt: DateTime.utc(2026, 3, 1, 8),
    updatedAt: DateTime.utc(2026, 3, 1, 10),
  ),
  Event(
    id: 'event-2',
    classId: 'class-1',
    type: 'KA',
    priority: 'HIGH',
    subjectId: 'subject-2',
    subjectName: 'Mathematik',
    title: 'Mathematik KA',
    date: DateTime.utc(2026, 3, 5),
    createdAt: DateTime.utc(2026, 3, 1, 8),
    updatedAt: DateTime.utc(2026, 3, 1, 10),
  ),
];
