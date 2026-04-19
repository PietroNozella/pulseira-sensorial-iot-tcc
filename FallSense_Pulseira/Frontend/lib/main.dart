import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/auth/screens/register_screen.dart';
import 'features/home/presentation/screens/main_navigation_screen.dart';
import 'features/auth/screens/two_factor_screen.dart'; 

void main() {
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Pulseira Sensorial',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: false, 
      ),
      
      initialRoute: '/', 

      onGenerateRoute: (settings) {
        // Rota de Login
        if (settings.name == '/') {
          return MaterialPageRoute(builder: (context) => const LoginScreen());
        }
        
        // Rota de Registro
        if (settings.name == '/register') {
          return MaterialPageRoute(builder: (context) => const RegisterScreen());
        }

        // Rota de Home
        if (settings.name == '/home') {
          return MaterialPageRoute(
            builder: (context) => const MainNavigationScreen(),
          );
        }

        // ROTA ESPECIAL: 2FA (Segura contra argumentos nulos)
        if (settings.name == '/2fa') {
          // Captura os argumentos com segurança: se for nulo, cria um mapa vazio {}
          final args = (settings.arguments ?? {}) as Map<String, dynamic>;
          
          return MaterialPageRoute(
            builder: (context) => TwoFactorScreen(
              email: args['email'] ?? '',
              senha: args['senha'] ?? '',
              // secretKey só vem após registro; null quando usuário vem pelo login
              secretKey: args['secretKey'],
              // recoveryCodes só vem após registro; null no login normal
              recoveryCodes: args['recoveryCodes'] != null
                  ? List<String>.from(args['recoveryCodes'])
                  : null,
            ),
          );
        }

        return null;
      },
    );
  }
}