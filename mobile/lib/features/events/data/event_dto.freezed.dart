// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'event_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$EventDto {

 String get id;@JsonKey(name: 'class_id') String get classId; String get type; String get priority;@JsonKey(name: 'subject_id') String? get subjectId;@JsonKey(name: 'subject_name') String get subjectName; String get title; DateTime get date;@JsonKey(name: 'created_at') DateTime get createdAt;@JsonKey(name: 'updated_at') DateTime get updatedAt;@JsonKey(name: 'author_id') String? get authorId; List<EventTopicDto> get topics; List<EventLinkDto> get links;
/// Create a copy of EventDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EventDtoCopyWith<EventDto> get copyWith => _$EventDtoCopyWithImpl<EventDto>(this as EventDto, _$identity);

  /// Serializes this EventDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EventDto&&(identical(other.id, id) || other.id == id)&&(identical(other.classId, classId) || other.classId == classId)&&(identical(other.type, type) || other.type == type)&&(identical(other.priority, priority) || other.priority == priority)&&(identical(other.subjectId, subjectId) || other.subjectId == subjectId)&&(identical(other.subjectName, subjectName) || other.subjectName == subjectName)&&(identical(other.title, title) || other.title == title)&&(identical(other.date, date) || other.date == date)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.authorId, authorId) || other.authorId == authorId)&&const DeepCollectionEquality().equals(other.topics, topics)&&const DeepCollectionEquality().equals(other.links, links));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,classId,type,priority,subjectId,subjectName,title,date,createdAt,updatedAt,authorId,const DeepCollectionEquality().hash(topics),const DeepCollectionEquality().hash(links));

@override
String toString() {
  return 'EventDto(id: $id, classId: $classId, type: $type, priority: $priority, subjectId: $subjectId, subjectName: $subjectName, title: $title, date: $date, createdAt: $createdAt, updatedAt: $updatedAt, authorId: $authorId, topics: $topics, links: $links)';
}


}

