import 'package:classly_mobile/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('app shell renders classly title', (tester) async {
    await tester.pumpWidget(const ClasslyMobileApp());

    expect(find.text('Classly Mobile'), findsOneWidget);
  });
}
