import 'dart:async';

import 'package:classly_mobile/features/events/domain/event.dart';

abstract class EventsLocalStore {
  Future<List<Event>> readAll();

  Stream<List<Event>> watchAll();

  Future<void> upsertAll(List<Event> events);

  Future<DateTime?> readLastSyncAt();

  Future<void> saveLastSyncAt(DateTime timestamp);

  Future<void> clear();
}

class InMemoryEventsLocalStore implements EventsLocalStore {
  final _controller = StreamController<List<Event>>.broadcast();
  final Map<String, Event> _eventsById = {};
  DateTime? _lastSyncAt;

  @override
  Future<void> clear() async {
    _eventsById.clear();
    _lastSyncAt = null;
    _emit();
  }

  @override
  Future<List<Event>> readAll() async {
    return _sortedEvents();
  }

  @override
  Future<DateTime?> readLastSyncAt() async => _lastSyncAt;

  @override
  Future<void> saveLastSyncAt(DateTime timestamp) async {
    _lastSyncAt = timestamp.toUtc();
  }

  @override
  Future<void> upsertAll(List<Event> events) async {
    for (final event in events) {
      _eventsById[event.id] = event;
    }
    _emit();
  }

  @override
  Stream<List<Event>> watchAll() => _controller.stream;

  void _emit() {
    _controller.add(_sortedEvents());
  }

  List<Event> _sortedEvents() {
    final values = _eventsById.values.toList()
      ..sort((left, right) => left.date.compareTo(right.date));
    return values;
  }
}
