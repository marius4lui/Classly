import 'package:classly_mobile/app/theme/app_colors.dart';
import 'package:classly_mobile/app/theme/app_theme.dart';
import 'package:classly_mobile/shared/widgets/app_text_field.dart';
import 'package:classly_mobile/shared/widgets/primary_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('app theme can be built', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme,
        home: const Scaffold(body: SizedBox()),
      ),
    );

    final app = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(app.theme?.colorScheme.primary, AppColors.brand);
  });

  testWidgets('primary button renders', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: PrimaryButton(label: 'Weiter', onPressed: () {}),
        ),
      ),
    );

    expect(find.text('Weiter'), findsOneWidget);
  });

  testWidgets('text field renders', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: AppTheme.lightTheme,
        home: const Scaffold(
          body: AppTextField(
            label: 'Instanz',
            hintText: 'https://classly.example',
          ),
        ),
      ),
    );

    expect(find.text('Instanz'), findsOneWidget);
    expect(find.text('https://classly.example'), findsOneWidget);
  });
}
