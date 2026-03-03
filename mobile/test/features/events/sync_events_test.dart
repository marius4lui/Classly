import 'package:classly_mobile/features/auth/data/session_storage.dart';
import 'package:classly_mobile/features/auth/domain/user_session.dart';
import 'package:classly_mobile/features/events/data/event_dto.dart';
import 'package:classly_mobile/features/events/data/events_local_store.dart';
import 'package:classly_mobile/features/events/data/events_repository_impl.dart';
import 'package:classly_mobile/features/subjects/data/subject_dto.dart';
import 'package:classly_mobile/features/subjects/data/subjects_local_store.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('initial sync stores remote events', () async {
    final sessionStorage = InMemorySessionStorage();
    final eventsStore = InMemoryEventsLocalStore();
    final subjectsStore = InMemorySubjectsLocalStore();
    final remote = _FakeEventsRemoteSource(
      eventsBySync: [
        [_eventDto(title: 'Mathe Hausaufgaben')],
      ],
      subjects: [
        const SubjectDto(id: 'subject-1', name: 'Mathematik', color: '#2454E6'),
      ],
    );

    await sessionStorage.saveSession(_session());

    final repository = EventsRepositoryImpl(
      remoteSource: remote,
      eventsLocalStore: eventsStore,
      subjectsLocalStore: subjectsStore,
      sessionStorage: sessionStorage,
    );

    await repository.syncEvents();

    expect((await eventsStore.readAll()).single.title, 'Mathe Hausaufgaben');
    expect((await subjectsStore.readAll()).single.name, 'Mathematik');
  });

  test('delta sync upserts changed events', () async {
    final sessionStorage = InMemorySessionStorage();
    final eventsStore = InMemoryEventsLocalStore();
    final subjectsStore = InMemorySubjectsLocalStore();
    final remote = _FakeEventsRemoteSource(
      eventsBySync: [
        [
          _eventDto(
            title: 'Mathe alt',
            updatedAt: DateTime.utc(2026, 3, 1, 10),
          ),
        ],
        [
          _eventDto(
            title: 'Mathe aktualisiert',
            updatedAt: DateTime.utc(2026, 3, 2, 12),
          ),
        ],
      ],
      subjects: const [],
    );

    await sessionStorage.saveSession(_session());

    final repository = EventsRepositoryImpl(
      remoteSource: remote,
      eventsLocalStore: eventsStore,
      subjectsLocalStore: subjectsStore,
      sessionStorage: sessionStorage,
    );

    await repository.syncEvents();
    await repository.syncEvents();

    expect((await eventsStore.readAll()).single.title, 'Mathe aktualisiert');
    expect(remote.lastUpdatedSince, DateTime.utc(2026, 3, 1, 10));
  });

  test('cached events are returned before refresh completes', () async {
    final sessionStorage = InMemorySessionStorage();
    final eventsStore = InMemoryEventsLocalStore();
    final subjectsStore = InMemorySubjectsLocalStore();
    final remote = _FakeEventsRemoteSource(
      delay: const Duration(milliseconds: 80),
      eventsBySync: [
        [_eventDto(title: 'Neu vom Server')],
      ],
      subjects: const [],
    );

    await sessionStorage.saveSession(_session());
    await eventsStore.upsertAll([_eventDto(title: 'Aus Cache').toDomain()]);

    final repository = EventsRepositoryImpl(
      remoteSource: remote,
      eventsLocalStore: eventsStore,
      subjectsLocalStore: subjectsStore,
      sessionStorage: sessionStorage,
    );

    final emissions = <List<String>>[];
    final subscription = repository.watchEvents().listen((events) {
      emissions.add(events.map((event) => event.title).toList());
    });

    await Future<void>.delayed(const Duration(milliseconds: 20));
    expect(emissions.first, ['Aus Cache']);

    await Future<void>.delayed(const Duration(milliseconds: 120));
    expect(emissions.last, ['Neu vom Server']);

    await subscription.cancel();
  });
}

class _FakeEventsRemoteSource implements EventsRemoteSource {
  _FakeEventsRemoteSource({
    required this.eventsBySync,
    required this.subjects,
    this.delay = Duration.zero,
  });

  final Duration delay;
  final List<List<EventDto>> eventsBySync;
  final List<SubjectDto> subjects;
  int _syncCount = 0;
  DateTime? lastUpdatedSince;

  @override
  Future<List<EventDto>> fetchEvents({
    required UserSession session,
    DateTime? updatedSince,
  }) async {
    lastUpdatedSince = updatedSince;
    await Future<void>.delayed(delay);

    final index = _syncCount.clamp(0, eventsBySync.length - 1);
    _syncCount++;
    return eventsBySync[index];
  }

  @override
  Future<List<SubjectDto>> fetchSubjects({required UserSession session}) async {
    return subjects;
  }
}

UserSession _session() {
  return const UserSession(
    baseUrl: 'https://classly.site',
    accessToken: 'token-123',
    scope: 'read:events',
  );
}

EventDto _eventDto({required String title, DateTime? updatedAt}) {
  return EventDto(
    id: 'event-1',
    classId: 'class-1',
    type: 'HA',
    priority: 'HIGH',
    subjectId: 'subject-1',
    subjectName: 'Mathematik',
    title: title,
    date: DateTime.utc(2026, 3, 4),
    createdAt: DateTime.utc(2026, 3, 1, 9),
    updatedAt: updatedAt ?? DateTime.utc(2026, 3, 1, 10),
    authorId: 'user-1',
    topics: const [],
    links: const [],
  );
}
