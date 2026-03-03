// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'event.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$Event {

 String get id; String get classId; String get type; String get priority; String? get subjectId; String get subjectName; String get title; DateTime get date; DateTime get createdAt; DateTime get updatedAt; String? get authorId; List<EventTopic> get topics; List<EventLink> get links;
/// Create a copy of Event
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EventCopyWith<Event> get copyWith => _$EventCopyWithImpl<Event>(this as Event, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Event&&(identical(other.id, id) || other.id == id)&&(identical(other.classId, classId) || other.classId == classId)&&(identical(other.type, type) || other.type == type)&&(identical(other.priority, priority) || other.priority == priority)&&(identical(other.subjectId, subjectId) || other.subjectId == subjectId)&&(identical(other.subjectName, subjectName) || other.subjectName == subjectName)&&(identical(other.title, title) || other.title == title)&&(identical(other.date, date) || other.date == date)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.authorId, authorId) || other.authorId == authorId)&&const DeepCollectionEquality().equals(other.topics, topics)&&const DeepCollectionEquality().equals(other.links, links));
}


@override
int get hashCode => Object.hash(runtimeType,id,classId,type,priority,subjectId,subjectName,title,date,createdAt,updatedAt,authorId,const DeepCollectionEquality().hash(topics),const DeepCollectionEquality().hash(links));

@override
String toString() {
  return 'Event(id: $id, classId: $classId, type: $type, priority: $priority, subjectId: $subjectId, subjectName: $subjectName, title: $title, date: $date, createdAt: $createdAt, updatedAt: $updatedAt, authorId: $authorId, topics: $topics, links: $links)';
}


}

/// @nodoc
abstract mixin class $EventCopyWith<$Res>  {
  factory $EventCopyWith(Event value, $Res Function(Event) _then) = _$EventCopyWithImpl;
@useResult
$Res call({
 String id, String classId, String type, String priority, String? subjectId, String subjectName, String title, DateTime date, DateTime createdAt, DateTime updatedAt, String? authorId, List<EventTopic> topics, List<EventLink> links
});




}
/// @nodoc
class _$EventCopyWithImpl<$Res>
    implements $EventCopyWith<$Res> {
  _$EventCopyWithImpl(this._self, this._then);

  final Event _self;
  final $Res Function(Event) _then;

/// Create a copy of Event
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
as List<EventTopic>,links: null == links ? _self.links : links // ignore: cast_nullable_to_non_nullable
as List<EventLink>,
  ));
}

}


/// Adds pattern-matching-related methods to [Event].
extension EventPatterns on Event {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Event value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Event() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Event value)  $default,){
final _that = this;
switch (_that) {
case _Event():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Event value)?  $default,){
final _that = this;
switch (_that) {
case _Event() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String classId,  String type,  String priority,  String? subjectId,  String subjectName,  String title,  DateTime date,  DateTime createdAt,  DateTime updatedAt,  String? authorId,  List<EventTopic> topics,  List<EventLink> links)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Event() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String classId,  String type,  String priority,  String? subjectId,  String subjectName,  String title,  DateTime date,  DateTime createdAt,  DateTime updatedAt,  String? authorId,  List<EventTopic> topics,  List<EventLink> links)  $default,) {final _that = this;
switch (_that) {
case _Event():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String classId,  String type,  String priority,  String? subjectId,  String subjectName,  String title,  DateTime date,  DateTime createdAt,  DateTime updatedAt,  String? authorId,  List<EventTopic> topics,  List<EventLink> links)?  $default,) {final _that = this;
switch (_that) {
case _Event() when $default != null:
return $default(_that.id,_that.classId,_that.type,_that.priority,_that.subjectId,_that.subjectName,_that.title,_that.date,_that.createdAt,_that.updatedAt,_that.authorId,_that.topics,_that.links);case _:
  return null;

}
}

}

/// @nodoc


class _Event implements Event {
  const _Event({required this.id, required this.classId, required this.type, required this.priority, this.subjectId, required this.subjectName, required this.title, required this.date, required this.createdAt, required this.updatedAt, this.authorId, final  List<EventTopic> topics = const <EventTopic>[], final  List<EventLink> links = const <EventLink>[]}): _topics = topics,_links = links;
  

@override final  String id;
@override final  String classId;
@override final  String type;
@override final  String priority;
@override final  String? subjectId;
@override final  String subjectName;
@override final  String title;
@override final  DateTime date;
@override final  DateTime createdAt;
@override final  DateTime updatedAt;
@override final  String? authorId;
 final  List<EventTopic> _topics;
@override@JsonKey() List<EventTopic> get topics {
  if (_topics is EqualUnmodifiableListView) return _topics;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_topics);
}

 final  List<EventLink> _links;
@override@JsonKey() List<EventLink> get links {
  if (_links is EqualUnmodifiableListView) return _links;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_links);
}


