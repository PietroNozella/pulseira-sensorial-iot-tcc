import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../services/storage_service.dart';

/// Provider responsável por resolver o identificador do usuário autenticado.
///
/// O fluxo lê o token salvo localmente, decodifica o payload JWT e tenta
/// extrair o claim principal para exibição na camada de apresentação.
///
/// Retorna uma [String] com o identificador do usuário ou um fallback estável
/// quando o token está ausente, inválido ou incompleto.
final authProvider = FutureProvider<String>((ref) async {
  final storage = StorageService();

  final storedUserName = await storage.getUserName();
  if (storedUserName != null && storedUserName.trim().isNotEmpty) {
    return storedUserName.trim();
  }

  // Inicia pela fonte local de sessão para evitar chamadas remotas apenas para
  // exibição de identidade básica no perfil.
  final token = await storage.getToken();

  // Fallback defensivo: garante rótulo padrão quando não há sessão ativa.
  if (token == null || token.isEmpty) {
    return 'Usuario';
  }

  // Valida a estrutura mínima do JWT antes da etapa de decodificação.
  final tokenParts = token.split('.');
  if (tokenParts.length < 2) {
    return 'Usuario';
  }

  try {
    // Normaliza e decodifica o payload para suportar variações de padding
    // Base64URL e manter robustez entre provedores de autenticação.
    final normalizedPayload = base64Url.normalize(tokenParts[1]);
    final payloadJson = utf8.decode(base64Url.decode(normalizedPayload));
    final payload = jsonDecode(payloadJson) as Map<String, dynamic>;

    // TODO: trocar para nome quando o cadastro/login persistir e retornar nome corretamente.

    // Usa o claim de assunto como identificador provisório para exibição.
    final email = payload['sub'];
    if (email is String && email.trim().isNotEmpty) {
      return email.trim();
    }
  } catch (_) {
    // Se o token estiver malformado, mantemos fallback para não quebrar a UI.
  }

  return 'Usuario';
});
