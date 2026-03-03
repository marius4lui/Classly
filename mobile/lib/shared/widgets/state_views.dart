import 'package:classly_mobile/app/theme/app_colors.dart';
import 'package:classly_mobile/shared/widgets/primary_button.dart';
import 'package:flutter/material.dart';

class LoadingStateView extends StatelessWidget {
  const LoadingStateView({this.label = 'Daten werden geladen', super.key});

  final String label;

  @override
  Widget build(BuildContext context) {
    return _StateCard(
      icon: const CircularProgressIndicator(),
      title: 'Einen Moment',
      message: label,
    );
  }
}

class EmptyStateView extends StatelessWidget {
  const EmptyStateView({
    required this.title,
    required this.message,
    this.actionLabel,
    this.onAction,
    super.key,
  });

  final String title;
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    return _StateCard(
      icon: const _StateIcon(
        icon: Icons.event_busy_outlined,
        color: AppColors.info,
      ),
      title: title,
      message: message,
      action: actionLabel == null
          ? null
          : PrimaryButton(
              label: actionLabel!,
              expanded: false,
              tone: PrimaryButtonTone.subtle,
              onPressed: onAction,
            ),
    );
  }
}

class ErrorStateView extends StatelessWidget {
  const ErrorStateView({
    required this.title,
    required this.message,
    this.actionLabel = 'Erneut versuchen',
    this.onAction,
    super.key,
  });

  final String title;
  final String message;
  final String actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    return _StateCard(
      icon: const _StateIcon(
        icon: Icons.wifi_off_rounded,
        color: AppColors.danger,
      ),
      title: title,
      message: message,
      action: PrimaryButton(
        label: actionLabel,
        expanded: false,
        onPressed: onAction,
      ),
    );
  }
}

class _StateCard extends StatelessWidget {
  const _StateCard({
    required this.icon,
    required this.title,
    required this.message,
    this.action,
  });

  final Widget icon;
  final String title;
  final String message;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Center(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 420),
        margin: const EdgeInsets.all(24),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: theme.colorScheme.surface,
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: AppColors.border),
          boxShadow: const [
            BoxShadow(
              color: Color(0x120A1730),
              blurRadius: 28,
              offset: Offset(0, 12),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            icon,
            const SizedBox(height: 18),
            Text(
              title,
              style: theme.textTheme.titleLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: theme.textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            if (action != null) ...[const SizedBox(height: 20), action!],
          ],
        ),
      ),
    );
  }
}

class _StateIcon extends StatelessWidget {
  const _StateIcon({required this.icon, required this.color});

  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 72,
      width: 72,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Icon(icon, color: color, size: 32),
    );
  }
}
