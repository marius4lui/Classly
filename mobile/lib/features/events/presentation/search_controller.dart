import 'package:classly_mobile/features/events/domain/event.dart';

class EventSearchState {
  const EventSearchState({
    this.query = '',
    this.selectedType,
    this.selectedSubjectId,
  });

  final String query;
  final String? selectedType;
  final String? selectedSubjectId;

  EventSearchState copyWith({
    String? query,
    String? selectedType,
    String? selectedSubjectId,
  }) {
    return EventSearchState(
      query: query ?? this.query,
      selectedType: selectedType ?? this.selectedType,
      selectedSubjectId: selectedSubjectId ?? this.selectedSubjectId,
    );
  }
}

class EventSearchController {
  const EventSearchController(this.state);

  final EventSearchState state;

  List<Event> apply(List<Event> events) {
    final normalizedQuery = state.query.trim().toLowerCase();

    return events.where((event) {
      final matchesType =
          state.selectedType == null || event.type == state.selectedType;
      final matchesSubject =
          state.selectedSubjectId == null ||
          event.subjectId == state.selectedSubjectId;
      final matchesQuery =
          normalizedQuery.isEmpty ||
          event.title.toLowerCase().contains(normalizedQuery) ||
          event.subjectName.toLowerCase().contains(normalizedQuery);

      return matchesType && matchesSubject && matchesQuery;
    }).toList();
  }
}
