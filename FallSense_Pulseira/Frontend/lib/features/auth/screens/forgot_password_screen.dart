import 'package:flutter/material.dart';
import '../../../core/network/api_service.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  final _tokenController = TextEditingController();
  final _novaSenhaController = TextEditingController();
  final _confirmeSenhaController = TextEditingController();

  // Controla qual etapa está visível: false = pedir email, true = inserir token + nova senha
  bool _etapaReset = false;
  bool _carregando = false;
  bool _verSenha = false;

  // Etapa 1: solicita o token por e-mail
  Future<void> _solicitarToken() async {
    final email = _emailController.text.trim();

    if (email.isEmpty) {
      _exibirMensagem("Informe seu e-mail.", Colors.orange);
      return;
    }

    setState(() => _carregando = true);

    try {
      final resultado = await ApiService().solicitarRecuperacao(email);

      if (!mounted) return;

      if (resultado['status'] == 200) {
        _exibirMensagem("Se o e-mail estiver cadastrado, o código foi enviado.", Colors.green);
        // Avança para a etapa de inserir token + nova senha
        setState(() => _etapaReset = true);
      } else {
        final erro = resultado['body']['detail'] ?? "Erro ao solicitar recuperação.";
        _exibirMensagem(erro.toString(), Colors.red);
      }
    } catch (e) {
      _exibirMensagem("Erro de conexão. Verifique o servidor.", Colors.red);
    } finally {
      if (mounted) setState(() => _carregando = false);
    }
  }

  // Etapa 2: envia token + nova senha para resetar
  Future<void> _resetarSenha() async {
    final token = _tokenController.text.trim();
    final novaSenha = _novaSenhaController.text;
    final confirmeSenha = _confirmeSenhaController.text;

    if (token.isEmpty || novaSenha.isEmpty) {
      _exibirMensagem("Preencha o código e a nova senha.", Colors.orange);
      return;
    }

    if (novaSenha != confirmeSenha) {
      _exibirMensagem("As senhas não coincidem.", Colors.orange);
      return;
    }

    setState(() => _carregando = true);

    try {
      final resultado = await ApiService().resetarSenha(
        token: token,
        novaSenha: novaSenha,
      );

      if (!mounted) return;

      if (resultado['status'] == 200) {
        _exibirMensagem("Senha alterada com sucesso!", Colors.green);
        // Volta para o login após reset bem-sucedido
        Navigator.pop(context);
      } else {
        final erro = resultado['body']['detail'] ?? "Erro ao resetar senha.";
        _exibirMensagem(erro.toString(), Colors.red);
      }
    } catch (e) {
      _exibirMensagem("Erro de conexão. Verifique o servidor.", Colors.red);
    } finally {
      if (mounted) setState(() => _carregando = false);
    }
  }

  void _exibirMensagem(String msg, Color cor) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: cor),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Recuperar Senha"),
        centerTitle: true,
        backgroundColor: Colors.blueAccent,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(25.0),
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 30),
              const Icon(Icons.lock_reset, size: 80, color: Colors.blueAccent),
              const SizedBox(height: 20),

              // Etapa 1: campo de e-mail
              if (!_etapaReset) ...[
                const Text(
                  "Informe o e-mail cadastrado.\nEnviaremos um código de recuperação.",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 15, color: Colors.black54),
                ),
                const SizedBox(height: 30),
                TextField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: "E-mail",
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.email),
                  ),
                ),
                const SizedBox(height: 25),
                SizedBox(
                  width: double.infinity,
                  height: 55,
                  child: ElevatedButton(
                    onPressed: _carregando ? null : _solicitarToken,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blueAccent,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: _carregando
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text("ENVIAR CÓDIGO", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                  ),
                ),
              ],

              // Etapa 2: token + nova senha
              if (_etapaReset) ...[
                const Text(
                  "Digite o código recebido por e-mail e sua nova senha.",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 15, color: Colors.black54),
                ),
                const SizedBox(height: 30),
                TextField(
                  controller: _tokenController,
                  decoration: const InputDecoration(
                    labelText: "Código de recuperação",
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.vpn_key),
                  ),
                ),
                const SizedBox(height: 15),
                TextField(
                  controller: _novaSenhaController,
                  obscureText: !_verSenha,
                  decoration: InputDecoration(
                    labelText: "Nova senha",
                    border: const OutlineInputBorder(),
                    prefixIcon: const Icon(Icons.lock),
                    suffixIcon: IconButton(
                      icon: Icon(_verSenha ? Icons.visibility : Icons.visibility_off),
                      onPressed: () => setState(() => _verSenha = !_verSenha),
                    ),
                  ),
                ),
                const SizedBox(height: 15),
                TextField(
                  controller: _confirmeSenhaController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: "Confirme a nova senha",
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.lock_reset),
                  ),
                ),
                const SizedBox(height: 25),
                SizedBox(
                  width: double.infinity,
                  height: 55,
                  child: ElevatedButton(
                    onPressed: _carregando ? null : _resetarSenha,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blueAccent,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: _carregando
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text("SALVAR NOVA SENHA", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                  ),
                ),
                const SizedBox(height: 10),
                // Permite voltar para reenviar o código se necessário
                TextButton(
                  onPressed: () => setState(() => _etapaReset = false),
                  child: const Text("Reenviar código", style: TextStyle(color: Colors.blueAccent)),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
