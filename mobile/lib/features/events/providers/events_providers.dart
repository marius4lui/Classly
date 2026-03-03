import 'package:classly_mobile/features/auth/providers/auth_providers.dart';
import 'package:classly_mobile/features/events/data/events_local_store.dart';
import 'package:classly_mobile/features/events/data/events_repository_impl.dart';
import 'package:classly_mobile/features/events/domain/event.dart';
import 'package:classly_mobile/features/events/domain/events_repository.dart';
import 'package:classly_mobile/features/subjects/data/subjects_local_store.dart';
import 'package:classly_mobile/shared/http/classly_dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final eventsLocalStoreProvider = Provider<EventsLocalStore>((ref) {
  return InMemoryEventsLocalStore();
});

final subjectsLocalStoreProvider = Provider<SubjectsLocalStore>((ref) {
  return InMemorySubjectsLocalStore();
});

final eventsRemoteSourceProvider = Provider<EventsRemoteSource>((ref) {
  return DioEventsRemoteSource(dio: ref.watch(classlyDioProvider));
});

final eventsRepositoryProvider = Provider<EventsRepository>((ref) {
  return EventsRepositoryImpl(
    remoteSource: ref.watch(eventsRemoteSourceProvider),
    eventsLocalStore: ref.watch(eventsLocalStoreProvider),
    subjectsLocalStore: ref.watch(subjectsLocalStoreProvider),
    sessionStorage: ref.watch(sessionStorageProvider),
  );
});

final eventsStreamProvider = StreamProvider<List<Event>>((ref) {
  return ref.watch(eventsRepositoryProvider).watchEvents();
});
