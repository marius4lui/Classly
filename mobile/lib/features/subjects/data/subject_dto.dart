import 'package:classly_mobile/features/subjects/domain/subject.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'subject_dto.freezed.dart';
part 'subject_dto.g.dart';

@freezed
abstract class SubjectDto with _$SubjectDto {
  const SubjectDto._();

  const factory SubjectDto({
    required String id,
    required String name,
    String? color,
  }) = _SubjectDto;

  factory SubjectDto.fromJson(Map<String, dynamic> json) =>
      _$SubjectDtoFromJson(json);

  Subject toDomain() {
    return Subject(id: id, name: name, color: color);
  }
}
