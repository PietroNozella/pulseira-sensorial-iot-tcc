import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../widgets/change_password_form_widget.dart';
import '../widgets/danger_zone_widget.dart';
import '../widgets/personal_info_form_widget.dart';

/// Tela para edição das informações pessoais do usuário.
/// 
/// Atua como um orquestrador que compõe a interface com componentes
/// independentes, respeitando o Princípio de Responsabilidade Única (SRP).
class EditProfileScreen extends StatelessWidget {
  const EditProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(
            Icons.arrow_back,
            color: AppColors.white,
          ),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: const Text(
          'Editar Perfil',
          style: TextStyle(
            color: AppColors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(
            color: AppColors.border,
            height: 1,
          ),
        ),
      ),
      body: const SingleChildScrollView(
        padding: EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Componente independente para gerenciar dados pessoais
            PersonalInfoFormWidget(),
            SizedBox(height: 24),
            
            // Componente independente para gerenciar credenciais (senha)
            ChangePasswordFormWidget(),
            SizedBox(height: 32),
            
            // Componente independente para ações críticas (exclusão de conta)
            DangerZoneWidget(),
          ],
        ),
      ),
    );
  }
}