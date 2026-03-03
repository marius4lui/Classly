import 'package:classly_mobile/features/events/data/event_dto.dart';
import 'package:classly_mobile/features/subjects/data/subject_dto.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('api event json maps into domain event', () {
    final dto = EventDto.fromJson({
      'id': 'event-1',
      'class_id': 'class-1',
      'type': 'HA',
      'priority': 'HIGH',
      'subject_id': 'subject-1',
      'subject_name': 'Mathematik',
      'title': 'S. 42 Nr. 1-5',
      'date': '2026-03-04T00:00:00Z',
      'created_at': '2026-03-01T10:00:00Z',
      'updated_at': '2026-03-02T12:00:00Z',
      'author_id': 'user-1',
      'topics': [
        {
          'id': 'topic-1',
          'topic_type': 'TASK',
          'content': 'Kapitel 2',
          'count': null,
          'pages': '42-45',
          'order': 1,
          'parent_id': null,
        },
      ],
      'links': [
        {'id': 'link-1', 'url': 'https://example.com', 'label': 'Arbeitsblatt'},
      ],
    });

    final event = dto.toDomain();

    expect(event.id, 'event-1');
    expect(event.type, 'HA');
    expect(event.subjectName, 'Mathematik');
    expect(event.topics.single.content, 'Kapitel 2');
    expect(event.links.single.url, 'https://example.com');
  });

  test('api subject json maps into domain subject', () {
    final dto = SubjectDto.fromJson({
      'id': 'subject-1',
      'name': 'Mathematik',
      'color': '#2454E6',
    });

    final subject = dto.toDomain();

    expect(subject.id, 'subject-1');
    expect(subject.name, 'Mathematik');
    expect(subject.color, '#2454E6');
  });
}
