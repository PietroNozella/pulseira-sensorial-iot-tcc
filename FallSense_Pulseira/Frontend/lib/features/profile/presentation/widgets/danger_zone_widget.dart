import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';
import 'delete_account_dialog_widget.dart';

/// Agrupa ações críticas do usuário em um escopo visual claramente separado.
class DangerZoneWidget extends StatelessWidget {
  const DangerZoneWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(
          color: AppColors.border,
          thickness: 1,
          height: 1,
        ),
        const SizedBox(height: 24),
        const Text(
          'Zona de Perigo',
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: AppColors.error,
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          'A exclusão da conta é permanente e não pode ser desfeita.',
          style: TextStyle(
            fontSize: 14,
            color: AppColors.textSecondary,
          ),
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () async {
              final password = await showDialog<String>(
                context: context,
                builder: (context) => const DeleteAccountDialogWidget(),
              );
              
              if (password != null && password.isNotEmpty) {
                // TODO: Fazer a chamada para a API passando a 'password' e excluir a conta
              }
            },
            icon: const Icon(Icons.delete_outline_rounded, color: AppColors.error),
            label: const Text(
              'Excluir minha conta',
              style: TextStyle(color: AppColors.error, fontSize: 16),
            ),
            style: OutlinedButton.styleFrom(
              backgroundColor: AppColors.transparent,
              side: const BorderSide(color: AppColors.error, width: 1.5),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
              padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
            ),
          ),
        ),
      ],
    );
  }
}