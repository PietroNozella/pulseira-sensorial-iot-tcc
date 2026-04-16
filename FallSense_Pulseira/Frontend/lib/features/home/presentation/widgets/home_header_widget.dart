import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

/// Cabeçalho da Home com saudação contextual e atalho de notificações.
///
/// Este componente reforça orientação do usuário na tela inicial ao exibir
/// identificação pessoal e um ponto de entrada para eventos importantes.
class HomeHeaderWidget extends StatelessWidget {
  /// Cria o cabeçalho com o nome do usuário exibido na saudação.
  ///
  /// [userName] representa o nome curto usado para personalizar a experiência.
  const HomeHeaderWidget({
    required this.userName,
    super.key,
  });

  /// Nome utilizado na mensagem de boas-vindas do topo da Home.
  final String userName;

  /// Monta a faixa superior da Home priorizando identificação e ação rápida.
  ///
  /// O layout horizontal mantém a saudação em destaque e preserva espaço para
  /// evolução futura do fluxo de notificações sem reestruturar a tela.
  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        // Bloco de contexto do usuário: prioriza leitura da saudação com largura
        // flexível para evitar truncamento prematuro em telas menores.
        Expanded(
          child: Text(
            'Olá, $userName!',
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 24,
              fontWeight: FontWeight.w700,
            ),
          ),
        ),

        // Bloco de ação rápida: reserva o ponto de interação para alertas e
        // notificações do monitoramento sem competir com a saudação.
        IconButton(
          onPressed: () {},
          icon: const Icon(
            Icons.notifications_none_rounded,
            color: AppColors.textPrimary,
          ),
          tooltip: 'Notificações',
        ),
      ],
    );
  }
}
