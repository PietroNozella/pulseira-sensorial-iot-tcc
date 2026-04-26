import 'package:flutter/material.dart';

import '../widgets/logout_button_widget.dart';
import '../widgets/profile_header_widget.dart';
import '../widgets/profile_menu_item_widget.dart';
import 'edit_profile_screen.dart';

/// Tela de perfil do usuario com acesso centralizado as configuracoes pessoais.
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  void _mostrarFuncionalidadeEmDesenvolvimento(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Funcionalidade em desenvolvimento.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Perfil',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              const ProfileHeaderWidget(),
              const SizedBox(height: 24),
              Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(18),
                  child: Column(
                    children: [
                      ProfileMenuItemWidget(
                        title: 'Editar Perfil',
                        icon: Icons.edit,
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const EditProfileScreen(),
                            ),
                          );
                        },
                      ),
                      ProfileMenuItemWidget(
                        title: 'Contatos de Emergência',
                        icon: Icons.contact_phone,
                        onTap: () => _mostrarFuncionalidadeEmDesenvolvimento(context),
                      ),
                      ProfileMenuItemWidget(
                        title: 'Autenticação e Segurança',
                        icon: Icons.fingerprint,
                        onTap: () => _mostrarFuncionalidadeEmDesenvolvimento(context),
                      ),
                      ProfileMenuItemWidget(
                        title: 'Permissões do App',
                        icon: Icons.phonelink_lock_rounded,
                        onTap: () => _mostrarFuncionalidadeEmDesenvolvimento(context),
                      ),
                      ProfileMenuItemWidget(
                        title: 'Registro Completo de Eventos',
                        icon: Icons.history,
                        onTap: () => _mostrarFuncionalidadeEmDesenvolvimento(context),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 28),
              const LogoutButtonWidget(),
            ],
          ),
        ),
      ),
    );
  }
}
