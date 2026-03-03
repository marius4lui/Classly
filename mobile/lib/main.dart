import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  runApp(const ProviderScope(child: ClasslyMobileApp()));
}

class ClasslyMobileApp extends StatelessWidget {
  const ClasslyMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Classly',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2251D1)),
        useMaterial3: true,
      ),
      home: const Scaffold(body: Center(child: Text('Classly Mobile'))),
    );
  }
}
