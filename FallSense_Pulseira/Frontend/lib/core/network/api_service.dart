import 'dart:convert';
import 'package:http/http.dart' as http;

// Centraliza todas as chamadas HTTP ao backend, evitando duplicação nas screens
class ApiService {
  static const String baseUrl = "https://fallsense-api.onrender.com/auth";

  // Retorna o body decodificado e o statusCode para o chamador tratar
  Future<Map<String, dynamic>> registrar({
    required String nome,
    required String email,
    required String telefone,
    required String senha,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/registrar'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "nome_completo": nome,
        "email": email,
        "telefone": telefone,
        "senha": senha,
      }),
    );
    return {"status": response.statusCode, "body": jsonDecode(response.body)};
  }

  // Primeira chamada de login (sem 2FA); retorna requer_2fa ou access_token
  Future<Map<String, dynamic>> login({
    required String email,
    required String senha,
    String? codigo2fa,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/login'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "email": email,
        "senha": senha,
        "codigo_2fa": codigo2fa,
      }),
    );
    return {"status": response.statusCode, "body": jsonDecode(response.body)};
  }

  // Solicita envio do código de recuperação por e-mail
  Future<Map<String, dynamic>> solicitarRecuperacao(String email) async {
    final response = await http.post(
      Uri.parse('$baseUrl/esqueci-senha'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"email": email}),
    );
    return {"status": response.statusCode, "body": jsonDecode(response.body)};
  }

  // Envia token + nova senha para concluir o reset
  Future<Map<String, dynamic>> resetarSenha({
    required String token,
    required String novaSenha,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/resetar-senha'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "token": token,
        "nova_senha": novaSenha,
      }),
    );
    return {"status": response.statusCode, "body": jsonDecode(response.body)};
  }

  Future<Map<String, dynamic>> obterPerfil(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/me'),
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer $token",
      },
    );
    return {"status": response.statusCode, "body": jsonDecode(response.body)};
  }

  Future<Map<String, dynamic>> obterMonitorados(String token) async {
    final response = await http.get(
      Uri.parse('https://fallsense-api.onrender.com/monitorados'),
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer $token",
      },
    );
    return {"status": response.statusCode, "body": jsonDecode(response.body)};
  }
}
