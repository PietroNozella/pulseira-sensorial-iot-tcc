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
  static const String baseUrl = "https://fallsense-api.onrender.com/auth";
  static const Duration requestTimeout = Duration(seconds: 15);

  Future<Map<String, dynamic>> registrar({
    required String nome,
    required String email,
    required String telefone,
    required String senha,
  }) async {
    return _sendRequest(
      'POST /auth/registrar',
      () => http.post(
        Uri.parse('$baseUrl/registrar'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "nome_completo": nome,
          "email": email,
          "telefone": telefone,
          "senha": senha,
        }),
      ),
    );
  }

  Future<Map<String, dynamic>> login({
    required String email,
    required String senha,
    String? codigo2fa,
  }) async {
    return _sendRequest(
      'POST /auth/login',
      () => http.post(
        Uri.parse('$baseUrl/login'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "email": email,
          "senha": senha,
          "codigo_2fa": codigo2fa,
        }),
      ),
    );
  }

  Future<Map<String, dynamic>> solicitarRecuperacao(String email) async {
    return _sendRequest(
      'POST /auth/esqueci-senha',
      () => http.post(
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
      () => http.post(
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
      () => http.get(
        Uri.parse('$baseUrl/me'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      ),
    );
  }

  Future<Map<String, dynamic>> obterMonitorados(String token) async {
    return _sendRequest(
      'GET /monitorados',
      () => http.get(
        Uri.parse('https://fallsense-api.onrender.com/monitorados'),
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
      () => http.get(
        Uri.parse('https://fallsense-api.onrender.com/pulseiras'),
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
      () => http.get(
        Uri.parse('https://fallsense-api.onrender.com/eventos'),
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
