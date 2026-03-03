import 'dart:async';

import 'package:classly_mobile/features/auth/data/session_storage.dart';
import 'package:classly_mobile/features/auth/domain/user_session.dart';
import 'package:classly_mobile/features/events/data/event_dto.dart';
import 'package:classly_mobile/features/events/data/events_local_store.dart';
import 'package:classly_mobile/features/events/domain/event.dart';
import 'package:classly_mobile/features/events/domain/events_repository.dart';
import 'package:classly_mobile/features/subjects/data/subject_dto.dart';
import 'package:classly_mobile/features/subjects/data/subjects_local_store.dart';
import 'package:dio/dio.dart';

class EventsRepositoryImpl implements EventsRepository {
  EventsRepositoryImpl({
    required EventsRemoteSource remoteSource,
    required EventsLocalStore eventsLocalStore,
    required SubjectsLocalStore subjectsLocalStore,
    required SessionStorage sessionStorage,
  }) : _remoteSource = remoteSource,
       _eventsLocalStore = eventsLocalStore,
       _subjectsLocalStore = subjectsLocalStore,
       _sessionStorage = sessionStorage;

  final EventsRemoteSource _remoteSource;
  final EventsLocalStore _eventsLocalStore;
  final SubjectsLocalStore _subjectsLocalStore;
  final SessionStorage _sessionStorage;

  @override
  Future<void> syncEvents() async {
    final session = await _sessionStorage.readSession();
    if (session == null || !session.isAuthenticated) {
      throw StateError('No authenticated session available for sync.');
    }

    final lastSyncAt = await _eventsLocalStore.readLastSyncAt();
    if (lastSyncAt == null) {
      final subjects = await _remoteSource.fetchSubjects(session: session);
      await _subjectsLocalStore.upsertAll(
        subjects.map((subject) => subject.toDomain()).toList(),
      );
    }

    final eventDtos = await _remoteSource.fetchEvents(
      session: session,
      updatedSince: lastSyncAt,
    );
    final events = eventDtos.map((event) => event.toDomain()).toList();

    if (events.isNotEmpty) {
      await _eventsLocalStore.upsertAll(events);
      final newestUpdate = events
          .map((event) => event.updatedAt.toUtc())
          .reduce((left, right) => left.isAfter(right) ? left : right);
      await _eventsLocalStore.saveLastSyncAt(newestUpdate);
    } else if (lastSyncAt == null) {
      await _eventsLocalStore.saveLastSyncAt(DateTime.now().toUtc());
    }
  }

  @override
  Stream<List<Event>> watchEvents() {
    return Stream.multi((controller) async {
      controller.add(await _eventsLocalStore.readAll());
      final subscription = _eventsLocalStore.watchAll().listen(controller.add);
      unawaited(syncEvents());
      controller.onCancel = subscription.cancel;
    });
  }
}

abstract class EventsRemoteSource {
  Future<List<EventDto>> fetchEvents({
    required UserSession session,
    DateTime? updatedSince,
  });

  Future<List<SubjectDto>> fetchSubjects({required UserSession session});
}

class DioEventsRemoteSource implements EventsRemoteSource {
  DioEventsRemoteSource({required Dio dio}) : _dio = dio;

  final Dio _dio;

  @override
  Future<List<EventDto>> fetchEvents({
    required UserSession session,
    DateTime? updatedSince,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '${session.baseUrl}/api/events',
      queryParameters: {
        'limit': 500,
        if (updatedSince != null)
          'updated_since': updatedSince.toUtc().toIso8601String(),
      },
    );

    final payload = response.data?['events'] as List<dynamic>? ?? const [];
    return payload
        .map((entry) => EventDto.fromJson(entry as Map<String, dynamic>))
        .toList();
  }

  @override
  Future<List<SubjectDto>> fetchSubjects({required UserSession session}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '${session.baseUrl}/api/subjects',
    );

    final payload = response.data?['subjects'] as List<dynamic>? ?? const [];
    return payload
        .map((entry) => SubjectDto.fromJson(entry as Map<String, dynamic>))
        .toList();
  }
}
