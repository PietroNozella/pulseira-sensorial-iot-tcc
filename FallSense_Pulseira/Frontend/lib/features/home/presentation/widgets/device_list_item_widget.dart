import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import 'device_status_widget.dart';

/// Card de resumo do dispositivo IoT exibido na Home.
///
/// Consolida os sinais essenciais para tomada de decisão rápida do cuidador:
/// identificação da pulseira, estado de conectividade e nível de bateria.
class DeviceListItemWidget extends StatelessWidget {
  /// Cria o card do dispositivo com configuração imutável.
  const DeviceListItemWidget({
    super.key,
  });

  /// Monta a estrutura visual principal do status da pulseira.
  ///
  /// A composição privilegia leitura rápida em dois blocos: contexto do
  /// dispositivo à esquerda e energia à direita, reduzindo esforço cognitivo
  /// em cenários de monitoramento contínuo.
  @override
  Widget build(BuildContext context) {
    return Container(
      // Bloco de identidade visual do card: contraste, profundidade e formato
      // para destacar informações críticas no topo da Home.
      constraints: const BoxConstraints(minHeight: 140),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.primary,
        borderRadius: BorderRadius.circular(18),
        boxShadow: const <BoxShadow>[
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 14,
            offset: Offset(0, 6),
          ),
        ],
      ),

      // Bloco de conteúdo funcional:
      // - Esquerda: identificação da pulseira e status de conexão.
      // - Direita: leitura resumida do nível de bateria.
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                Icon(
                  Icons.watch,
                  color: AppColors.white,
                  size: 30,
                ),
                SizedBox(width: 12),
                Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        'Pulseira Vo Maria',
                        style: TextStyle(
                          color: AppColors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      SizedBox(height: 8),
                      DeviceStatusWidget(color: AppColors.white),
                    ],
                  ),
                ),
              ],
            ),
          ),
          SizedBox(width: 16),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              Text(
                'Bateria',
                style: TextStyle(
                  color: AppColors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
              SizedBox(height: 4),
              Row(
                children: <Widget>[
                  Icon(
                    Icons.battery_5_bar_rounded,
                    color: AppColors.white,
                  ),
                  SizedBox(width: 6),
                  Text(
                    '85%',
                    style: TextStyle(
                      color: AppColors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}