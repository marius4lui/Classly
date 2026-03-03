import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/shared/widgets/app_text_field.dart';
import 'package:classly_mobile/shared/widgets/primary_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../domain/auth_repository.dart';

class InstanceSelectScreen extends ConsumerStatefulWidget {
  const InstanceSelectScreen({super.key});

  @override
  ConsumerState<InstanceSelectScreen> createState() =>
      _InstanceSelectScreenState();
}

class _InstanceSelectScreenState extends ConsumerState<InstanceSelectScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: ref.read(sessionBootstrapProvider).baseUrl ?? '',
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final baseUrl = _controller.text.trim();
    await ref.read(authRepositoryProvider).saveBaseUrl(baseUrl);
    ref.read(sessionBootstrapControllerProvider.notifier).setBaseUrl(baseUrl);

    if (!mounted) {
      return;
    }

    final router = GoRouter.maybeOf(context);
    if (router != null) {
      router.go('/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          'Instanz waehlen',
                          style: theme.textTheme.headlineMedium,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Verbinde die App mit deiner Classly-Instanz. '
                          'Self-hosted und Cloud-Instanzen werden gleich behandelt.',
                          style: theme.textTheme.bodyMedium,
                        ),
                        const SizedBox(height: 24),
                        AppTextField(
                          controller: _controller,
                          label: 'Base URL',
                          hintText: 'https://classly.site',
                          keyboardType: TextInputType.url,
                          textInputAction: TextInputAction.done,
                          validator: _validateBaseUrl,
                        ),
                        const SizedBox(height: 20),
                        PrimaryButton(label: 'Weiter', onPressed: _submit),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  String? _validateBaseUrl(String? value) {
    final raw = value?.trim() ?? '';
    final uri = Uri.tryParse(raw);

    if (uri == null || !uri.hasScheme || !uri.hasAuthority) {
      return 'Bitte eine gueltige https:// URL eingeben';
    }

    if (uri.scheme != 'https') {
      return 'Bitte eine gueltige https:// URL eingeben';
    }

    return null;
  }
}
