import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../core/network/api_service.dart';
import '../../../../../services/storage_service.dart';

class AuthUserProfile {
  const AuthUserProfile({
    required this.name,
    required this.email,
  });

  final String name;
  final String email;
}

/// Provider responsável por resolver o perfil do usuário autenticado.
final userProfileProvider = FutureProvider<AuthUserProfile>((ref) async {
  final storage = StorageService();
  final token = await storage.getToken();

  if (token == null || token.isEmpty) {
    return const AuthUserProfile(name: 'Usuario', email: '');
  }

  try {
    final resultado = await ApiService().obterPerfil(token);
    final status = resultado['status'] as int;
    final body = resultado['body'] as Map<String, dynamic>;

    if (status == 200) {
      final nomeCompleto = (body['nome_completo'] as String?)?.trim();
      final email = (body['email'] as String?)?.trim() ?? '';
      final resolvedName = (nomeCompleto != null && nomeCompleto.isNotEmpty)
          ? nomeCompleto
          : (email.isNotEmpty ? email : 'Usuario');

      await storage.saveUserName(resolvedName);
      return AuthUserProfile(name: resolvedName, email: email);
    }
  } catch (_) {
    // Se a chamada remota falhar, fazemos fallback local para não quebrar a UI.
  }

  final storedUserName = await storage.getUserName();
  if (storedUserName != null && storedUserName.trim().isNotEmpty) {
    final fallbackEmail = await _extrairEmailDoToken(token);
    return AuthUserProfile(
      name: storedUserName.trim(),
      email: fallbackEmail,
    );
  }

  final email = await _extrairEmailDoToken(token);
  if (email.isNotEmpty) {
    return AuthUserProfile(name: email, email: email);
  }

  return const AuthUserProfile(name: 'Usuario', email: '');
});

/// Atalho compatível para widgets que só precisam do nome exibido.
final authProvider = FutureProvider<String>((ref) async {
  final profile = await ref.watch(userProfileProvider.future);
  return profile.name;
});

Future<String> _extrairEmailDoToken(String token) async {
  final tokenParts = token.split('.');
  if (tokenParts.length < 2) {
    return '';
  }

  try {
    final normalizedPayload = base64Url.normalize(tokenParts[1]);
    final payloadJson = utf8.decode(base64Url.decode(normalizedPayload));
    final payload = jsonDecode(payloadJson) as Map<String, dynamic>;
    final email = payload['sub'];

    if (email is String && email.trim().isNotEmpty) {
      return email.trim();
    }
  } catch (_) {
    return '';
  }

  return '';
}