/// @nodoc
abstract mixin class $EventDtoCopyWith<$Res>  {
  factory $EventDtoCopyWith(EventDto value, $Res Function(EventDto) _then) = _$EventDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'class_id') String classId, String type, String priority,@JsonKey(name: 'subject_id') String? subjectId,@JsonKey(name: 'subject_name') String subjectName, String title, DateTime date,@JsonKey(name: 'created_at') DateTime createdAt,@JsonKey(name: 'updated_at') DateTime updatedAt,@JsonKey(name: 'author_id') String? authorId, List<EventTopicDto> topics, List<EventLinkDto> links
});




}
/// @nodoc
class _$EventDtoCopyWithImpl<$Res>
    implements $EventDtoCopyWith<$Res> {
  _$EventDtoCopyWithImpl(this._self, this._then);

  final EventDto _self;
  final $Res Function(EventDto) _then;

/// Create a copy of EventDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? classId = null,Object? type = null,Object? priority = null,Object? subjectId = freezed,Object? subjectName = null,Object? title = null,Object? date = null,Object? createdAt = null,Object? updatedAt = null,Object? authorId = freezed,Object? topics = null,Object? links = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,classId: null == classId ? _self.classId : classId // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,priority: null == priority ? _self.priority : priority // ignore: cast_nullable_to_non_nullable
as String,subjectId: freezed == subjectId ? _self.subjectId : subjectId // ignore: cast_nullable_to_non_nullable
as String?,subjectName: null == subjectName ? _self.subjectName : subjectName // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,date: null == date ? _self.date : date // ignore: cast_nullable_to_non_nullable
as DateTime,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,authorId: freezed == authorId ? _self.authorId : authorId // ignore: cast_nullable_to_non_nullable
as String?,topics: null == topics ? _self.topics : topics // ignore: cast_nullable_to_non_nullable
as List<EventTopicDto>,links: null == links ? _self.links : links // ignore: cast_nullable_to_non_nullable
as List<EventLinkDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [EventDto].
extension EventDtoPatterns on EventDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EventDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EventDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EventDto value)  $default,){
final _that = this;
switch (_that) {
case _EventDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EventDto value)?  $default,){
final _that = this;
switch (_that) {
case _EventDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'class_id')  String classId,  String type,  String priority, @JsonKey(name: 'subject_id')  String? subjectId, @JsonKey(name: 'subject_name')  String subjectName,  String title,  DateTime date, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt, @JsonKey(name: 'author_id')  String? authorId,  List<EventTopicDto> topics,  List<EventLinkDto> links)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EventDto() when $default != null:
return $default(_that.id,_that.classId,_that.type,_that.priority,_that.subjectId,_that.subjectName,_that.title,_that.date,_that.createdAt,_that.updatedAt,_that.authorId,_that.topics,_that.links);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'class_id')  String classId,  String type,  String priority, @JsonKey(name: 'subject_id')  String? subjectId, @JsonKey(name: 'subject_name')  String subjectName,  String title,  DateTime date, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt, @JsonKey(name: 'author_id')  String? authorId,  List<EventTopicDto> topics,  List<EventLinkDto> links)  $default,) {final _that = this;
switch (_that) {
case _EventDto():
return $default(_that.id,_that.classId,_that.type,_that.priority,_that.subjectId,_that.subjectName,_that.title,_that.date,_that.createdAt,_that.updatedAt,_that.authorId,_that.topics,_that.links);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'class_id')  String classId,  String type,  String priority, @JsonKey(name: 'subject_id')  String? subjectId, @JsonKey(name: 'subject_name')  String subjectName,  String title,  DateTime date, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt, @JsonKey(name: 'author_id')  String? authorId,  List<EventTopicDto> topics,  List<EventLinkDto> links)?  $default,) {final _that = this;
switch (_that) {
case _EventDto() when $default != null:
return $default(_that.id,_that.classId,_that.type,_that.priority,_that.subjectId,_that.subjectName,_that.title,_that.date,_that.createdAt,_that.updatedAt,_that.authorId,_that.topics,_that.links);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EventDto extends EventDto {
  const _EventDto({required this.id, @JsonKey(name: 'class_id') required this.classId, required this.type, this.priority = 'MEDIUM', @JsonKey(name: 'subject_id') this.subjectId, @JsonKey(name: 'subject_name') this.subjectName = '', required this.title, required this.date, @JsonKey(name: 'created_at') required this.createdAt, @JsonKey(name: 'updated_at') required this.updatedAt, @JsonKey(name: 'author_id') this.authorId, final  List<EventTopicDto> topics = const <EventTopicDto>[], final  List<EventLinkDto> links = const <EventLinkDto>[]}): _topics = topics,_links = links,super._();
  factory _EventDto.fromJson(Map<String, dynamic> json) => _$EventDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'class_id') final  String classId;
@override final  String type;
@override@JsonKey() final  String priority;
@override@JsonKey(name: 'subject_id') final  String? subjectId;
@override@JsonKey(name: 'subject_name') final  String subjectName;
@override final  String title;
@override final  DateTime date;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;
@override@JsonKey(name: 'updated_at') final  DateTime updatedAt;
@override@JsonKey(name: 'author_id') final  String? authorId;
 final  List<EventTopicDto> _topics;
@override@JsonKey() List<EventTopicDto> get topics {
  if (_topics is EqualUnmodifiableListView) return _topics;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_topics);
}

 final  List<EventLinkDto> _links;
@override@JsonKey() List<EventLinkDto> get links {
  if (_links is EqualUnmodifiableListView) return _links;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_links);
}


/// Create a copy of EventDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EventDtoCopyWith<_EventDto> get copyWith => __$EventDtoCopyWithImpl<_EventDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EventDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EventDto&&(identical(other.id, id) || other.id == id)&&(identical(other.classId, classId) || other.classId == classId)&&(identical(other.type, type) || other.type == type)&&(identical(other.priority, priority) || other.priority == priority)&&(identical(other.subjectId, subjectId) || other.subjectId == subjectId)&&(identical(other.subjectName, subjectName) || other.subjectName == subjectName)&&(identical(other.title, title) || other.title == title)&&(identical(other.date, date) || other.date == date)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.authorId, authorId) || other.authorId == authorId)&&const DeepCollectionEquality().equals(other._topics, _topics)&&const DeepCollectionEquality().equals(other._links, _links));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,classId,type,priority,subjectId,subjectName,title,date,createdAt,updatedAt,authorId,const DeepCollectionEquality().hash(_topics),const DeepCollectionEquality().hash(_links));