/// Create a copy of Event
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EventCopyWith<_Event> get copyWith => __$EventCopyWithImpl<_Event>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Event&&(identical(other.id, id) || other.id == id)&&(identical(other.classId, classId) || other.classId == classId)&&(identical(other.type, type) || other.type == type)&&(identical(other.priority, priority) || other.priority == priority)&&(identical(other.subjectId, subjectId) || other.subjectId == subjectId)&&(identical(other.subjectName, subjectName) || other.subjectName == subjectName)&&(identical(other.title, title) || other.title == title)&&(identical(other.date, date) || other.date == date)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.authorId, authorId) || other.authorId == authorId)&&const DeepCollectionEquality().equals(other._topics, _topics)&&const DeepCollectionEquality().equals(other._links, _links));
}


@override
int get hashCode => Object.hash(runtimeType,id,classId,type,priority,subjectId,subjectName,title,date,createdAt,updatedAt,authorId,const DeepCollectionEquality().hash(_topics),const DeepCollectionEquality().hash(_links));

@override
String toString() {
  return 'Event(id: $id, classId: $classId, type: $type, priority: $priority, subjectId: $subjectId, subjectName: $subjectName, title: $title, date: $date, createdAt: $createdAt, updatedAt: $updatedAt, authorId: $authorId, topics: $topics, links: $links)';
}


}

/// @nodoc
abstract mixin class _$EventCopyWith<$Res> implements $EventCopyWith<$Res> {
  factory _$EventCopyWith(_Event value, $Res Function(_Event) _then) = __$EventCopyWithImpl;
@override @useResult
$Res call({
 String id, String classId, String type, String priority, String? subjectId, String subjectName, String title, DateTime date, DateTime createdAt, DateTime updatedAt, String? authorId, List<EventTopic> topics, List<EventLink> links
});




}
/// @nodoc
class __$EventCopyWithImpl<$Res>
    implements _$EventCopyWith<$Res> {
  __$EventCopyWithImpl(this._self, this._then);

  final _Event _self;
  final $Res Function(_Event) _then;

/// Create a copy of Event
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? classId = null,Object? type = null,Object? priority = null,Object? subjectId = freezed,Object? subjectName = null,Object? title = null,Object? date = null,Object? createdAt = null,Object? updatedAt = null,Object? authorId = freezed,Object? topics = null,Object? links = null,}) {
  return _then(_Event(
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
as List<EventTopic>,links: null == links ? _self._links : links // ignore: cast_nullable_to_non_nullable
as List<EventLink>,
  ));
}


}

/// @nodoc
mixin _$EventTopic {

 String get id; String get topicType; String get content; int? get count; String? get pages; int? get order; String? get parentId;
/// Create a copy of EventTopic
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EventTopicCopyWith<EventTopic> get copyWith => _$EventTopicCopyWithImpl<EventTopic>(this as EventTopic, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EventTopic&&(identical(other.id, id) || other.id == id)&&(identical(other.topicType, topicType) || other.topicType == topicType)&&(identical(other.content, content) || other.content == content)&&(identical(other.count, count) || other.count == count)&&(identical(other.pages, pages) || other.pages == pages)&&(identical(other.order, order) || other.order == order)&&(identical(other.parentId, parentId) || other.parentId == parentId));
}


@override
int get hashCode => Object.hash(runtimeType,id,topicType,content,count,pages,order,parentId);

@override
String toString() {
  return 'EventTopic(id: $id, topicType: $topicType, content: $content, count: $count, pages: $pages, order: $order, parentId: $parentId)';
}


}

/// @nodoc
abstract mixin class $EventTopicCopyWith<$Res>  {
  factory $EventTopicCopyWith(EventTopic value, $Res Function(EventTopic) _then) = _$EventTopicCopyWithImpl;
@useResult
$Res call({
 String id, String topicType, String content, int? count, String? pages, int? order, String? parentId
});




}
/// @nodoc
class _$EventTopicCopyWithImpl<$Res>
    implements $EventTopicCopyWith<$Res> {
  _$EventTopicCopyWithImpl(this._self, this._then);

  final EventTopic _self;
  final $Res Function(EventTopic) _then;

/// Create a copy of EventTopic
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


/// Adds pattern-matching-related methods to [EventTopic].
extension EventTopicPatterns on EventTopic {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EventTopic value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EventTopic() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EventTopic value)  $default,){
final _that = this;
switch (_that) {
case _EventTopic():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EventTopic value)?  $default,){
final _that = this;
switch (_that) {
case _EventTopic() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String topicType,  String content,  int? count,  String? pages,  int? order,  String? parentId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EventTopic() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String topicType,  String content,  int? count,  String? pages,  int? order,  String? parentId)  $default,) {final _that = this;
switch (_that) {
case _EventTopic():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String topicType,  String content,  int? count,  String? pages,  int? order,  String? parentId)?  $default,) {final _that = this;
switch (_that) {
case _EventTopic() when $default != null:
return $default(_that.id,_that.topicType,_that.content,_that.count,_that.pages,_that.order,_that.parentId);case _:
  return null;

}
}

}

/// @nodoc


