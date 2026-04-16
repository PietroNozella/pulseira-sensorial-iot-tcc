import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

/// Indicador visual compacto do estado de conectividade da pulseira.
///
/// Este componente padroniza a forma de exibir status em diferentes telas,
/// reduzindo inconsistências visuais e facilitando leitura rápida do estado.
class DeviceStatusWidget extends StatelessWidget {
  /// Cria o indicador de status com cor customizável para adaptação ao contexto.
  ///
  /// Quando [color] não é informado, utiliza a cor de sucesso do tema para
  /// representar o estado conectado de forma semanticamente consistente.
  const DeviceStatusWidget({
    this.color = AppColors.success,
    super.key,
  });

  /// Cor aplicada ao marcador e ao texto de status.
  final Color color;

  /// Monta o selo de status com ícone e texto em layout horizontal compacto.
  ///
  /// O formato reduzido permite reutilização em cards densos sem comprometer
  /// legibilidade, especialmente em cenários de monitoramento contínuo.
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: <Widget>[
        // Bloco de semântica visual imediata: ponto circular para leitura rápida
        // de estado mesmo em visões periféricas da interface.
        Icon(
          Icons.circle,
          size: 10,
          color: color,
        ),
        const SizedBox(width: 6),

        // Bloco textual de confirmação explícita para reduzir ambiguidade do ícone.
        Text(
          'Conectada',
          style: TextStyle(
            color: color,
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
