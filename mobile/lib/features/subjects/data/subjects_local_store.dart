import 'dart:async';

import 'package:classly_mobile/features/subjects/domain/subject.dart';

abstract class SubjectsLocalStore {
  Future<List<Subject>> readAll();

  Stream<List<Subject>> watchAll();

  Future<void> upsertAll(List<Subject> subjects);

  Future<void> clear();
}

class InMemorySubjectsLocalStore implements SubjectsLocalStore {
  final _controller = StreamController<List<Subject>>.broadcast();
  final Map<String, Subject> _subjectsById = {};

  @override
  Future<void> clear() async {
    _subjectsById.clear();
    _emit();
  }

  @override
  Future<List<Subject>> readAll() async {
    return _sortedSubjects();
  }

  @override
  Future<void> upsertAll(List<Subject> subjects) async {
    for (final subject in subjects) {
      _subjectsById[subject.id] = subject;
    }
    _emit();
  }

  @override
  Stream<List<Subject>> watchAll() => _controller.stream;

  void _emit() {
    _controller.add(_sortedSubjects());
  }

  List<Subject> _sortedSubjects() {
    final values = _subjectsById.values.toList()
      ..sort((left, right) => left.name.compareTo(right.name));
    return values;
  }
}
