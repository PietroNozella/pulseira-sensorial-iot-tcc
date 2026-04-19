import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../services/storage_service.dart';

/// Botão responsável por encerrar a sessão do usuário na tela de perfil.
class LogoutButtonWidget extends StatelessWidget {
  const LogoutButtonWidget({super.key});

  /// Executa o fluxo de logout.
  ///
  /// Remove o token persistido localmente e, em seguida, redefine a pilha de
  /// navegação para impedir retorno a telas autenticadas.
  ///
  /// [context] é utilizado para navegação após a limpeza da sessão.
  Future<void> _fazerLogout(BuildContext context) async {
    // Garante a invalidação da sessão local antes de qualquer redirecionamento,
    // evitando que telas protegidas sejam reabertas com credenciais antigas.
    await StorageService().deleteToken();

    if (!context.mounted) return;

    // Reinicia o fluxo de navegação na rota inicial para consolidar o estado
    // de usuário deslogado e bloquear o retorno pela pilha anterior.
    Navigator.pushNamedAndRemoveUntil(
      context,
      '/',
      (route) => false,
    );
  }

  /// Monta o estilo do botão de logout.
  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton.icon(
        onPressed: () => _fazerLogout(context),
        icon: const Icon(Icons.logout_rounded, color: AppColors.error),
        label: const Text(
          'Sair',
          style: TextStyle(color: AppColors.error),
        ),
        style: OutlinedButton.styleFrom(
          backgroundColor: AppColors.transparent,
          side: const BorderSide(color: AppColors.error, width: 1.5),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
        ),
      ),
    );
  }
}