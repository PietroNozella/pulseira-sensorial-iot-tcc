import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // ATENÇÃO: Peça para seu amigo o IP da máquina dele. 
  // Se estiverem na mesma rede, será algo como "192.168.0.XX"
  static const String baseUrl = "http://192.168.0.XXX:8000/auth";

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
          "nome_completo": nome, // Exatamente como no RegistroPayload do Python
          "email": email,
          "telefone": telefone,
          "senha": senha,
        }),
      );

      // Status 201 significa "Criado com sucesso" no FastAPI
      return response.statusCode == 201;
    } catch (e) {
      print("Erro de conexão: $e");
      return false;
    }
  }
}