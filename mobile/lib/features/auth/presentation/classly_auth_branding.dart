import 'package:classly_mobile/app/theme/app_colors.dart';
import 'package:flutter/material.dart';

class ClasslyAuthBranding extends StatelessWidget {
  const ClasslyAuthBranding({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 68,
          height: 68,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppColors.border),
            boxShadow: const [
              BoxShadow(
                color: Color(0x120F172A),
                blurRadius: 28,
                offset: Offset(0, 18),
              ),
            ],
          ),
          child: Image.asset('assets/classly-logo.png', fit: BoxFit.contain),
        ),
        const SizedBox(height: 20),
        Text(
          'Fuer Schulklassen gemacht',
          style: theme.textTheme.labelLarge?.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 10),
        Text('Classly Mobile', style: theme.textTheme.headlineLarge),
        const SizedBox(height: 12),
        Text(
          'Kalender, Hausaufgaben und wichtige Infos in einer klaren App. '
          'Standardmaessig verbindest du dich direkt mit Classly Cloud.',
          style: theme.textTheme.bodyLarge?.copyWith(
            color: AppColors.textSecondary,
            height: 1.45,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          decoration: BoxDecoration(
            color: const Color(0xFFF7F9FC),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: AppColors.border),
          ),
          child: Wrap(
            crossAxisAlignment: WrapCrossAlignment.center,
            spacing: 10,
            children: [
              Container(
                width: 8,
                height: 8,
                margin: const EdgeInsets.only(bottom: 1),
                decoration: const BoxDecoration(
                  color: Color(0xFF16A34A),
                  shape: BoxShape.circle,
                ),
              ),
              Text(
                'Kostenlos und Open Source',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
