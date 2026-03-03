import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:classly_mobile/app/app.dart';

void main() {
  runApp(const ProviderScope(child: ClasslyMobileApp()));
}

class ClasslyMobileApp extends ClasslyApp {
  const ClasslyMobileApp({super.key});
}
