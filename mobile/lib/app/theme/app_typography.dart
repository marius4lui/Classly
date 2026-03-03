import 'package:classly_mobile/app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

abstract final class AppTypography {
  static TextTheme buildTextTheme(ColorScheme colorScheme) {
    final base = GoogleFonts.plusJakartaSansTextTheme();

    return base.copyWith(
      displaySmall: base.displaySmall?.copyWith(
        color: colorScheme.onSurface,
        fontSize: 34,
        fontWeight: FontWeight.w700,
        height: 1.08,
        letterSpacing: -0.8,
      ),
      headlineMedium: base.headlineMedium?.copyWith(
        color: colorScheme.onSurface,
        fontSize: 28,
        fontWeight: FontWeight.w700,
        height: 1.12,
        letterSpacing: -0.5,
      ),
      titleLarge: base.titleLarge?.copyWith(
        color: colorScheme.onSurface,
        fontSize: 20,
        fontWeight: FontWeight.w700,
        height: 1.2,
      ),
      titleMedium: base.titleMedium?.copyWith(
        color: colorScheme.onSurface,
        fontSize: 16,
        fontWeight: FontWeight.w700,
        height: 1.25,
      ),
      bodyLarge: base.bodyLarge?.copyWith(
        color: colorScheme.onSurface,
        fontSize: 16,
        fontWeight: FontWeight.w500,
        height: 1.45,
      ),
      bodyMedium: base.bodyMedium?.copyWith(
        color: AppColors.textSecondary,
        fontSize: 14,
        fontWeight: FontWeight.w500,
        height: 1.45,
      ),
      bodySmall: base.bodySmall?.copyWith(
        color: AppColors.textMuted,
        fontSize: 12,
        fontWeight: FontWeight.w600,
        height: 1.35,
        letterSpacing: 0.1,
      ),
      labelLarge: base.labelLarge?.copyWith(
        color: colorScheme.onPrimary,
        fontSize: 14,
        fontWeight: FontWeight.w700,
        height: 1.1,
      ),
      labelMedium: base.labelMedium?.copyWith(
        color: AppColors.textSecondary,
        fontSize: 12,
        fontWeight: FontWeight.w700,
        height: 1.1,
      ),
    );
  }
}
