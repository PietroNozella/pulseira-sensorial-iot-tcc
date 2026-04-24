import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/network/api_service.dart';
import '../../../core/theme/app_colors.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _nomeController = TextEditingController();
  final _emailController = TextEditingController();
  final _telefoneController = TextEditingController();
  final _senhaController = TextEditingController();
  final _confirmeSenhaController = TextEditingController();

  bool _verSenha = false;
  bool _verConfirmeSenha = false;
  bool _carregando = false;

  Future<void> _realizarCadastro() async {
    if (_carregando) return;

    final nome = _nomeController.text.trim();
    final email = _emailController.text.trim().toLowerCase();
    final telefoneRaw = _telefoneController.text;
    final senha = _senhaController.text;
    final confirmeSenha = _confirmeSenhaController.text;
    final telefone = telefoneRaw.replaceAll(RegExp(r'[^0-9]'), '');

    if (nome.isEmpty || email.isEmpty || telefone.isEmpty || senha.isEmpty) {
      _mensagemErro("Preencha todos os campos!");
      return;
    }

    if (senha != confirmeSenha) {
      _mensagemErro("As senhas não coincidem!");
      return;
    }

    setState(() => _carregando = true);

    try {
      final resultado = await ApiService().registrar(
        nome: nome,
        email: email,
        telefone: telefone,
        senha: senha,
      );

      final int status = resultado['status'];
      final Map<String, dynamic> corpo = resultado['body'];

      if (status == 201 || status == 200) {
        if (!mounted) return;

        final String? segredo2FA = corpo['totp_secret'];
        final String? totpUri = corpo['totp_uri'];

        if (segredo2FA == null || segredo2FA.isEmpty) {
          _mensagemErro("Erro: chave 2FA não gerada pelo servidor.");
          return;
        }

        final recoveryCodes = List<String>.from(corpo['recovery_codes'] ?? []);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Conta criada! Vamos configurar a segurança."),
            backgroundColor: AppColors.success,
          ),
        );

        Navigator.pushReplacementNamed(
          context,
          '/2fa',
          arguments: {
            'email': email,
            'senha': senha,
            'secretKey': segredo2FA,
            'totpUri': totpUri,
            'recoveryCodes': recoveryCodes,
          },
        );
      } else {
        final detalhe = corpo['detail'];
        var msgParaUsuario = "Erro ao realizar cadastro.";

        if (detalhe is List && detalhe.isNotEmpty) {
          msgParaUsuario =
              detalhe[0]['msg'].toString().replaceAll('Value error, ', '');
        } else if (detalhe != null) {
          msgParaUsuario = detalhe.toString();
        }

        _mensagemErro(msgParaUsuario);
      }
    } on ApiRequestTimeoutException {
      _mensagemErro("Servidor demorou para responder. Tente novamente.");
    } catch (e) {
      _mensagemErro("Erro de conexão. Verifique o servidor.");
    } finally {
      if (mounted) setState(() => _carregando = false);
    }
  }

  void _mensagemErro(String texto) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(texto),
        backgroundColor: AppColors.error,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Container(
            width: double.infinity,
            height: double.infinity,
            decoration: const BoxDecoration(
              image: DecorationImage(
                image: AssetImage('assets/images/fundo.jpg'),
                fit: BoxFit.cover,
              ),
            ),
          ),
          Container(
            width: double.infinity,
            height: double.infinity,
            color: AppColors.white.withValues(alpha: 0.8),
          ),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(25.0),
              child: Column(
                children: [
                  const SizedBox(height: 20),
                  const Icon(
                    Icons.person_add_alt_1,
                    size: 80,
                    color: AppColors.primary,
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    "Crie sua Conta",
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 30),
                  _buildTextField(
                    _nomeController,
                    "Nome Completo",
                    Icons.person,
                  ),
                  const SizedBox(height: 15),
                  _buildTextField(
                    _emailController,
                    "E-mail",
                    Icons.email,
                    keyboardType: TextInputType.emailAddress,
                  ),
                  const SizedBox(height: 15),
                  _buildTextField(
                    _telefoneController,
                    "Telefone",
                    Icons.phone,
                    hint: "(00) 00000-0000",
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      TelefoneInputFormatter(),
                    ],
                  ),
                  const SizedBox(height: 15),
                  _buildTextField(
                    _senhaController,
                    "Senha",
                    Icons.lock,
                    isPassword: true,
                    isVisible: _verSenha,
                    onToggle: () => setState(() => _verSenha = !_verSenha),
                  ),
                  const SizedBox(height: 15),
                  _buildTextField(
                    _confirmeSenhaController,
                    "Confirme sua Senha",
                    Icons.lock_reset,
                    isPassword: true,
                    isVisible: _verConfirmeSenha,
                    onToggle: () {
                      setState(() => _verConfirmeSenha = !_verConfirmeSenha);
                    },
                  ),
                  const SizedBox(height: 30),
                  SizedBox(
                    width: double.infinity,
                    height: 55,
                    child: ElevatedButton(
                      onPressed: _carregando ? null : _realizarCadastro,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      child: _carregando
                          ? const SizedBox(
                              height: 22,
                              width: 22,
                              child: CircularProgressIndicator(
                                color: AppColors.white,
                                strokeWidth: 2,
                              ),
                            )
                          : const Text(
                              "CADASTRAR",
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                                color: AppColors.white,
                              ),
                            ),
                    ),
                  ),
                  TextButton(
                    onPressed: _carregando ? null : () => Navigator.pop(context),
                    child: const Text("Já tem uma conta? Faça Login"),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField(
    TextEditingController controller,
    String label,
    IconData icon, {
    bool isPassword = false,
    bool isVisible = false,
    VoidCallback? onToggle,
    TextInputType keyboardType = TextInputType.text,
    String? hint,
    List<TextInputFormatter>? inputFormatters,
  }) {
    return TextField(
      controller: controller,
      obscureText: isPassword ? !isVisible : false,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        border: const OutlineInputBorder(),
        filled: true,
        fillColor: AppColors.white.withValues(alpha: 0.7),
        prefixIcon: Icon(icon),
        suffixIcon: isPassword
            ? IconButton(
                icon: Icon(isVisible ? Icons.visibility : Icons.visibility_off),
                onPressed: onToggle,
              )
            : null,
      ),
    );
  }
}

class TelefoneInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    var text = newValue.text.replaceAll(RegExp(r'\D'), '');
    if (text.length > 11) text = text.substring(0, 11);

    var formatted = '';
    if (text.isNotEmpty) {
      formatted += '(' + text.substring(0, text.length >= 2 ? 2 : text.length);
    }
    if (text.length > 2) {
      formatted += ') ' + text.substring(2, text.length >= 7 ? 7 : text.length);
    }
    if (text.length > 7) {
      formatted += '-' + text.substring(7, text.length);
    }

    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}
