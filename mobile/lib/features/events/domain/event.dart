import 'package:freezed_annotation/freezed_annotation.dart';

part 'event.freezed.dart';

@freezed
abstract class Event with _$Event {
  const factory Event({
    required String id,
    required String classId,
    required String type,
    required String priority,
    String? subjectId,
    required String subjectName,
    required String title,
    required DateTime date,
    required DateTime createdAt,
    required DateTime updatedAt,
    String? authorId,
    @Default(<EventTopic>[]) List<EventTopic> topics,
    @Default(<EventLink>[]) List<EventLink> links,
  }) = _Event;
}

@freezed
abstract class EventTopic with _$EventTopic {
  const factory EventTopic({
    required String id,
    required String topicType,
    required String content,
    int? count,
    String? pages,
    int? order,
    String? parentId,
  }) = _EventTopic;
}

@freezed
abstract class EventLink with _$EventLink {
  const factory EventLink({
    required String id,
    required String url,
    String? label,
  }) = _EventLink;
}
