import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../../core/network/api_service.dart';
import '../../../../../services/storage_service.dart';

class AuthUserProfile {
  const AuthUserProfile({
    required this.name,
    required this.email,
    this.phone = '',
  });

  final String name;
  final String email;
  final String phone;
}

class MonitoredPerson {
  const MonitoredPerson({
    required this.id,
    required this.name,
  });

  final int id;
  final String name;
}

class WearableDevice {
  const WearableDevice({
    required this.macAddress,
    required this.monitoredPersonId,
    required this.monitoredPersonName,
    required this.firmwareVersion,
    required this.isActive,
  });

  final String macAddress;
  final int? monitoredPersonId;
  final String monitoredPersonName;
  final String firmwareVersion;
  final bool isActive;
}

class TelemetryEvent {
  const TelemetryEvent({
    required this.id,
    required this.type,
    required this.macAddress,
    required this.monitoredPersonName,
    required this.gpsCoordinates,
    required this.occurredAt,
  });

  final int id;
  final String type;
  final String macAddress;
  final String monitoredPersonName;
  final String gpsCoordinates;
  final DateTime? occurredAt;
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
      final telefone = (body['telefone'] as String?)?.trim() ?? (body['phone'] as String?)?.trim() ?? '';
      final resolvedName = (nomeCompleto != null && nomeCompleto.isNotEmpty)
          ? nomeCompleto
          : (email.isNotEmpty ? email : 'Usuario');

      await storage.saveUserName(resolvedName);
      return AuthUserProfile(name: resolvedName, email: email, phone: telefone);
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

final monitoredPeopleProvider = FutureProvider<List<MonitoredPerson>>((ref) async {
  final token = await StorageService().getToken();
  if (token == null || token.isEmpty) {
    return const <MonitoredPerson>[];
  }

  try {
    final resultado = await ApiService().obterMonitorados(token);
    final status = resultado['status'] as int;
    final body = resultado['body'];

    if (status == 200 && body is List) {
      return body
          .whereType<Map<String, dynamic>>()
          .map((item) => MonitoredPerson(
                id: item['id'] as int,
                name: (item['nome_completo'] as String?)?.trim().isNotEmpty == true
                    ? (item['nome_completo'] as String).trim()
                    : 'Pessoa monitorada',
              ))
          .toList();
    }
  } catch (_) {
    return const <MonitoredPerson>[];
  }

  return const <MonitoredPerson>[];
});

final wearableDevicesProvider = FutureProvider<List<WearableDevice>>((ref) async {
  final token = await StorageService().getToken();
  if (token == null || token.isEmpty) {
    return const <WearableDevice>[];
  }

  try {
    final resultado = await ApiService().obterPulseiras(token);
    final status = resultado['status'] as int;
    final body = resultado['body'];

    if (status == 200 && body is List) {
      return body
          .whereType<Map<String, dynamic>>()
          .map((item) => WearableDevice(
                macAddress: (item['mac_address'] as String?)?.trim() ?? '',
                monitoredPersonId: item['pessoa_monitorada_id'] as int?,
                monitoredPersonName:
                    (item['pessoa_monitorada_nome'] as String?)?.trim() ?? '',
                firmwareVersion: (item['versao_firmware'] as String?)?.trim() ?? '',
                isActive: item['status_ativo'] as bool? ?? false,
              ))
          .where((device) => device.macAddress.isNotEmpty)
          .toList();
    }
  } catch (_) {
    return const <WearableDevice>[];
  }

  return const <WearableDevice>[];
});

final telemetryEventsProvider = FutureProvider<List<TelemetryEvent>>((ref) async {
  final token = await StorageService().getToken();
  if (token == null || token.isEmpty) {
    return const <TelemetryEvent>[];
  }

  try {
    final resultado = await ApiService().obterEventos(token);
    final status = resultado['status'] as int;
    final body = resultado['body'];

    if (status == 200 && body is List) {
      return body
          .whereType<Map<String, dynamic>>()
          .map((item) => TelemetryEvent(
                id: item['id'] as int,
                type: (item['tipo_evento'] as String?)?.trim() ?? 'EVENTO',
                macAddress: (item['mac_address'] as String?)?.trim() ?? '',
                monitoredPersonName:
                    (item['pessoa_monitorada_nome'] as String?)?.trim() ?? '',
                gpsCoordinates: (item['coordenadas_gps'] as String?)?.trim() ?? '',
                occurredAt: _parseDateTime(item['data_evento']),
              ))
          .toList();
    }
  } catch (_) {
    return const <TelemetryEvent>[];
  }

  return const <TelemetryEvent>[];
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

DateTime? _parseDateTime(Object? value) {
  if (value is! String || value.trim().isEmpty) {
    return null;
  }

  try {
    return DateTime.parse(value);
  } catch (_) {
    return null;
  }
}
