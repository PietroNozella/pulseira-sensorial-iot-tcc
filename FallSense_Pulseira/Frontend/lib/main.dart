import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/home_screen.dart';
import 'screens/two_factor_screen.dart'; 

void main() {
  runApp(const MyApp());
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
          return MaterialPageRoute(builder: (context) => const HomeScreen());
        }

        // ROTA ESPECIAL: 2FA (Segura contra argumentos nulos)
        if (settings.name == '/2fa') {
          // Captura os argumentos com segurança: se for nulo, cria um mapa vazio {}
          final args = (settings.arguments ?? {}) as Map<String, dynamic>;
          
          return MaterialPageRoute(
            builder: (context) => TwoFactorScreen(
              // Se o argumento não existir, passa uma string vazia para evitar erro de tipo
              email: args['email'] ?? '',
              senha: args['senha'] ?? '',
              // secretKey pode ser null (ex: quando o usuário vem pelo login normal)
              secretKey: args['secretKey'], 
            ),
          );
        }

        return null;
      },
    );
  }
}