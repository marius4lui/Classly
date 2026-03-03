import 'package:flutter/material.dart';

class AppTextField extends StatelessWidget {
  const AppTextField({
    this.label,
    this.hintText,
    this.controller,
    this.validator,
    this.onChanged,
    this.keyboardType,
    this.textInputAction,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.autofillHints,
    super.key,
  });

  final String? label;
  final String? hintText;
  final TextEditingController? controller;
  final FormFieldValidator<String>? validator;
  final ValueChanged<String>? onChanged;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final Iterable<String>? autofillHints;

  @override
  Widget build(BuildContext context) {
    final children = <Widget>[];
    final labelText = label;

    if (labelText != null) {
      children.add(
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Text(
            labelText,
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
              color: Theme.of(context).colorScheme.onSurface,
            ),
          ),
        ),
      );
    }

    children.add(
      TextFormField(
        controller: controller,
        validator: validator,
        onChanged: onChanged,
        keyboardType: keyboardType,
        textInputAction: textInputAction,
        obscureText: obscureText,
        autofillHints: autofillHints,
        decoration: InputDecoration(
          hintText: hintText,
          prefixIcon: prefixIcon,
          suffixIcon: suffixIcon,
        ),
      ),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: children,
    );
  }
}
