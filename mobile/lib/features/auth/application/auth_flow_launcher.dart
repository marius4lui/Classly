import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../providers/auth_providers.dart';

abstract class AuthFlowLauncher {
  Future<void> startLogin(String baseUrl);
}

class ExternalBrowserAuthFlowLauncher implements AuthFlowLauncher {
  ExternalBrowserAuthFlowLauncher({required this.ref});

  final Ref ref;

  @override
  Future<void> startLogin(String baseUrl) async {
    final uri = ref
        .read(authRepositoryProvider)
        .buildAuthorizeUri(baseUrl: baseUrl);

    final launched = await launchUrl(uri, mode: LaunchMode.externalApplication);

    if (!launched) {
      throw Exception('OAuth-Browser konnte nicht geoeffnet werden.');
    }
  }
}

final authFlowLauncherProvider = Provider<AuthFlowLauncher>((ref) {
  return ExternalBrowserAuthFlowLauncher(ref: ref);
});
