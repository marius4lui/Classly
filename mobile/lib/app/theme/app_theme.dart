import 'package:classly_mobile/app/theme/app_colors.dart';
import 'package:classly_mobile/app/theme/app_typography.dart';
import 'package:flutter/material.dart';

abstract final class AppTheme {
  static final ColorScheme _lightScheme = ColorScheme(
    brightness: Brightness.light,
    primary: AppColors.brand,
    onPrimary: Colors.white,
    secondary: AppColors.accent,
    onSecondary: Colors.white,
    error: AppColors.danger,
    onError: Colors.white,
    surface: AppColors.surface,
    onSurface: AppColors.textPrimary,
  );

  static final ColorScheme _darkScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: const Color(0xFF7FA7FF),
    onPrimary: const Color(0xFF0F172A),
    secondary: const Color(0xFF45D3CA),
    onSecondary: const Color(0xFF042B29),
    error: const Color(0xFFFF8A80),
    onError: const Color(0xFF451214),
    surface: AppColors.surfaceDark,
    onSurface: const Color(0xFFF8FAFC),
  );

  static ThemeData get lightTheme => _buildTheme(
    colorScheme: _lightScheme,
    scaffoldBackgroundColor: AppColors.canvas,
  );

  static ThemeData get darkTheme => _buildTheme(
    colorScheme: _darkScheme,
    scaffoldBackgroundColor: const Color(0xFF09111F),
  );

  static ThemeData _buildTheme({
    required ColorScheme colorScheme,
    required Color scaffoldBackgroundColor,
  }) {
    final textTheme = AppTypography.buildTextTheme(colorScheme);

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: scaffoldBackgroundColor,
      textTheme: textTheme,
      appBarTheme: AppBarTheme(
        backgroundColor: colorScheme.surface,
        elevation: 0,
        foregroundColor: colorScheme.onSurface,
        centerTitle: false,
        surfaceTintColor: Colors.transparent,
        titleTextStyle: textTheme.titleLarge,
      ),
      cardTheme: CardThemeData(
        color: colorScheme.surface,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: AppColors.border),
        ),
        margin: EdgeInsets.zero,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colorScheme.surface,
        hintStyle: textTheme.bodyMedium?.copyWith(color: AppColors.textMuted),
        labelStyle: textTheme.labelMedium,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 16,
        ),
        border: _inputBorder(AppColors.border),
        enabledBorder: _inputBorder(AppColors.border),
        focusedBorder: _inputBorder(colorScheme.primary, width: 1.8),
        errorBorder: _inputBorder(AppColors.danger),
        focusedErrorBorder: _inputBorder(AppColors.danger, width: 1.8),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: colorScheme.primary,
          foregroundColor: colorScheme.onPrimary,
          minimumSize: const Size.fromHeight(52),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          textStyle: textTheme.labelLarge,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: colorScheme.onSurface,
          minimumSize: const Size.fromHeight(52),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          side: const BorderSide(color: AppColors.border),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          textStyle: textTheme.labelLarge?.copyWith(
            color: colorScheme.onSurface,
          ),
        ),
      ),
      dividerColor: AppColors.border,
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: colorScheme.surface,
        surfaceTintColor: Colors.transparent,
        showDragHandle: true,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
        ),
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: colorScheme.primary,
      ),
    );
  }

  static OutlineInputBorder _inputBorder(Color color, {double width = 1}) {
    return OutlineInputBorder(
      borderRadius: BorderRadius.circular(18),
      borderSide: BorderSide(color: color, width: width),
    );
  }
}
