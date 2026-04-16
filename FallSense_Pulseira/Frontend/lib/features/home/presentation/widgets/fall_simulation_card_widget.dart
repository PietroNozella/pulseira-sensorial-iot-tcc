import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

class FallSimulationCardWidget extends StatefulWidget {
  const FallSimulationCardWidget({
    super.key,
  });

  @override
  State<FallSimulationCardWidget> createState() =>
      _FallSimulationCardWidgetState();
}

class _FallSimulationCardWidgetState extends State<FallSimulationCardWidget> {
  bool _quedaDetectada = false;
  DateTime? _momentoDeteccao;

  void _alternarSimulacaoQueda() {
    setState(() {
      _quedaDetectada = !_quedaDetectada;
      _momentoDeteccao = _quedaDetectada ? DateTime.now() : null;
    });
  }

  String _formatarDataHora(DateTime dataHora) {
    final String dia = dataHora.day.toString().padLeft(2, '0');
    final String mes = dataHora.month.toString().padLeft(2, '0');
    final String ano = dataHora.year.toString();
    final String hora = dataHora.hour.toString().padLeft(2, '0');
    final String minuto = dataHora.minute.toString().padLeft(2, '0');

    return '$dia/$mes/$ano - $hora:$minuto';
  }

  @override
  Widget build(BuildContext context) {
    final Color cardColor = _quedaDetectada ? AppColors.error : AppColors.surface;
    final Color titleColor =
        _quedaDetectada ? AppColors.white : AppColors.textPrimary;
    final Color subtitleColor =
        _quedaDetectada ? AppColors.white : AppColors.textSecondary;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(
          color: _quedaDetectada ? AppColors.transparent : AppColors.border,
        ),
        boxShadow: const <BoxShadow>[
          BoxShadow(
            color: AppColors.shadow,
            blurRadius: 12,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Icon(
                _quedaDetectada
                    ? Icons.warning_amber_rounded
                    : Icons.warning_amber_rounded,
                size: 28,
                color: titleColor,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  _quedaDetectada
                      ? 'Queda detectada!'
                      : 'Detecção de queda',
                  style: TextStyle(
                    color: titleColor,
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            _quedaDetectada
                ? 'Alerta ativo para testes do sistema.'
                : 'Use o botao abaixo para simular um alerta de queda.',
            style: TextStyle(
              color: subtitleColor,
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
          if (_quedaDetectada && _momentoDeteccao != null) ...<Widget>[
            const SizedBox(height: 16),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Icon(
                  Icons.location_on_outlined,
                  size: 18,
                  color: subtitleColor,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'Localizacao: -23.5505, -46.6333',
                    style: TextStyle(
                      color: subtitleColor,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Icon(
                  Icons.calendar_month_outlined,
                  size: 18,
                  color: subtitleColor,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'Data e hora: ${_formatarDataHora(_momentoDeteccao!)}',
                    style: TextStyle(
                      color: subtitleColor,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _alternarSimulacaoQueda,
              style: ElevatedButton.styleFrom(
                backgroundColor:
                    _quedaDetectada ? AppColors.white : AppColors.primary,
                foregroundColor:
                    _quedaDetectada ? AppColors.error : AppColors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              icon: Icon(
                _quedaDetectada
                    ? Icons.refresh_rounded
                    : Icons.warning_amber_rounded,
              ),
              label: Text(
                _quedaDetectada ? 'Normalizar sistema' : 'Simular queda',
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
