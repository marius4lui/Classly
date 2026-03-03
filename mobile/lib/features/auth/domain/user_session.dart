class UserInfo {
  const UserInfo({
    required this.id,
    required this.name,
    required this.role,
    this.classId,
    this.className,
    this.email,
    this.isRegistered,
  });

  final String id;
  final String name;
  final String role;
  final String? classId;
  final String? className;
  final String? email;
  final bool? isRegistered;

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'role': role,
      'class_id': classId,
      'class_name': className,
      'email': email,
      'is_registered': isRegistered,
    };
  }

  factory UserInfo.fromJson(Map<String, dynamic> json) {
    return UserInfo(
      id: json['id'] as String? ?? json['sub'] as String? ?? '',
      name: json['name'] as String? ?? '',
      role: json['role'] as String? ?? 'member',
      classId: json['class_id'] as String?,
      className: json['class_name'] as String?,
      email: json['email'] as String?,
      isRegistered: json['is_registered'] as bool?,
    );
  }
}

class UserSession {
  const UserSession({
    required this.baseUrl,
    this.accessToken,
    this.scope,
    this.classId,
    this.userInfo,
  });

  final String baseUrl;
  final String? accessToken;
  final String? scope;
  final String? classId;
  final UserInfo? userInfo;

  bool get isAuthenticated => accessToken != null && accessToken!.isNotEmpty;

  UserSession copyWith({
    String? baseUrl,
    String? accessToken,
    String? scope,
    String? classId,
    UserInfo? userInfo,
  }) {
    return UserSession(
      baseUrl: baseUrl ?? this.baseUrl,
      accessToken: accessToken ?? this.accessToken,
      scope: scope ?? this.scope,
      classId: classId ?? this.classId,
      userInfo: userInfo ?? this.userInfo,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'base_url': baseUrl,
      'access_token': accessToken,
      'scope': scope,
      'class_id': classId,
      'user_info': userInfo?.toJson(),
    };
  }

  factory UserSession.fromJson(Map<String, dynamic> json) {
    return UserSession(
      baseUrl: json['base_url'] as String? ?? '',
      accessToken: json['access_token'] as String?,
      scope: json['scope'] as String?,
      classId: json['class_id'] as String?,
      userInfo: json['user_info'] is Map<String, dynamic>
          ? UserInfo.fromJson(json['user_info'] as Map<String, dynamic>)
          : null,
    );
  }
}
