import 'package:flutter/material.dart';

import '../../../../core/network/api_service.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../services/storage_service.dart';
import '../../../../widgets/custom_text_field_widget.dart';

/// Gerencia a entrada de senhas e a interacao de ocultar/mostrar caracteres.
class ChangePasswordFormWidget extends StatefulWidget {
  const ChangePasswordFormWidget({super.key});

  @override
  State<ChangePasswordFormWidget> createState() => _ChangePasswordFormWidgetState();
}

class _ChangePasswordFormWidgetState extends State<ChangePasswordFormWidget> {
  late final TextEditingController _currentPasswordController;
  late final TextEditingController _newPasswordController;
  late final TextEditingController _confirmPasswordController;

  bool _obscureCurrentPassword = true;
  bool _obscureNewPassword = true;
  bool _obscureConfirmPassword = true;
  bool _carregando = false;

  @override
  void initState() {
    super.initState();
    _currentPasswordController = TextEditingController();
    _newPasswordController = TextEditingController();
    _confirmPasswordController = TextEditingController();
  }

  @override
  void dispose() {
    _currentPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _alterarSenha() async {
    if (_carregando) return;

    final senhaAtual = _currentPasswordController.text;
    final novaSenha = _newPasswordController.text;
    final confirmarSenha = _confirmPasswordController.text;

    if (senhaAtual.isEmpty || novaSenha.isEmpty || confirmarSenha.isEmpty) {
      _exibirMensagem('Preencha todos os campos de senha.', AppColors.warning);
      return;
    }

    if (novaSenha != confirmarSenha) {
      _exibirMensagem('As senhas nao coincidem.', AppColors.warning);
      return;
    }

    setState(() => _carregando = true);

    try {
      final token = await StorageService().getToken();

      if (!mounted) return;

      if (token == null || token.isEmpty) {
        _exibirMensagem('Sessao expirada. Faca login novamente.', AppColors.error);
        return;
      }

      final resultado = await ApiService().alterarSenha(
        token: token,
        senhaAtual: senhaAtual,
        novaSenha: novaSenha,
      );

      if (!mounted) return;

      final status = resultado['status'] as int;
      final body = resultado['body'] as Map<String, dynamic>;

      if (status == 200) {
        _currentPasswordController.clear();
        _newPasswordController.clear();
        _confirmPasswordController.clear();
        _exibirMensagem('Senha atualizada com sucesso!', AppColors.success);
      } else {
        _exibirMensagem(
          ApiService.errorMessage(body, 'Erro ao atualizar senha.'),
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
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Alterar Senha',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 20),
          CustomTextFieldWidget(
            label: 'Senha Atual',
            controller: _currentPasswordController,
            icon: Icons.lock_outline_rounded,
            obscureText: _obscureCurrentPassword,
            suffixIcon: IconButton(
              icon: Icon(
                _obscureCurrentPassword ? Icons.visibility_off : Icons.visibility,
                color: AppColors.textSecondary,
              ),
              onPressed: () => setState(() => _obscureCurrentPassword = !_obscureCurrentPassword),
            ),
          ),
          const SizedBox(height: 16),
          CustomTextFieldWidget(
            label: 'Nova Senha',
            controller: _newPasswordController,
            icon: Icons.lock_outline_rounded,
            obscureText: _obscureNewPassword,
            suffixIcon: IconButton(
              icon: Icon(
                _obscureNewPassword ? Icons.visibility_off : Icons.visibility,
                color: AppColors.textSecondary,
              ),
              onPressed: () => setState(() => _obscureNewPassword = !_obscureNewPassword),
            ),
          ),
          const SizedBox(height: 16),
          CustomTextFieldWidget(
            label: 'Confirmar Senha',
            controller: _confirmPasswordController,
            icon: Icons.lock_outline_rounded,
            obscureText: _obscureConfirmPassword,
            suffixIcon: IconButton(
              icon: Icon(
                _obscureConfirmPassword ? Icons.visibility_off : Icons.visibility,
                color: AppColors.textSecondary,
              ),
              onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
            ),
          ),
          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _carregando ? null : _alterarSenha,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                elevation: 0,
              ),
              child: _carregando
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                        color: AppColors.white,
                        strokeWidth: 2,
                      ),
                    )
                  : const Text(
                      'Atualizar Senha',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}
