import 'package:freezed_annotation/freezed_annotation.dart';

part 'subject.freezed.dart';

@freezed
abstract class Subject with _$Subject {
  const factory Subject({
    required String id,
    required String name,
    String? color,
  }) = _Subject;
}
