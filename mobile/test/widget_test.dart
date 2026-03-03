import 'package:classly_mobile/main.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('app shell redirects to login', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: ClasslyMobileApp()));
    await tester.pumpAndSettle();

    expect(find.text('Mit Classly anmelden'), findsOneWidget);
  });
}
