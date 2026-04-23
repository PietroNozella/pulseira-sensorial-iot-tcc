import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import 'device_status_widget.dart';

/// Card de resumo do dispositivo principal exibido na Home.
class DeviceListItemWidget extends StatelessWidget {
  const DeviceListItemWidget({
    required this.title,
    required this.subtitle,
    required this.supportingText,
    required this.hasDevice,
    required this.isActive,
    super.key,
  });

  final String title;
  final String subtitle;
  final String supportingText;
  final bool hasDevice;
  final bool isActive;

  @override
  Widget build(BuildContext context) {
    final statusColor = isActive ? AppColors.white : Colors.white70;

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
                        title,
                        style: const TextStyle(
                          color: AppColors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      if (hasDevice)
                        DeviceStatusWidget(
                          color: statusColor,
                          label: isActive ? 'Conectada' : 'Inativa',
                        )
                      else
                        const Text(
                          'Cadastre a primeira pulseira',
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
                hasDevice ? 'Firmware' : 'Status',
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
                    hasDevice ? Icons.memory_rounded : Icons.info_outline_rounded,
                    color: AppColors.white,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    supportingText,
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
