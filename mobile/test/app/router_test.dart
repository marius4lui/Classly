import 'package:classly_mobile/app/app.dart';
import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('unauthenticated user lands on instance select', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sessionBootstrapProvider.overrideWithValue(
            const SessionBootstrapState.unauthenticated(),
          ),
        ],
        child: const ClasslyApp(),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Instanz waehlen'), findsOneWidget);
  });

  testWidgets('authenticated user lands on kalender', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sessionBootstrapProvider.overrideWithValue(
            const SessionBootstrapState.authenticated(),
          ),
        ],
        child: const ClasslyApp(),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Kalender'), findsOneWidget);
  });
}
