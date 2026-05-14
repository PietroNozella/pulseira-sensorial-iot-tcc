import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiRequestTimeoutException implements Exception {
  const ApiRequestTimeoutException(this.operacao, this.timeout);

  final String operacao;
  final Duration timeout;

  @override
  String toString() {
    return 'A operacao $operacao excedeu ${timeout.inSeconds}s.';
  }
}

class ApiService {
  factory ApiService() => _instance;

  ApiService._({http.Client? client}) : _client = client ?? http.Client();

  static final ApiService _instance = ApiService._();

  static const String apiUrl = "https://fallsense-api.onrender.com";
  static const String baseUrl = "$apiUrl/auth";
  static const Duration requestTimeout = Duration(seconds: 30);

  final http.Client _client;

  static String errorMessage(
    Map<String, dynamic> body,
    String fallback,
  ) {
    final detail = body['detail'];

    if (detail is List && detail.isNotEmpty) {
      final firstError = detail.first;
      if (firstError is Map && firstError['msg'] != null) {
        return firstError['msg'].toString().replaceAll('Value error, ', '');
      }
      return firstError.toString();
    }

    if (detail != null) {
      return detail.toString();
    }

    return fallback;
  }

  Future<Map<String, dynamic>> registrar({
    required String nome,
    required String email,
    required String telefone,
    required String senha,
    required bool termosAceitos, // Adicionado apenas este parâmetro
  }) async {
    return _sendRequest(
      'POST /auth/registrar',
      () => _client.post(
        Uri.parse('$baseUrl/registrar'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "nome_completo": nome,
          "email": email,
          "telefone": telefone,
          "senha": senha,
          "termos_aceitos": termosAceitos, // Adicionado o envio para o banco
        }),
      ),
    );
  }

  Future<Map<String, dynamic>> login({
    required String email,
    String? senha,
    String? codigo2fa,
    String? challengeId,
  }) async {
    return _sendRequest(
      'POST /auth/login',
      () => _client.post(
        Uri.parse('$baseUrl/login'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "email": email,
          "senha": senha,
          "codigo_2fa": codigo2fa,
          "challenge_id": challengeId,
        }),
      ),
    );
  }

  Future<Map<String, dynamic>> solicitarRecuperacao(String email) async {
    return _sendRequest(
      'POST /auth/esqueci-senha',
      () => _client.post(
        Uri.parse('$baseUrl/esqueci-senha'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email}),
      ),
    );
  }

  Future<Map<String, dynamic>> resetarSenha({
    required String token,
    required String novaSenha,
  }) async {
    return _sendRequest(
      'POST /auth/resetar-senha',
      () => _client.post(
        Uri.parse('$baseUrl/resetar-senha'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "token": token,
          "nova_senha": novaSenha,
        }),
      ),
    );
  }

  Future<Map<String, dynamic>> obterPerfil(String token) async {
    return _sendRequest(
      'GET /auth/me',
      () => _client.get(
        Uri.parse('$baseUrl/me'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
    );
  }

  Future<Map<String, dynamic>> atualizarPerfil({
    required String token,
    required String nome,
    required String email,
    required String telefone,
  }) async {
    return _sendRequest(
      'PATCH /auth/me',
      () => _client.patch(
        Uri.parse('$baseUrl/me'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
        body: jsonEncode({
          "nome_completo": nome,
          "email": email,
          "telefone": telefone,
        }),
      ),
    );
  }

  Future<Map<String, dynamic>> alterarSenha({
    required String token,
    required String senhaAtual,
    required String novaSenha,
  }) async {
    return _sendRequest(
      'PATCH /auth/me/senha',
      () => _client.patch(
        Uri.parse('$baseUrl/me/senha'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
        body: jsonEncode({
          "senha_atual": senhaAtual,
          "nova_senha": novaSenha,
        }),
      ),
    );
  }

  Future<Map<String, dynamic>> excluirConta({
    required String token,
    required String senha,
  }) async {
    return _sendRequest(
      'DELETE /auth/me',
      () => _client.delete(
        Uri.parse('$baseUrl/me'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
        body: jsonEncode({"senha": senha}),
      ),
    );
  }

  Future<Map<String, dynamic>> obterMonitorados(String token) async {
    return _sendRequest(
      'GET /monitorados',
      () => _client.get(
        Uri.parse('$apiUrl/monitorados'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
    );
  }

  Future<Map<String, dynamic>> obterPulseiras(String token) async {
    return _sendRequest(
      'GET /pulseiras',
      () => _client.get(
        Uri.parse('$apiUrl/pulseiras'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
    );
  }

  Future<Map<String, dynamic>> obterEventos(String token) async {
    return _sendRequest(
      'GET /eventos',
      () => _client.get(
        Uri.parse('$apiUrl/eventos'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
    );
  }

  Future<Map<String, dynamic>> _sendRequest(
    String operacao,
    Future<http.Response> Function() request,
  ) async {
    final stopwatch = Stopwatch()..start();

    try {
      final response = await request().timeout(requestTimeout);
      final body = _decodeBody(response.body);

      if (kDebugMode) {
        debugPrint(
          '[ApiService] $operacao -> ${response.statusCode} em ${stopwatch.elapsedMilliseconds}ms',
        );
      }

      return {"status": response.statusCode, "body": body};
    } on TimeoutException {
      if (kDebugMode) {
        debugPrint(
          '[ApiService] $operacao -> timeout apos ${stopwatch.elapsedMilliseconds}ms',
        );
      }
      throw ApiRequestTimeoutException(operacao, requestTimeout);
    } finally {
      stopwatch.stop();
    }
  }

  Map<String, dynamic> _decodeBody(String responseBody) {
    if (responseBody.isEmpty) {
      return {};
    }

    final decoded = jsonDecode(responseBody);
    if (decoded is Map<String, dynamic>) {
      return decoded;
    }

    return {"data": decoded};
  }
}