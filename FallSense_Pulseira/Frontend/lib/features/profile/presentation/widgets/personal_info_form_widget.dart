import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../../widgets/custom_text_field_widget.dart';

/// Gerencia exclusivamente o estado e a UI das informações pessoais.
class PersonalInfoFormWidget extends ConsumerStatefulWidget {
  const PersonalInfoFormWidget({super.key});

  @override
  ConsumerState<PersonalInfoFormWidget> createState() => _PersonalInfoFormWidgetState();
}

class _PersonalInfoFormWidgetState extends ConsumerState<PersonalInfoFormWidget> {
  late final TextEditingController _nameController;
  late final TextEditingController _emailController;
  late final TextEditingController _phoneController;

  @override
  void initState() {
    super.initState();
    
    // O acesso ao provedor ocorre aqui para preencher os dados iniciais
    // sem obrigar a tela inteira a escutar mudanças e ser reconstruída atoa.
    final userProfileAsync = ref.read(userProfileProvider);
    final userProfile = userProfileAsync.maybeWhen(
      data: (value) => value,
      orElse: () => null,
    );

    _nameController = TextEditingController(text: userProfile?.name ?? '');
    _emailController = TextEditingController(text: userProfile?.email ?? '');
    _phoneController = TextEditingController(text: userProfile?.phone ?? '');
  }

  @override
  void dispose() {
    // Evita memory leak descartando controladores quando este widget sai da tela.
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    super.dispose();
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
              onPressed: () {
                // TODO: Implementar a chamada para a API
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                elevation: 0,
              ),
              child: const Text(
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