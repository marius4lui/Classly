import 'package:classly_mobile/app/theme/app_colors.dart';
import 'package:classly_mobile/features/events/domain/event.dart';
import 'package:flutter/material.dart';

class EventCard extends StatelessWidget {
  const EventCard({required this.event, this.onTap, super.key});

  final Event event;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final badgeColor = _badgeColor(event.type);

    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(24),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: badgeColor.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      event.type,
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: badgeColor,
                      ),
                    ),
                  ),
                  const Spacer(),
                  Text(
                    _formatDate(event.date),
                    style: theme.textTheme.labelMedium,
                  ),
                ],
              ),
              const SizedBox(height: 14),
              Text(event.title, style: theme.textTheme.titleLarge),
              const SizedBox(height: 8),
              Text(event.subjectName, style: theme.textTheme.bodyMedium),
            ],
          ),
        ),
      ),
    );
  }

  static String formatDate(DateTime date) => _formatDate(date);

  static String _formatDate(DateTime date) {
    final normalized = date.toLocal();
    final day = normalized.day.toString().padLeft(2, '0');
    final month = normalized.month.toString().padLeft(2, '0');
    final year = normalized.year.toString();
    return '$day.$month.$year';
  }

  Color _badgeColor(String type) {
    return switch (type) {
      'KA' => AppColors.danger,
      'TEST' => AppColors.warning,
      'HA' => AppColors.brand,
      _ => AppColors.info,
    };
  }
}
