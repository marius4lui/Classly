import 'package:classly_mobile/app/bootstrap/bootstrap.dart';
import 'package:classly_mobile/app/theme/app_colors.dart';
import 'package:classly_mobile/features/auth/application/auth_flow_launcher.dart';
import 'package:classly_mobile/shared/widgets/app_text_field.dart';
import 'package:classly_mobile/shared/widgets/primary_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/auth_providers.dart';
import 'classly_auth_branding.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _controller;
  bool _advancedExpanded = false;
  bool _isLaunching = false;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(
      text: ref.read(sessionBootstrapProvider).baseUrl ?? defaultClasslyBaseUrl,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _saveCustomInstance() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    final baseUrl = _controller.text.trim();
    await ref.read(authRepositoryProvider).saveBaseUrl(baseUrl);
    ref.read(sessionBootstrapControllerProvider.notifier).setBaseUrl(baseUrl);

    if (!mounted) {
      return;
    }

    FocusScope.of(context).unfocus();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Eigene Instanz gespeichert.')),
    );
  }

  Future<void> _startLogin() async {
    setState(() {
      _isLaunching = true;
    });

    try {
      final baseUrl =
          ref.read(sessionBootstrapProvider).baseUrl ?? defaultClasslyBaseUrl;
      await ref.read(authFlowLauncherProvider).startLogin(baseUrl);
    } catch (error) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error.toString().replaceFirst('Exception: ', '')),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLaunching = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final bootstrap = ref.watch(sessionBootstrapProvider);
    final theme = Theme.of(context);
    final activeBaseUrl = bootstrap.baseUrl ?? defaultClasslyBaseUrl;
    final isDefaultInstance = activeBaseUrl == defaultClasslyBaseUrl;

    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFF8FBFF), Color(0xFFF2F5FB)],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 460),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const ClasslyAuthBranding(),
                        const SizedBox(height: 28),
                        Text(
                          'Mit Classly anmelden',
                          style: theme.textTheme.headlineMedium,
                        ),
                        const SizedBox(height: 10),
                        Text(
                          isDefaultInstance
                              ? 'Du startest direkt mit der offiziellen Classly-Instanz.'
                              : 'Deine benutzerdefinierte Instanz ist fuer den Login aktiv.',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: AppColors.border),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Aktive Instanz',
                                style: theme.textTheme.labelMedium,
                              ),
                              const SizedBox(height: 6),
                              SelectableText(
                                activeBaseUrl,
                                style: theme.textTheme.titleMedium,
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 20),
                        PrimaryButton(
                          label: 'OAuth im Browser starten',
                          isLoading: _isLaunching,
                          onPressed: _startLogin,
                        ),
                        const SizedBox(height: 10),
                        Align(
                          alignment: Alignment.centerLeft,
                          child: TextButton(
                            onPressed: () {
                              setState(() {
                                _advancedExpanded = !_advancedExpanded;
                              });
                            },
                            style: TextButton.styleFrom(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 0,
                                vertical: 4,
                              ),
                              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            ),
                            child: Text(
                              _advancedExpanded
                                  ? 'Advanced ausblenden'
                                  : 'Advanced',
                              style: theme.textTheme.labelMedium?.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ),
                        ),
                        if (_advancedExpanded)
                          Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: _AdvancedInstanceSection(
                              formKey: _formKey,
                              controller: _controller,
                              onSave: _saveCustomInstance,
                            ),
                          ),
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
}

class _AdvancedInstanceSection extends StatelessWidget {
  const _AdvancedInstanceSection({
    required this.formKey,
    required this.controller,
    required this.onSave,
  });

  final GlobalKey<FormState> formKey;
  final TextEditingController controller;
  final Future<void> Function() onSave;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFFF9FBFF),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.border),
      ),
      child: Form(
        key: formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Eigene Instanz', style: theme.textTheme.titleMedium),
            const SizedBox(height: 8),
            Text(
              'Nur fuer self-hosted Setups oder dedizierte Classly-Domains. '
              'Fuer die meisten Nutzer reicht der Standard-Login.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 16),
            AppTextField(
              controller: controller,
              label: 'Base URL',
              hintText: defaultClasslyBaseUrl,
              keyboardType: TextInputType.url,
              textInputAction: TextInputAction.done,
              validator: _validateBaseUrl,
            ),
            const SizedBox(height: 14),
            PrimaryButton(
              label: 'Instanz speichern',
              expanded: false,
              tone: PrimaryButtonTone.outline,
              onPressed: () {
                onSave();
              },
            ),
          ],
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
