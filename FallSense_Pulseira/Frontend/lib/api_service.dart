import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Mudamos para localhost (127.0.0.1) para rodar tudo na sua máquina
  static const String baseUrl = "http://127.0.0.1:8000/auth";

  // --- FUNÇÃO DE REGISTRO (Já existia) ---
  Future<bool> registrarNoBackend({
    required String nome,
    required String email,
    required String telefone,
    required String senha,
  }) async {
    try {
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
      return response.statusCode == 201;
    } catch (e) {
      print("Erro de conexão no Registro: $e");
      return false;
    }
  }

  // --- NOVA FUNÇÃO: SOLICITAR RECUPERAÇÃO ---
  Future<bool> solicitarRecuperacao(String email) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/esqueci-senha'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email}),
      );
      return response.statusCode == 200;
    } catch (e) {
      print("Erro ao solicitar recuperação: $e");
      return false;
    }
  }

  // --- NOVA FUNÇÃO: RESETAR SENHA ---
  Future<bool> resetarSenha(String token, String novaSenha) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/resetar-senha'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "token": token,
          "nova_senha": novaSenha,
        }),
      );
      return response.statusCode == 200;
    } catch (e) {
      print("Erro ao resetar senha: $e");
      return false;
    }
  }
}