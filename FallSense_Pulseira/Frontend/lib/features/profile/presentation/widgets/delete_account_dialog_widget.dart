import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

/// Dialogo de seguranca para confirmar a exclusao da conta do usuario.
class DeleteAccountDialogWidget extends StatefulWidget {
  const DeleteAccountDialogWidget({super.key});

  @override
  State<DeleteAccountDialogWidget> createState() => _DeleteAccountDialogWidgetState();
}

class _DeleteAccountDialogWidgetState extends State<DeleteAccountDialogWidget> {
  final TextEditingController _passwordController = TextEditingController();
  bool _obscurePassword = true;

  bool get _podeConfirmar => _passwordController.text.trim().isNotEmpty;

  @override
  void dispose() {
    _passwordController.dispose();
    super.dispose();
  }

  void _confirmar() {
    final password = _passwordController.text.trim();
    if (password.isEmpty) return;

    Navigator.of(context).pop(password);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      backgroundColor: AppColors.surface,
      title: const Text(
        'Excluir Conta',
        style: TextStyle(
          color: AppColors.error,
          fontWeight: FontWeight.bold,
          fontSize: 20,
        ),
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            'Esta ação é permanente e não pode ser desfeita. Confirme sua senha para continuar.',
            style: TextStyle(
              color: AppColors.textPrimary,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 20),
          TextField(
            controller: _passwordController,
            autofocus: true,
            obscureText: _obscurePassword,
            onChanged: (_) => setState(() {}),
            onSubmitted: (_) => _confirmar(),
            style: const TextStyle(color: AppColors.textPrimary),
            decoration: InputDecoration(
              labelText: 'Senha',
              labelStyle: const TextStyle(color: AppColors.textSecondary),
              prefixIcon: const Icon(Icons.lock_outline_rounded, color: AppColors.error),
              suffixIcon: IconButton(
                icon: Icon(
                  _obscurePassword ? Icons.visibility_off : Icons.visibility,
                  color: AppColors.textSecondary,
                ),
                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.border),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.error, width: 2),
              ),
              filled: true,
              fillColor: AppColors.background,
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text(
            'Cancelar',
            style: TextStyle(color: AppColors.textSecondary, fontWeight: FontWeight.w600),
          ),
        ),
        ElevatedButton(
          onPressed: _podeConfirmar ? _confirmar : null,
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.error,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
          child: const Text('Excluir', style: TextStyle(color: AppColors.white)),
        ),
      ],
    );
  }
}
