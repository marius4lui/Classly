import 'package:classly_mobile/features/events/domain/event.dart';
import 'package:classly_mobile/features/events/presentation/search_controller.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  final events = <Event>[
    Event(
      id: 'event-1',
      classId: 'class-1',
      type: 'HA',
      priority: 'HIGH',
      subjectId: 'subject-1',
      subjectName: 'Deutsch',
      title: 'Analyse schreiben',
      date: DateTime.utc(2026, 3, 4),
      createdAt: DateTime.utc(2026, 3, 1),
      updatedAt: DateTime.utc(2026, 3, 1, 1),
    ),
    Event(
      id: 'event-2',
      classId: 'class-1',
      type: 'KA',
      priority: 'HIGH',
      subjectId: 'subject-2',
      subjectName: 'Mathematik',
      title: 'Lineare Funktionen',
      date: DateTime.utc(2026, 3, 5),
      createdAt: DateTime.utc(2026, 3, 1),
      updatedAt: DateTime.utc(2026, 3, 1, 1),
    ),
  ];

  test('filter by event type', () {
    final controller = EventSearchController(
      const EventSearchState(selectedType: 'KA'),
    );

    final filtered = controller.apply(events);

    expect(filtered.single.id, 'event-2');
  });

  test('filter by subject', () {
    final controller = EventSearchController(
      const EventSearchState(selectedSubjectId: 'subject-1'),
    );

    final filtered = controller.apply(events);

    expect(filtered.single.subjectName, 'Deutsch');
  });

  test('search matches title and subject name', () {
    final titleController = EventSearchController(
      const EventSearchState(query: 'analyse'),
    );
    final subjectController = EventSearchController(
      const EventSearchState(query: 'mathe'),
    );

    expect(titleController.apply(events).single.id, 'event-1');
    expect(subjectController.apply(events).single.id, 'event-2');
  });
}
