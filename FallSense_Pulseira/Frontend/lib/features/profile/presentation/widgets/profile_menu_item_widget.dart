import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';

/// Item reutilizável do menu de perfil com ícone, título e ação de navegação.
///
/// Este componente padroniza a aparência e a interação dos atalhos da tela de
/// perfil para manter consistência visual e comportamental.
class ProfileMenuItemWidget extends StatelessWidget {
  /// Cria um item clicável do menu de perfil.
  ///
  /// [title] define o rótulo principal exibido ao usuário.
  /// [icon] representa visualmente a categoria da ação.
  /// [onTap] encapsula a regra de negócio disparada ao toque.
  const ProfileMenuItemWidget({
    required this.title,
    required this.icon,
    required this.onTap,
    super.key,
  });

  final String title;
  final IconData icon;
  final VoidCallback onTap;

  /// Constrói a linha de ação do menu com affordance de toque e separador.
  ///
  /// A composição em coluna permite anexar um divisor inferior para organizar
  /// visualmente listas de opções sem repetir lógica em cada item.
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Centraliza a área interativa e o feedback tátil no próprio item,
        // garantindo boa usabilidade em listas de configurações/perfil.
        InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(18),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 14),
            child: Row(
              children: [
                // Destaca o ícone com fundo suave para facilitar escaneabilidade
                // rápida das opções sem competir com o texto principal.
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: AppColors.primaryLight,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    icon,
                    size: 22,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
                const Icon(
                  Icons.chevron_right,
                  color: AppColors.textPrimary,
                ),
              ],
            ),
          ),
        ),
        // Separa semanticamente os itens do menu, melhorando leitura e toque
        // em interfaces móveis com múltiplas ações consecutivas.
        const Divider(
          color: AppColors.border,
          thickness: 0.8,
          height: 1,
        ),
      ],
    );
  }
}