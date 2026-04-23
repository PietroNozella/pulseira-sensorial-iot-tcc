import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../widgets/device_list_item_widget.dart';
import '../widgets/fall_simulation_card_widget.dart';
import '../widgets/home_header_widget.dart';

/// Tela inicial do aplicativo após autenticação.
///
/// Centraliza os principais pontos de interação do usuário no contexto do TCC:
/// identificação do usuário, status resumido do dispositivo IoT e um painel de
/// simulação para validar o fluxo de detecção de queda em ambiente controlado.
class HomeScreen extends ConsumerWidget {
  /// Cria a HomeScreen com configuração imutável para renderização previsível.
  const HomeScreen({
    super.key,
  });

  /// Monta a composição visual da Home com foco em leitura sequencial dos blocos.
  ///
  /// A organização em lista vertical facilita evolução incremental de conteúdo
  /// sem acoplamento entre os componentes, alinhando com a arquitetura em camadas.
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userNameAsync = ref.watch(authProvider);
    final monitoredPeopleAsync = ref.watch(monitoredPeopleProvider);
    final userName = userNameAsync.maybeWhen(
      data: (value) => value,
      orElse: () => 'Usuario',
    );
    final monitoredPeople = monitoredPeopleAsync.maybeWhen(
      data: (value) => value,
      orElse: () => const <MonitoredPerson>[],
    );
    final hasMonitoredPerson = monitoredPeople.isNotEmpty;
    final monitoredPersonName = hasMonitoredPerson
        ? monitoredPeople.first.name
        : 'Nenhuma pessoa monitorada';

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: ListView(
          children: <Widget>[
            // Bloco de contexto do usuário: saudação e ações rápidas do topo.
            HomeHeaderWidget(userName: userName),
            const SizedBox(height: 20),

            // Bloco de status operacional: resumo visual da pulseira conectada.
            DeviceListItemWidget(
              monitoredPersonName: monitoredPersonName,
              hasMonitoredPerson: hasMonitoredPerson,
            ),
            const SizedBox(height: 16),

            // Bloco de entrada para o painel principal da funcionalidade crítica.
            const Text(
              'Painel Principal',
              style: TextStyle(
                color: AppColors.textPrimary,
                fontSize: 24,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 16),

            // Bloco de simulação: permite validar o cenário de queda no front-end.
            const FallSimulationCardWidget(),
          ],
        ),
      ),
    );
  }
}