@override
String toString() {
  return 'EventDto(id: $id, classId: $classId, type: $type, priority: $priority, subjectId: $subjectId, subjectName: $subjectName, title: $title, date: $date, createdAt: $createdAt, updatedAt: $updatedAt, authorId: $authorId, topics: $topics, links: $links)';
}


}

/// @nodoc
abstract mixin class _$EventDtoCopyWith<$Res> implements $EventDtoCopyWith<$Res> {
  factory _$EventDtoCopyWith(_EventDto value, $Res Function(_EventDto) _then) = __$EventDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'class_id') String classId, String type, String priority,@JsonKey(name: 'subject_id') String? subjectId,@JsonKey(name: 'subject_name') String subjectName, String title, DateTime date,@JsonKey(name: 'created_at') DateTime createdAt,@JsonKey(name: 'updated_at') DateTime updatedAt,@JsonKey(name: 'author_id') String? authorId, List<EventTopicDto> topics, List<EventLinkDto> links
});




}
/// @nodoc
class __$EventDtoCopyWithImpl<$Res>
    implements _$EventDtoCopyWith<$Res> {
  __$EventDtoCopyWithImpl(this._self, this._then);

  final _EventDto _self;
  final $Res Function(_EventDto) _then;

/// Create a copy of EventDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? classId = null,Object? type = null,Object? priority = null,Object? subjectId = freezed,Object? subjectName = null,Object? title = null,Object? date = null,Object? createdAt = null,Object? updatedAt = null,Object? authorId = freezed,Object? topics = null,Object? links = null,}) {
  return _then(_EventDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,classId: null == classId ? _self.classId : classId // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,priority: null == priority ? _self.priority : priority // ignore: cast_nullable_to_non_nullable
as String,subjectId: freezed == subjectId ? _self.subjectId : subjectId // ignore: cast_nullable_to_non_nullable
as String?,subjectName: null == subjectName ? _self.subjectName : subjectName // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,date: null == date ? _self.date : date // ignore: cast_nullable_to_non_nullable
as DateTime,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,authorId: freezed == authorId ? _self.authorId : authorId // ignore: cast_nullable_to_non_nullable
as String?,topics: null == topics ? _self._topics : topics // ignore: cast_nullable_to_non_nullable
as List<EventTopicDto>,links: null == links ? _self._links : links // ignore: cast_nullable_to_non_nullable
as List<EventLinkDto>,
  ));
}


}


/// @nodoc
mixin _$EventTopicDto {

 String get id;@JsonKey(name: 'topic_type') String get topicType; String get content; int? get count; String? get pages; int? get order;@JsonKey(name: 'parent_id') String? get parentId;
/// Create a copy of EventTopicDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EventTopicDtoCopyWith<EventTopicDto> get copyWith => _$EventTopicDtoCopyWithImpl<EventTopicDto>(this as EventTopicDto, _$identity);

  /// Serializes this EventTopicDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EventTopicDto&&(identical(other.id, id) || other.id == id)&&(identical(other.topicType, topicType) || other.topicType == topicType)&&(identical(other.content, content) || other.content == content)&&(identical(other.count, count) || other.count == count)&&(identical(other.pages, pages) || other.pages == pages)&&(identical(other.order, order) || other.order == order)&&(identical(other.parentId, parentId) || other.parentId == parentId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,topicType,content,count,pages,order,parentId);

@override
String toString() {
  return 'EventTopicDto(id: $id, topicType: $topicType, content: $content, count: $count, pages: $pages, order: $order, parentId: $parentId)';
}


}

