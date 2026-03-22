import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'home_screen.dart';
import '../services/storage_service.dart';
import '../api_service.dart';

class TwoFactorScreen extends StatefulWidget {
  final String email;
  final String senha;
  final String? secretKey;
  // Lista de recovery codes exibida apenas no primeiro acesso (após registro)
  final List<String>? recoveryCodes;

  const TwoFactorScreen({
    super.key,
    required this.email,
    required this.senha,
    this.secretKey,
    this.recoveryCodes,
  });

  @override
  State<TwoFactorScreen> createState() => _TwoFactorScreenState();
}

class _TwoFactorScreenState extends State<TwoFactorScreen> {
  final TextEditingController _codeController = TextEditingController();
  bool _carregando = false;

  Future<void> _validarCodigo() async {
    // .trim() remove espaços acidentais que o teclado pode inserir
    String codigo = _codeController.text.trim();

    if (codigo.length != 6) {
      _exibirMensagem("O código deve ter 6 dígitos!", Colors.orange);
      return;
    }

    setState(() => _carregando = true);

    try {
      final resultado = await ApiService().login(
        email: widget.email,
        senha: widget.senha,
        codigo2fa: codigo,
      );

      final int status = resultado['status'];
      final Map<String, dynamic> corpo = resultado['body'];

      if (status == 200) {
        if (!mounted) return;

        // Extrai e persiste o JWT para uso nas requisições autenticadas
        final String? token = corpo['access_token'];
        if (token != null) {
          await StorageService().saveToken(token);
        }

        _exibirMensagem("Acesso autorizado!", Colors.green);

        // pushAndRemoveUntil impede voltar para login/2fa após entrar no app
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (context) => const HomeScreen()),
          (route) => false,
        );
      } else {
        _exibirMensagem(corpo['detail']?.toString() ?? "Código inválido.", Colors.red);
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

                // Exibe os recovery codes logo após a chave TOTP, apenas no registro
                if (widget.recoveryCodes != null) ...[
                  const SizedBox(height: 20),
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.orange.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.orange.withOpacity(0.4)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.warning_amber_rounded, color: Colors.orange, size: 18),
                            SizedBox(width: 6),
                            Text(
                              "Códigos de recuperação",
                              style: TextStyle(fontWeight: FontWeight.bold, color: Colors.orange),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          "Guarde esses códigos em local seguro. Use um deles para acessar sua conta caso perca o autenticador. Cada código funciona apenas uma vez.",
                          style: TextStyle(fontSize: 12, color: Colors.black54),
                        ),
                        const SizedBox(height: 10),
                        // Grade de 2 colunas com os 8 códigos
                        Wrap(
                          spacing: 8,
                          runSpacing: 6,
                          children: widget.recoveryCodes!.map((c) => Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(6),
                              border: Border.all(color: Colors.orange.withOpacity(0.3)),
                            ),
                            child: Text(c, style: const TextStyle(fontFamily: 'monospace', fontWeight: FontWeight.bold)),
                          )).toList(),
                        ),
                        const SizedBox(height: 8),
                        // Botão para copiar todos de uma vez
                        TextButton.icon(
                          onPressed: () {
                            Clipboard.setData(ClipboardData(text: widget.recoveryCodes!.join('\n')));
                            _exibirMensagem("Códigos copiados!", Colors.orange);
                          },
                          icon: const Icon(Icons.copy, size: 16, color: Colors.orange),
                          label: const Text("Copiar todos", style: TextStyle(color: Colors.orange)),
                        ),
                      ],
                    ),
                  ),
                ],
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