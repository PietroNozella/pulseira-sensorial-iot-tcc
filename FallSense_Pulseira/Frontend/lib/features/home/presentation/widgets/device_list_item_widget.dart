import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import 'device_status_widget.dart';

/// Card de resumo do contexto principal exibido na Home.
class DeviceListItemWidget extends StatelessWidget {
  const DeviceListItemWidget({
    required this.monitoredPersonName,
    required this.hasMonitoredPerson,
    super.key,
  });

  final String monitoredPersonName;
  final bool hasMonitoredPerson;

  @override
  Widget build(BuildContext context) {
    return Container(
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
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: <Widget>[
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                const Icon(
                  Icons.watch,
                  color: AppColors.white,
                  size: 30,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        monitoredPersonName,
                        style: const TextStyle(
                          color: AppColors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      if (hasMonitoredPerson)
                        const DeviceStatusWidget(color: AppColors.white)
                      else
                        const Text(
                          'Cadastre a primeira pessoa monitorada',
                          style: TextStyle(
                            color: AppColors.white,
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 16),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              Text(
                hasMonitoredPerson ? 'Bateria' : 'Status',
                style: const TextStyle(
                  color: AppColors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 4),
              Row(
                children: <Widget>[
                  Icon(
                    hasMonitoredPerson
                        ? Icons.battery_5_bar_rounded
                        : Icons.info_outline_rounded,
                    color: AppColors.white,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    hasMonitoredPerson ? '85%' : 'Pendente',
                    style: const TextStyle(
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
