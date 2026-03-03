// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'event_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_EventDto _$EventDtoFromJson(Map<String, dynamic> json) => _EventDto(
  id: json['id'] as String,
  classId: json['class_id'] as String,
  type: json['type'] as String,
  priority: json['priority'] as String? ?? 'MEDIUM',
  subjectId: json['subject_id'] as String?,
  subjectName: json['subject_name'] as String? ?? '',
  title: json['title'] as String,
  date: DateTime.parse(json['date'] as String),
  createdAt: DateTime.parse(json['created_at'] as String),
  updatedAt: DateTime.parse(json['updated_at'] as String),
  authorId: json['author_id'] as String?,
  topics:
      (json['topics'] as List<dynamic>?)
          ?.map((e) => EventTopicDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <EventTopicDto>[],
  links:
      (json['links'] as List<dynamic>?)
          ?.map((e) => EventLinkDto.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const <EventLinkDto>[],
);

Map<String, dynamic> _$EventDtoToJson(_EventDto instance) => <String, dynamic>{
  'id': instance.id,
  'class_id': instance.classId,
  'type': instance.type,
  'priority': instance.priority,
  'subject_id': instance.subjectId,
  'subject_name': instance.subjectName,
  'title': instance.title,
  'date': instance.date.toIso8601String(),
  'created_at': instance.createdAt.toIso8601String(),
  'updated_at': instance.updatedAt.toIso8601String(),
  'author_id': instance.authorId,
  'topics': instance.topics,
  'links': instance.links,
};

_EventTopicDto _$EventTopicDtoFromJson(Map<String, dynamic> json) =>
    _EventTopicDto(
      id: json['id'] as String,
      topicType: json['topic_type'] as String,
      content: json['content'] as String,
      count: (json['count'] as num?)?.toInt(),
      pages: json['pages'] as String?,
      order: (json['order'] as num?)?.toInt(),
      parentId: json['parent_id'] as String?,
    );

Map<String, dynamic> _$EventTopicDtoToJson(_EventTopicDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'topic_type': instance.topicType,
      'content': instance.content,
      'count': instance.count,
      'pages': instance.pages,
      'order': instance.order,
      'parent_id': instance.parentId,
    };

_EventLinkDto _$EventLinkDtoFromJson(Map<String, dynamic> json) =>
    _EventLinkDto(
      id: json['id'] as String,
      url: json['url'] as String,
      label: json['label'] as String?,
    );

Map<String, dynamic> _$EventLinkDtoToJson(_EventLinkDto instance) =>
    <String, dynamic>{
      'id': instance.id,
      'url': instance.url,
      'label': instance.label,
    };
