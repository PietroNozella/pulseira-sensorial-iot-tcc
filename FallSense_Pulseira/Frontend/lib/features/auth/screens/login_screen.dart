import 'package:flutter/material.dart';

import '../../../core/network/api_service.dart';
import '../../../core/theme/app_colors.dart';
import '../../../services/storage_service.dart';
import 'forgot_password_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _carregando = false;
  bool _verSenha = false;

  Future<void> _tentarEntrar() async {
    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      _exibirErro("Preencha e-mail e senha!");
      return;
    }

    setState(() => _carregando = true);

    try {
      final resultado = await ApiService().login(
        email: _emailController.text.trim(),
        senha: _passwordController.text,
      );

      final int status = resultado['status'];
      final Map<String, dynamic> corpo = resultado['body'];

      if (status == 200) {
        if (!mounted) return;

        if (corpo['requer_2fa'] == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text("Senha correta! Insira o código 2FA.")),
          );
          Navigator.pushNamed(
            context,
            '/2fa',
            arguments: {
              'email': _emailController.text.trim(),
              'senha': _passwordController.text,
              'secretKey': null,
            },
          );
        } else {
          final String? token = corpo['access_token'];
          final String? nomeCompleto = corpo['nome_completo'];

          if (token != null) {
            await StorageService().saveToken(token);
          }
          if (nomeCompleto != null && nomeCompleto.trim().isNotEmpty) {
            await StorageService().saveUserName(nomeCompleto.trim());
          }

          _irParaHome();
        }
      } else {
        _exibirErro(corpo['detail']?.toString() ?? "Erro ao realizar login");
      }
    } on ApiRequestTimeoutException {
      _exibirErro("Servidor demorou para responder. Tente novamente.");
    } catch (e) {
      _exibirErro("Erro de conexão. Verifique o servidor.");
    } finally {
      if (mounted) setState(() => _carregando = false);
    }
  }

  void _irParaHome() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("Login realizado com sucesso!"),
        backgroundColor: AppColors.success,
      ),
    );
    Navigator.pushReplacementNamed(context, '/home');
  }

  void _exibirErro(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: AppColors.error),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("FallSense - Login"),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 40),
              const Icon(Icons.security, size: 80, color: AppColors.primary),
              const SizedBox(height: 30),
              TextField(
                controller: _emailController,
                decoration: const InputDecoration(
                  labelText: "Email",
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.email),
                ),
                keyboardType: TextInputType.emailAddress,
              ),
              const SizedBox(height: 20),
              TextField(
                controller: _passwordController,
                obscureText: !_verSenha,
                decoration: InputDecoration(
                  labelText: "Senha",
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.lock),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _verSenha ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () => setState(() => _verSenha = !_verSenha),
                  ),
                ),
              ),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: _carregando
                      ? null
                      : () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) =>
                                  const ForgotPasswordScreen(),
                            ),
                          );
                        },
                  child: const Text(
                    "Esqueci minha senha",
                    style: TextStyle(
                      color: AppColors.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _carregando ? null : _tentarEntrar,
                  child: _carregando
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            color: AppColors.white,
                            strokeWidth: 2,
                          ),
                        )
                      : const Text("Entrar", style: TextStyle(fontSize: 18)),
                ),
              ),
              const SizedBox(height: 15),
              TextButton(
                onPressed: _carregando
                    ? null
                    : () => Navigator.pushNamed(context, '/register'),
                child: const Text("Ainda não tem conta? Criar uma conta"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
