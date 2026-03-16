import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; 
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'home_screen.dart'; 

class TwoFactorScreen extends StatefulWidget {
  final String email;
  final String senha;
  final String? secretKey; 

  const TwoFactorScreen({
    super.key, 
    required this.email, 
    required this.senha, 
    this.secretKey 
  });

  @override
  State<TwoFactorScreen> createState() => _TwoFactorScreenState();
}

class _TwoFactorScreenState extends State<TwoFactorScreen> {
  final TextEditingController _codeController = TextEditingController();
  bool _carregando = false;

  Future<void> _validarCodigo() async {
    const String urlServidor = "http://127.0.0.1:8000/auth/login";

    // .trim() remove espaços acidentais que o teclado pode inserir
    String codigo = _codeController.text.trim();

    if (codigo.length != 6) {
      _exibirMensagem("O código deve ter 6 dígitos!", Colors.orange);
      return;
    }

    setState(() => _carregando = true);

    try {
      final response = await http.post(
        Uri.parse(urlServidor),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "email": widget.email,
          "senha": widget.senha,
          "codigo_2fa": codigo,
        }),
      );

      if (response.statusCode == 200) {
        if (!mounted) return;
        _exibirMensagem("Acesso autorizado!", Colors.green);
        
        // MELHORIA: Navigator.pushAndRemoveUntil impede que o usuário volte 
        // para a tela de login/2fa após entrar no app
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (context) => const HomeScreen()),
          (route) => false,
        );
      } else {
        final erro = jsonDecode(response.body)['detail'];
        _exibirMensagem(erro.toString(), Colors.red);
      }
    } catch (e) {
      _exibirMensagem("Erro de conexão com o servidor.", Colors.red);
    } finally {
      if (mounted) setState(() => _carregando = false);
    }
  }

  void _exibirMensagem(String msg, Color cor) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: cor, duration: const Duration(seconds: 2)),
    );
  }

  @override
  Widget build(BuildContext context) {
    bool modoConfiguracao = widget.secretKey != null;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Segurança FallSense"),
        centerTitle: true,
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: SingleChildScrollView(
          child: Column(
            children: [
              const SizedBox(height: 20),
              Icon(
                modoConfiguracao ? Icons.phonelink_setup : Icons.phonelink_lock, 
                size: 80, 
                color: Colors.blueAccent
              ),
              const SizedBox(height: 20),
              Text(
                modoConfiguracao ? "Configure seu Autenticador" : "Verificação de Segurança",
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 15),

              if (modoConfiguracao) ...[
                const Text(
                  "1. Copie a chave abaixo\n2. Cole no Google Authenticator\n3. Digite o código de 6 dígitos gerado",
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.black87),
                ),
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.blueAccent.withOpacity(0.3)),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: SelectableText(
                          widget.secretKey!,
                          style: const TextStyle(
                            fontFamily: 'monospace', // Fonte mono para facilitar leitura
                            fontWeight: FontWeight.bold, 
                            fontSize: 18, 
                            letterSpacing: 1.2
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.copy, color: Colors.blueAccent),
                        onPressed: () {
                          Clipboard.setData(ClipboardData(text: widget.secretKey!));
                          _exibirMensagem("Chave copiada!", Colors.blue);
                        },
                      )
                    ],
                  ),
                ),
              ] else ...[
                const Text(
                  "Insira o código de 6 dígitos gerado no seu aplicativo de autenticação.",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: Colors.grey),
                ),
              ],

              const SizedBox(height: 30),
              
              TextField(
                controller: _codeController,
                keyboardType: TextInputType.number,
                // Garante que apenas números sejam digitados
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                maxLength: 6,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 32, letterSpacing: 15, fontWeight: FontWeight.bold),
                decoration: InputDecoration(
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  counterText: "", 
                  hintText: "000000",
                  hintStyle: const TextStyle(color: Colors.grey, letterSpacing: 15)
                ),
              ),
              const SizedBox(height: 40),
              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton(
                  onPressed: _carregando ? null : _validarCodigo,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: _carregando 
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text("VERIFICAR E ENTRAR", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                ),
              ),
              const SizedBox(height: 20),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text("Cancelar", style: TextStyle(color: Colors.grey)),
              )
            ],
          ),
        ),
      ),
    );
  }
}