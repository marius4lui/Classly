import 'package:classly_mobile/features/events/domain/event.dart';

abstract class EventsRepository {
  Stream<List<Event>> watchEvents();

  Future<void> syncEvents();
}
