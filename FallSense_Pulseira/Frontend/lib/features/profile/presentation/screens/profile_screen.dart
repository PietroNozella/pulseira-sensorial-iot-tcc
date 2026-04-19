import 'package:flutter/material.dart';

import '../widgets/logout_button_widget.dart';
import '../widgets/profile_header_widget.dart';
import '../widgets/profile_menu_item_widget.dart';

/// Tela de perfil do usuário com acesso centralizado às configurações pessoais.
///
/// Este componente organiza informações de identidade, atalhos de manutenção
/// da conta e a ação de logout.
class ProfileScreen extends StatelessWidget {
	/// Cria a tela de perfil exibida no fluxo principal do aplicativo.
	const ProfileScreen({super.key});

	/// Constrói a estrutura visual do perfil com seção de cabeçalho,
	/// lista de funcionalidades e ação de logout.
	///
	/// [context] fornece acesso a recursos de navegação, tema e mídia da árvore.
	///
	/// Retorna um [Widget] rolável para acomodar conteúdo em diferentes tamanhos
	/// de tela sem perda de usabilidade.
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
							// Exibe dados de identidade do usuário autenticado 
							const ProfileHeaderWidget(),
							const SizedBox(height: 24),
							// Agrupa os atalhos de perfil em um card único para melhorar
							// escaneabilidade e percepção de seção funcional.
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
												onTap: () {},
											),
											ProfileMenuItemWidget(
												title: 'Contatos de Emergência',
												icon: Icons.contact_phone,
												onTap: () {},
											),
											ProfileMenuItemWidget(
												title: 'Autenticação e Segurança',
												icon: Icons.fingerprint,
												onTap: () {},
											),
											ProfileMenuItemWidget(
												title: 'Permissões do App',
												icon: Icons.phonelink_lock_rounded,
												onTap: () {},
											),
											ProfileMenuItemWidget(
												title: 'Registro Completo de Eventos',
												icon: Icons.history,
												onTap: () {},
											),
										],
									),
								),
							),
							const SizedBox(height: 28),
							// Mantém a ação de logout destacada e separada das preferências,
							// reduzindo risco de acionamento acidental.
							const LogoutButtonWidget(),
						],
					),
				),
			),
		);
	}
}