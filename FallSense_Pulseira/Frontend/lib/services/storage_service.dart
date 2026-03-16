import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class StorageService {
  // Criamos o objeto que representa o cofre seguro do celular
  final _storage = const FlutterSecureStorage();

  // Função para GUARDAR o token (Tarefa 4.3 do seu TCC)
  // Chamamos isso quando o login ou 2FA der certo
  Future<void> saveToken(String token) async {
    // 'jwt_token' é o nome da "gaveta" dentro do cofre
    await _storage.write(key: 'jwt_token', value: token);
  }

  // Função para LER o token (Para saber se o usuário já está logado)
  Future<String?> getToken() async {
    return await _storage.read(key: 'jwt_token');
  }

  // Função para APAGAR o token (Tarefa 4.4 - Logout)
  // Chamamos isso quando o usuário clica em "Sair"
  Future<void> deleteToken() async {
    await _storage.delete(key: 'jwt_token');
  }
}