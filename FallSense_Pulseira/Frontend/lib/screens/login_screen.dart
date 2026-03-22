import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'home_screen.dart';
import 'forgot_password_screen.dart';
import '../services/storage_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  bool _carregando = false;
  
  // VARIÁVEL PARA CONTROLAR A VISIBILIDADE DA SENHA
  bool _verSenha = false;

  Future<void> _tentarEntrar() async {
    const String urlServidor = "http://127.0.0.1:8000/auth/login";

    if (_emailController.text.isEmpty || _passwordController.text.isEmpty) {
      _exibirErro("Preencha e-mail e senha!");
      return;
    }

    setState(() => _carregando = true);

    try {
      final response = await http.post(
        Uri.parse(urlServidor),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "email": _emailController.text.trim(),
          "senha": _passwordController.text,
          "codigo_2fa": null, 
        }),
      );

      final dadosCorpo = jsonDecode(response.body);

      if (response.statusCode == 200) {
        if (!mounted) return;

        if (dadosCorpo['requer_2fa'] == true) {
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
          // Salva o token JWT caso o backend retorne sem exigir 2FA
          final String? token = dadosCorpo['access_token'];
          if (token != null) {
            await StorageService().saveToken(token);
          }
          _irParaHome();
        }

      } else {
        final erro = dadosCorpo['detail'] ?? "Erro ao realizar login";
        _exibirErro(erro.toString());
      }
    } catch (e) {
      _exibirErro("Erro de conexão: Verifique o servidor");
    } finally {
      if (mounted) setState(() => _carregando = false);
    }
  }

  void _irParaHome() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Login realizado com sucesso!"), backgroundColor: Colors.green),
    );
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const HomeScreen()),
    );
  }

  void _exibirErro(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("FallSense - Login"), centerTitle: true),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 40),
              const Icon(Icons.security, size: 80, color: Colors.blue), 
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
              
              // CAMPO DE SENHA ATUALIZADO COM O OLHINHO
              TextField(
                controller: _passwordController,
                obscureText: !_verSenha, // Controla se o texto fica oculto
                decoration: InputDecoration(
                  labelText: "Senha",
                  border: const OutlineInputBorder(),
                  prefixIcon: const Icon(Icons.lock),
                  // BOTÃO PARA MOSTRAR/ESCONDER
                  suffixIcon: IconButton(
                    icon: Icon(
                      _verSenha ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() {
                        _verSenha = !_verSenha;
                      });
                    },
                  ),
                ),
              ),

              // --- BOTÃO ESQUECI MINHA SENHA ADICIONADO AQUI ---
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const ForgotPasswordScreen(),
                      ),
                    );
                  },
                  child: const Text(
                    "Esqueci minha senha",
                    style: TextStyle(
                      color: Colors.blueAccent, 
                      fontWeight: FontWeight.bold
                    ),
                  ),
                ),
              ),
              // ------------------------------------------------
              
              const SizedBox(height: 20), // Ajustei o espaço para o botão caber bem
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: _carregando ? null : _tentarEntrar,
                  child: _carregando 
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Text("Entrar", style: TextStyle(fontSize: 18)),
                ),
              ),
              const SizedBox(height: 15),
              TextButton(
                onPressed: () => Navigator.pushNamed(context, '/register'),
                child: const Text("Ainda não tem conta? Criar uma conta"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}