// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'subject_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$SubjectDto {

 String get id; String get name; String? get color;
/// Create a copy of SubjectDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SubjectDtoCopyWith<SubjectDto> get copyWith => _$SubjectDtoCopyWithImpl<SubjectDto>(this as SubjectDto, _$identity);

  /// Serializes this SubjectDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SubjectDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.color, color) || other.color == color));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,color);

@override
String toString() {
  return 'SubjectDto(id: $id, name: $name, color: $color)';
}


}

/// @nodoc
abstract mixin class $SubjectDtoCopyWith<$Res>  {
  factory $SubjectDtoCopyWith(SubjectDto value, $Res Function(SubjectDto) _then) = _$SubjectDtoCopyWithImpl;
@useResult
$Res call({
 String id, String name, String? color
});




}
/// @nodoc
class _$SubjectDtoCopyWithImpl<$Res>
    implements $SubjectDtoCopyWith<$Res> {
  _$SubjectDtoCopyWithImpl(this._self, this._then);

  final SubjectDto _self;
  final $Res Function(SubjectDto) _then;

/// Create a copy of SubjectDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? color = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,color: freezed == color ? _self.color : color // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SubjectDto].
extension SubjectDtoPatterns on SubjectDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SubjectDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SubjectDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SubjectDto value)  $default,){
final _that = this;
switch (_that) {
case _SubjectDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SubjectDto value)?  $default,){
final _that = this;
switch (_that) {
case _SubjectDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String? color)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SubjectDto() when $default != null:
return $default(_that.id,_that.name,_that.color);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String? color)  $default,) {final _that = this;
switch (_that) {
case _SubjectDto():
return $default(_that.id,_that.name,_that.color);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String? color)?  $default,) {final _that = this;
switch (_that) {
case _SubjectDto() when $default != null:
return $default(_that.id,_that.name,_that.color);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SubjectDto extends SubjectDto {
  const _SubjectDto({required this.id, required this.name, this.color}): super._();
  factory _SubjectDto.fromJson(Map<String, dynamic> json) => _$SubjectDtoFromJson(json);

@override final  String id;
@override final  String name;
@override final  String? color;

/// Create a copy of SubjectDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SubjectDtoCopyWith<_SubjectDto> get copyWith => __$SubjectDtoCopyWithImpl<_SubjectDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SubjectDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _SubjectDto&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.color, color) || other.color == color));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,color);

@override
String toString() {
  return 'SubjectDto(id: $id, name: $name, color: $color)';
}


}

/// @nodoc
abstract mixin class _$SubjectDtoCopyWith<$Res> implements $SubjectDtoCopyWith<$Res> {
  factory _$SubjectDtoCopyWith(_SubjectDto value, $Res Function(_SubjectDto) _then) = __$SubjectDtoCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String? color
});




}
/// @nodoc
class __$SubjectDtoCopyWithImpl<$Res>
    implements _$SubjectDtoCopyWith<$Res> {
  __$SubjectDtoCopyWithImpl(this._self, this._then);

  final _SubjectDto _self;
  final $Res Function(_SubjectDto) _then;

/// Create a copy of SubjectDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? color = freezed,}) {
  return _then(_SubjectDto(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,color: freezed == color ? _self.color : color // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
