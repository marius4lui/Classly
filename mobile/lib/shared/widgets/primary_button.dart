import 'package:classly_mobile/app/theme/app_colors.dart';
import 'package:flutter/material.dart';

enum PrimaryButtonTone { filled, subtle, outline }

class PrimaryButton extends StatelessWidget {
  const PrimaryButton({
    required this.label,
    this.onPressed,
    this.leading,
    this.isLoading = false,
    this.expanded = true,
    this.tone = PrimaryButtonTone.filled,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final Widget? leading;
  final bool isLoading;
  final bool expanded;
  final PrimaryButtonTone tone;

  @override
  Widget build(BuildContext context) {
    final disabled = onPressed == null || isLoading;
    final child = Row(
      mainAxisSize: MainAxisSize.max,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (isLoading)
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: SizedBox(
              height: 18,
              width: 18,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: _foregroundColor(context),
              ),
            ),
          )
        else if (leading != null)
          Padding(padding: const EdgeInsets.only(right: 10), child: leading),
        Flexible(
          child: Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );

    final button = switch (tone) {
      PrimaryButtonTone.filled => FilledButton(
        onPressed: disabled ? null : onPressed,
        child: child,
      ),
      PrimaryButtonTone.subtle => FilledButton(
        style: FilledButton.styleFrom(
          backgroundColor: const Color(0xFFEAF0FF),
          foregroundColor: AppColors.brand,
        ),
        onPressed: disabled ? null : onPressed,
        child: child,
      ),
      PrimaryButtonTone.outline => OutlinedButton(
        onPressed: disabled ? null : onPressed,
        child: child,
      ),
    };

    if (!expanded) {
      return button;
    }

    return SizedBox(width: double.infinity, child: button);
  }

  Color _foregroundColor(BuildContext context) {
    return switch (tone) {
      PrimaryButtonTone.filled => Theme.of(context).colorScheme.onPrimary,
      PrimaryButtonTone.subtle => AppColors.brand,
      PrimaryButtonTone.outline => Theme.of(context).colorScheme.onSurface,
    };
  }
}