/// @nodoc
abstract mixin class $EventTopicDtoCopyWith<$Res>  {
  factory $EventTopicDtoCopyWith(EventTopicDto value, $Res Function(EventTopicDto) _then) = _$EventTopicDtoCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'topic_type') String topicType, String content, int? count, String? pages, int? order,@JsonKey(name: 'parent_id') String? parentId
});




}
/// @nodoc
class _$EventTopicDtoCopyWithImpl<$Res>
    implements $EventTopicDtoCopyWith<$Res> {
  _$EventTopicDtoCopyWithImpl(this._self, this._then);

  final EventTopicDto _self;
  final $Res Function(EventTopicDto) _then;

/// Create a copy of EventTopicDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? topicType = null,Object? content = null,Object? count = freezed,Object? pages = freezed,Object? order = freezed,Object? parentId = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,topicType: null == topicType ? _self.topicType : topicType // ignore: cast_nullable_to_non_nullable
as String,content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as String,count: freezed == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int?,pages: freezed == pages ? _self.pages : pages // ignore: cast_nullable_to_non_nullable
as String?,order: freezed == order ? _self.order : order // ignore: cast_nullable_to_non_nullable
as int?,parentId: freezed == parentId ? _self.parentId : parentId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [EventTopicDto].
extension EventTopicDtoPatterns on EventTopicDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EventTopicDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EventTopicDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EventTopicDto value)  $default,){
final _that = this;
switch (_that) {
case _EventTopicDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EventTopicDto value)?  $default,){
final _that = this;
switch (_that) {
case _EventTopicDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'topic_type')  String topicType,  String content,  int? count,  String? pages,  int? order, @JsonKey(name: 'parent_id')  String? parentId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EventTopicDto() when $default != null:
return $default(_that.id,_that.topicType,_that.content,_that.count,_that.pages,_that.order,_that.parentId);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'topic_type')  String topicType,  String content,  int? count,  String? pages,  int? order, @JsonKey(name: 'parent_id')  String? parentId)  $default,) {final _that = this;
switch (_that) {
case _EventTopicDto():
return $default(_that.id,_that.topicType,_that.content,_that.count,_that.pages,_that.order,_that.parentId);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'topic_type')  String topicType,  String content,  int? count,  String? pages,  int? order, @JsonKey(name: 'parent_id')  String? parentId)?  $default,) {final _that = this;
switch (_that) {
case _EventTopicDto() when $default != null:
return $default(_that.id,_that.topicType,_that.content,_that.count,_that.pages,_that.order,_that.parentId);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EventTopicDto extends EventTopicDto {
  const _EventTopicDto({required this.id, @JsonKey(name: 'topic_type') required this.topicType, required this.content, this.count, this.pages, this.order, @JsonKey(name: 'parent_id') this.parentId}): super._();
  factory _EventTopicDto.fromJson(Map<String, dynamic> json) => _$EventTopicDtoFromJson(json);

@override final  String id;
@override@JsonKey(name: 'topic_type') final  String topicType;
@override final  String content;
@override final  int? count;
@override final  String? pages;
@override final  int? order;
@override@JsonKey(name: 'parent_id') final  String? parentId;

/// Create a copy of EventTopicDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EventTopicDtoCopyWith<_EventTopicDto> get copyWith => __$EventTopicDtoCopyWithImpl<_EventTopicDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EventTopicDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EventTopicDto&&(identical(other.id, id) || other.id == id)&&(identical(other.topicType, topicType) || other.topicType == topicType)&&(identical(other.content, content) || other.content == content)&&(identical(other.count, count) || other.count == count)&&(identical(other.pages, pages) || other.pages == pages)&&(identical(other.order, order) || other.order == order)&&(identical(other.parentId, parentId) || other.parentId == parentId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,topicType,content,count,pages,order,parentId);

@override
String toString() {
  return 'EventTopicDto(id: $id, topicType: $topicType, content: $content, count: $count, pages: $pages, order: $order, parentId: $parentId)';
}


}

/// @nodoc
abstract mixin class _$EventTopicDtoCopyWith<$Res> implements $EventTopicDtoCopyWith<$Res> {
  factory _$EventTopicDtoCopyWith(_EventTopicDto value, $Res Function(_EventTopicDto) _then) = __$EventTopicDtoCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'topic_type') String topicType, String content, int? count, String? pages, int? order,@JsonKey(name: 'parent_id') String? parentId
});




}
/// @nodoc
class __$EventTopicDtoCopyWithImpl<$Res>
    implements _$EventTopicDtoCopyWith<$Res> {
  __$EventTopicDtoCopyWithImpl(this._self, this._then);

  final _EventTopicDto _self;
  final $Res Function(_EventTopicDto) _then;

/// Create a copy of EventTopicDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? topicType = null,Object? content = null,Object? count = freezed,Object? pages = freezed,Object? order = freezed,Object? parentId = freezed,}) {
  return _then(_EventTopicDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,topicType: null == topicType ? _self.topicType : topicType // ignore: cast_nullable_to_non_nullable
as String,content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as String,count: freezed == count ? _self.count : count // ignore: cast_nullable_to_non_nullable
as int?,pages: freezed == pages ? _self.pages : pages // ignore: cast_nullable_to_non_nullable
as String?,order: freezed == order ? _self.order : order // ignore: cast_nullable_to_non_nullable
as int?,parentId: freezed == parentId ? _self.parentId : parentId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$EventLinkDto {

 String get id; String get url; String? get label;
/// Create a copy of EventLinkDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EventLinkDtoCopyWith<EventLinkDto> get copyWith => _$EventLinkDtoCopyWithImpl<EventLinkDto>(this as EventLinkDto, _$identity);

  /// Serializes this EventLinkDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EventLinkDto&&(identical(other.id, id) || other.id == id)&&(identical(other.url, url) || other.url == url)&&(identical(other.label, label) || other.label == label));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,url,label);

@override
String toString() {
  return 'EventLinkDto(id: $id, url: $url, label: $label)';
}


}

/// @nodoc
abstract mixin class $EventLinkDtoCopyWith<$Res>  {
  factory $EventLinkDtoCopyWith(EventLinkDto value, $Res Function(EventLinkDto) _then) = _$EventLinkDtoCopyWithImpl;
@useResult
$Res call({
 String id, String url, String? label
});




}
/// @nodoc
class _$EventLinkDtoCopyWithImpl<$Res>
    implements $EventLinkDtoCopyWith<$Res> {
  _$EventLinkDtoCopyWithImpl(this._self, this._then);

  final EventLinkDto _self;
  final $Res Function(EventLinkDto) _then;

/// Create a copy of EventLinkDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? url = null,Object? label = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,url: null == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [EventLinkDto].
extension EventLinkDtoPatterns on EventLinkDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EventLinkDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EventLinkDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EventLinkDto value)  $default,){
final _that = this;
switch (_that) {
case _EventLinkDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EventLinkDto value)?  $default,){
final _that = this;
switch (_that) {
case _EventLinkDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String url,  String? label)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EventLinkDto() when $default != null:
return $default(_that.id,_that.url,_that.label);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String url,  String? label)  $default,) {final _that = this;
switch (_that) {
case _EventLinkDto():
return $default(_that.id,_that.url,_that.label);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String url,  String? label)?  $default,) {final _that = this;
switch (_that) {
case _EventLinkDto() when $default != null:
return $default(_that.id,_that.url,_that.label);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EventLinkDto extends EventLinkDto {
  const _EventLinkDto({required this.id, required this.url, this.label}): super._();
  factory _EventLinkDto.fromJson(Map<String, dynamic> json) => _$EventLinkDtoFromJson(json);

@override final  String id;
@override final  String url;
@override final  String? label;

/// Create a copy of EventLinkDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EventLinkDtoCopyWith<_EventLinkDto> get copyWith => __$EventLinkDtoCopyWithImpl<_EventLinkDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EventLinkDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EventLinkDto&&(identical(other.id, id) || other.id == id)&&(identical(other.url, url) || other.url == url)&&(identical(other.label, label) || other.label == label));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,url,label);

@override
String toString() {
  return 'EventLinkDto(id: $id, url: $url, label: $label)';
}


}

/// @nodoc
abstract mixin class _$EventLinkDtoCopyWith<$Res> implements $EventLinkDtoCopyWith<$Res> {
  factory _$EventLinkDtoCopyWith(_EventLinkDto value, $Res Function(_EventLinkDto) _then) = __$EventLinkDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String url, String? label
});




}
/// @nodoc
class __$EventLinkDtoCopyWithImpl<$Res>
    implements _$EventLinkDtoCopyWith<$Res> {
  __$EventLinkDtoCopyWithImpl(this._self, this._then);

  final _EventLinkDto _self;
  final $Res Function(_EventLinkDto) _then;

/// Create a copy of EventLinkDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? url = null,Object? label = freezed,}) {
  return _then(_EventLinkDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,url: null == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
