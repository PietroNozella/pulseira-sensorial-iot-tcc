import 'package:flutter/material.dart';

import '../../../../core/network/api_service.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../services/storage_service.dart';
import 'delete_account_dialog_widget.dart';

/// Agrupa acoes criticas do usuario em um escopo visual separado.
class DangerZoneWidget extends StatefulWidget {
  const DangerZoneWidget({super.key});

  @override
  State<DangerZoneWidget> createState() => _DangerZoneWidgetState();
}

class _DangerZoneWidgetState extends State<DangerZoneWidget> {
  bool _carregando = false;

  Future<void> _confirmarExclusao() async {
    if (_carregando) return;

    final password = await showDialog<String>(
      context: context,
      builder: (context) => const DeleteAccountDialogWidget(),
    );

    if (!mounted || password == null || password.trim().isEmpty) return;

    setState(() => _carregando = true);

    try {
      final storage = StorageService();
      final token = await storage.getToken();

      if (!mounted) return;

      if (token == null || token.isEmpty) {
        _exibirMensagem('Sessao expirada. Faca login novamente.', AppColors.error);
        return;
      }

      final resultado = await ApiService().excluirConta(
        token: token,
        senha: password,
      );

      if (!mounted) return;

      final status = resultado['status'] as int;
      final body = resultado['body'] as Map<String, dynamic>;

      if (status == 200) {
        await storage.clearSession();

        if (!mounted) return;

        _exibirMensagem('Conta excluida com sucesso.', AppColors.success);
        Navigator.pushNamedAndRemoveUntil(
          context,
          '/',
          (route) => false,
        );
      } else {
        _exibirMensagem(
          ApiService.errorMessage(body, 'Erro ao excluir conta.'),
          AppColors.error,
        );
      }
    } on ApiRequestTimeoutException {
      _exibirMensagem('Servidor demorou para responder. Tente novamente.', AppColors.error);
    } catch (_) {
      _exibirMensagem('Erro de conexao. Verifique o servidor.', AppColors.error);
    } finally {
      if (mounted) setState(() => _carregando = false);
    }
  }

  void _exibirMensagem(String texto, Color cor) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(texto), backgroundColor: cor),
    );
  }

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
            onPressed: _carregando ? null : _confirmarExclusao,
            icon: _carregando
                ? const SizedBox(
                    height: 18,
                    width: 18,
                    child: CircularProgressIndicator(
                      color: AppColors.error,
                      strokeWidth: 2,
                    ),
                  )
                : const Icon(Icons.delete_outline_rounded, color: AppColors.error),
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
