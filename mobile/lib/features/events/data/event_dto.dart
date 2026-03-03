import 'package:classly_mobile/features/events/domain/event.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'event_dto.freezed.dart';
part 'event_dto.g.dart';

@freezed
abstract class EventDto with _$EventDto {
  const EventDto._();

  const factory EventDto({
    required String id,
    @JsonKey(name: 'class_id') required String classId,
    required String type,
    @Default('MEDIUM') String priority,
    @JsonKey(name: 'subject_id') String? subjectId,
    @JsonKey(name: 'subject_name') @Default('') String subjectName,
    required String title,
    required DateTime date,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'updated_at') required DateTime updatedAt,
    @JsonKey(name: 'author_id') String? authorId,
    @Default(<EventTopicDto>[]) List<EventTopicDto> topics,
    @Default(<EventLinkDto>[]) List<EventLinkDto> links,
  }) = _EventDto;

  factory EventDto.fromJson(Map<String, dynamic> json) =>
      _$EventDtoFromJson(json);

  Event toDomain() {
    return Event(
      id: id,
      classId: classId,
      type: type,
      priority: priority,
      subjectId: subjectId,
      subjectName: subjectName,
      title: title,
      date: date,
      createdAt: createdAt,
      updatedAt: updatedAt,
      authorId: authorId,
      topics: topics.map((topic) => topic.toDomain()).toList(),
      links: links.map((link) => link.toDomain()).toList(),
    );
  }
}

@freezed
abstract class EventTopicDto with _$EventTopicDto {
  const EventTopicDto._();

  const factory EventTopicDto({
    required String id,
    @JsonKey(name: 'topic_type') required String topicType,
    required String content,
    int? count,
    String? pages,
    int? order,
    @JsonKey(name: 'parent_id') String? parentId,
  }) = _EventTopicDto;

  factory EventTopicDto.fromJson(Map<String, dynamic> json) =>
      _$EventTopicDtoFromJson(json);

  EventTopic toDomain() {
    return EventTopic(
      id: id,
      topicType: topicType,
      content: content,
      count: count,
      pages: pages,
      order: order,
      parentId: parentId,
    );
  }
}

@freezed
abstract class EventLinkDto with _$EventLinkDto {
  const EventLinkDto._();

  const factory EventLinkDto({
    required String id,
    required String url,
    String? label,
  }) = _EventLinkDto;

  factory EventLinkDto.fromJson(Map<String, dynamic> json) =>
      _$EventLinkDtoFromJson(json);

  EventLink toDomain() {
    return EventLink(id: id, url: url, label: label);
  }
}
