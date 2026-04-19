import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../../core/theme/app_colors.dart';

/// Cabeçalho do perfil que apresenta identidade visual e nome do usuário autenticado.
///
/// Este componente concentra a exibição dos dados principais do perfil para
/// reforçar contexto de quem está utilizando o aplicativo.
class ProfileHeaderWidget extends ConsumerWidget {
  /// Cria o widget de cabeçalho do perfil.
  const ProfileHeaderWidget({super.key});

  /// Constrói o cabeçalho com nome do usuário e metadados de papel.
  ///
  /// [context] provê informações de tema e layout da árvore de widgets.
  /// [ref] permite observar o estado de autenticação via Riverpod.
  ///
  /// Retorna um [Widget] com avatar, nome resolvido do estado e descrição
  /// complementar do perfil.
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Observa o provider para manter o nome sincronizado com o estado de
    // autenticação e reação automática da interface em atualizações.
    final userNameAsync = ref.watch(authProvider);

    // Define fallback para garantir experiência estável quando o dado ainda
    // está carregando ou em estado de erro, evitando quebra visual do cabeçalho.
    final userName = userNameAsync.maybeWhen(
      data: (value) => value,
      orElse: () => 'Usuario',
    );

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          const CircleAvatar(
            radius: 36,
            backgroundColor: AppColors.primaryLight,
            child: Icon(
              Icons.person,
              size: 36,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  userName,
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Responsável Principal',
                  style: TextStyle(
                    fontSize: 15,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}