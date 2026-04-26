import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/network/api_service.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../services/storage_service.dart';
import '../../../../widgets/custom_text_field_widget.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

/// Gerencia exclusivamente o estado e a UI das informacoes pessoais.
class PersonalInfoFormWidget extends ConsumerStatefulWidget {
  const PersonalInfoFormWidget({super.key});

  @override
  ConsumerState<PersonalInfoFormWidget> createState() => _PersonalInfoFormWidgetState();
}

class _PersonalInfoFormWidgetState extends ConsumerState<PersonalInfoFormWidget> {
  late final TextEditingController _nameController;
  late final TextEditingController _emailController;
  late final TextEditingController _phoneController;

  bool _carregando = false;
  bool _dadosIniciaisAplicados = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController();
    _emailController = TextEditingController();
    _phoneController = TextEditingController();
  }

  void _aplicarDadosIniciais(AuthUserProfile profile) {
    if (_dadosIniciaisAplicados) return;

    _nameController.text = profile.name;
    _emailController.text = profile.email;
    _phoneController.text = profile.phone;
    _dadosIniciaisAplicados = true;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _salvarAlteracoes() async {
    if (_carregando) return;

    final nome = _nameController.text.trim();
    final email = _emailController.text.trim().toLowerCase();
    final telefone = _phoneController.text.trim();

    if (nome.isEmpty || email.isEmpty) {
      _exibirMensagem('Preencha nome e e-mail.', AppColors.warning);
      return;
    }

    setState(() => _carregando = true);

    try {
      final storage = StorageService();
      final token = await storage.getToken();

      if (!mounted) return;

      if (token == null || token.isEmpty) {
        _exibirMensagem('Sessao expirada. Faca login novamente.', AppColors.error);
        return;
      }

      final resultado = await ApiService().atualizarPerfil(
        token: token,
        nome: nome,
        email: email,
        telefone: telefone,
      );

      if (!mounted) return;

      final status = resultado['status'] as int;
      final body = resultado['body'] as Map<String, dynamic>;

      if (status == 200) {
        final novoToken = body['access_token'] as String?;
        final nomeAtualizado = (body['nome_completo'] as String?)?.trim() ?? nome;

        if (novoToken != null && novoToken.isNotEmpty) {
          await storage.saveToken(novoToken);
        }
        await storage.saveUserName(nomeAtualizado);

        if (!mounted) return;

        ref.invalidate(userProfileProvider);
        _exibirMensagem('Perfil atualizado com sucesso!', AppColors.success);
      } else {
        _exibirMensagem(
          ApiService.errorMessage(body, 'Erro ao atualizar perfil.'),
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
    final userProfileAsync = ref.watch(userProfileProvider);
    userProfileAsync.whenData(_aplicarDadosIniciais);

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
            'Informações Pessoais',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 20),
          CustomTextFieldWidget(
            label: 'Nome Completo',
            controller: _nameController,
            icon: Icons.person_outline_rounded,
            keyboardType: TextInputType.name,
          ),
          const SizedBox(height: 16),
          CustomTextFieldWidget(
            label: 'E-mail',
            controller: _emailController,
            icon: Icons.email_outlined,
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 16),
          CustomTextFieldWidget(
            label: 'Telefone',
            controller: _phoneController,
            icon: Icons.phone_outlined,
            keyboardType: TextInputType.phone,
          ),
          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _carregando ? null : _salvarAlteracoes,
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
                      'Salvar Alterações',
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