class _EventTopic implements EventTopic {
  const _EventTopic({required this.id, required this.topicType, required this.content, this.count, this.pages, this.order, this.parentId});
  

@override final  String id;
@override final  String topicType;
@override final  String content;
@override final  int? count;
@override final  String? pages;
@override final  int? order;
@override final  String? parentId;

/// Create a copy of EventTopic
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EventTopicCopyWith<_EventTopic> get copyWith => __$EventTopicCopyWithImpl<_EventTopic>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EventTopic&&(identical(other.id, id) || other.id == id)&&(identical(other.topicType, topicType) || other.topicType == topicType)&&(identical(other.content, content) || other.content == content)&&(identical(other.count, count) || other.count == count)&&(identical(other.pages, pages) || other.pages == pages)&&(identical(other.order, order) || other.order == order)&&(identical(other.parentId, parentId) || other.parentId == parentId));
}


@override
int get hashCode => Object.hash(runtimeType,id,topicType,content,count,pages,order,parentId);

@override
String toString() {
  return 'EventTopic(id: $id, topicType: $topicType, content: $content, count: $count, pages: $pages, order: $order, parentId: $parentId)';
}


}

/// @nodoc
abstract mixin class _$EventTopicCopyWith<$Res> implements $EventTopicCopyWith<$Res> {
  factory _$EventTopicCopyWith(_EventTopic value, $Res Function(_EventTopic) _then) = __$EventTopicCopyWithImpl;
@override @useResult
$Res call({
 String id, String topicType, String content, int? count, String? pages, int? order, String? parentId
});




}
/// @nodoc
class __$EventTopicCopyWithImpl<$Res>
    implements _$EventTopicCopyWith<$Res> {
  __$EventTopicCopyWithImpl(this._self, this._then);

  final _EventTopic _self;
  final $Res Function(_EventTopic) _then;

/// Create a copy of EventTopic
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? topicType = null,Object? content = null,Object? count = freezed,Object? pages = freezed,Object? order = freezed,Object? parentId = freezed,}) {
  return _then(_EventTopic(
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
mixin _$EventLink {

 String get id; String get url; String? get label;
/// Create a copy of EventLink
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EventLinkCopyWith<EventLink> get copyWith => _$EventLinkCopyWithImpl<EventLink>(this as EventLink, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is EventLink&&(identical(other.id, id) || other.id == id)&&(identical(other.url, url) || other.url == url)&&(identical(other.label, label) || other.label == label));
}


@override
int get hashCode => Object.hash(runtimeType,id,url,label);

@override
String toString() {
  return 'EventLink(id: $id, url: $url, label: $label)';
}


}

/// @nodoc
abstract mixin class $EventLinkCopyWith<$Res>  {
  factory $EventLinkCopyWith(EventLink value, $Res Function(EventLink) _then) = _$EventLinkCopyWithImpl;
@useResult
$Res call({
 String id, String url, String? label
});




}
/// @nodoc
class _$EventLinkCopyWithImpl<$Res>
    implements $EventLinkCopyWith<$Res> {
  _$EventLinkCopyWithImpl(this._self, this._then);

  final EventLink _self;
  final $Res Function(EventLink) _then;

/// Create a copy of EventLink
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


/// Adds pattern-matching-related methods to [EventLink].
extension EventLinkPatterns on EventLink {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EventLink value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EventLink() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EventLink value)  $default,){
final _that = this;
switch (_that) {
case _EventLink():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EventLink value)?  $default,){
final _that = this;
switch (_that) {
case _EventLink() when $default != null:
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
case _EventLink() when $default != null:
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
case _EventLink():
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
case _EventLink() when $default != null:
return $default(_that.id,_that.url,_that.label);case _:
  return null;

}
}

}

/// @nodoc


class _EventLink implements EventLink {
  const _EventLink({required this.id, required this.url, this.label});
  

@override final  String id;
@override final  String url;
@override final  String? label;

/// Create a copy of EventLink
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EventLinkCopyWith<_EventLink> get copyWith => __$EventLinkCopyWithImpl<_EventLink>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _EventLink&&(identical(other.id, id) || other.id == id)&&(identical(other.url, url) || other.url == url)&&(identical(other.label, label) || other.label == label));
}


@override
int get hashCode => Object.hash(runtimeType,id,url,label);

@override
String toString() {
  return 'EventLink(id: $id, url: $url, label: $label)';
}


}

/// @nodoc
abstract mixin class _$EventLinkCopyWith<$Res> implements $EventLinkCopyWith<$Res> {
  factory _$EventLinkCopyWith(_EventLink value, $Res Function(_EventLink) _then) = __$EventLinkCopyWithImpl;
@override @useResult
$Res call({
 String id, String url, String? label
});




}
/// @nodoc
class __$EventLinkCopyWithImpl<$Res>
    implements _$EventLinkCopyWith<$Res> {
  __$EventLinkCopyWithImpl(this._self, this._then);

  final _EventLink _self;
  final $Res Function(_EventLink) _then;

/// Create a copy of EventLink
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? url = null,Object? label = freezed,}) {
  return _then(_EventLink(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,url: null == url ? _self.url : url // ignore: cast_nullable_to_non_nullable
as String,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
