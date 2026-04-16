import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../profile/presentation/screens/profile_screen.dart';
import 'home_screen.dart';

/// Container raiz da navegação interna após autenticação.
///
/// Mantém o estado da aba ativa e garante troca de contexto entre Home,
/// Dispositivos e Perfil com baixa complexidade e previsibilidade de fluxo.
class MainNavigationScreen extends StatefulWidget {
  /// Cria a tela principal de navegação com estado local para abas.
  const MainNavigationScreen({
    super.key,
  });

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

/// Estado responsável por sincronizar a aba selecionada e o conteúdo exibido.
class _MainNavigationScreenState extends State<MainNavigationScreen> {
  /// Índice da aba atualmente ativa no BottomNavigationBar.
  int _selectedIndex = 0;

  /// Mapa estático de telas por posição de aba.
  ///
  /// A estrutura em lista reduz lógica condicional no build e facilita evoluir
  /// cada módulo de forma independente sem acoplar navegação com UI de conteúdo.
  static const List<Widget> _tabs = <Widget>[
    HomeScreen(),
    Center(
      child: Text(
        'Em breve',
        style: TextStyle(color: AppColors.textSecondary),
      ),
    ),
    ProfileScreen(),
  ];

  /// Atualiza a aba ativa quando o usuário toca em um item de navegação.
  ///
  /// [index] representa a posição do item no BottomNavigationBar.
  void _onItemTapped(int index) {
    // Mantém a atualização de estado centralizada para refletir a troca de aba
    // imediatamente no corpo da tela.
    setState(() {
      _selectedIndex = index;
    });
  }

  /// Constrói o shell visual com conteúdo dinâmico e barra inferior fixa.
  ///
  /// O corpo reflete a aba selecionada em [_tabs], enquanto a barra inferior
  /// atua como ponto único de navegação principal do usuário autenticado.
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,

      // Exibe a tela correspondente ao índice selecionado na navegação inferior.
      body: _tabs[_selectedIndex],

      // Barra de navegação principal do aplicativo para módulos centrais.
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed,
        backgroundColor: AppColors.surface,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textSecondary,
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home_rounded),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.watch_outlined),
            activeIcon: Icon(Icons.watch),
            label: 'Dispositivos',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline_rounded),
            activeIcon: Icon(Icons.person_rounded),
            label: 'Perfil',
          ),
        ],
      ),
    );
  }
}