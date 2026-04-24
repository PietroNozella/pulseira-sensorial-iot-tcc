import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../../services/storage_service.dart';
import '../../../core/network/api_service.dart';
import '../../../core/theme/app_colors.dart';

class TwoFactorScreen extends StatefulWidget {
  final String email;
  final String senha;
  final String? secretKey;
  final String? totpUri;
  final List<String>? recoveryCodes;

  const TwoFactorScreen({
    super.key,
    required this.email,
    required this.senha,
    this.secretKey,
    this.totpUri,
    this.recoveryCodes,
  });

  @override
  State<TwoFactorScreen> createState() => _TwoFactorScreenState();
}

class _TwoFactorScreenState extends State<TwoFactorScreen> {
  final TextEditingController _codeController = TextEditingController();
  bool _carregando = false;

  Future<void> _validarCodigo() async {
    String codigo = _codeController.text.trim();

    if (codigo.length != 6) {
      _exibirMensagem("O código deve ter 6 dígitos!", AppColors.warning);
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

        final String? token = corpo['access_token'];
        final String? nomeCompleto = corpo['nome_completo'];
        if (token != null) {
          await StorageService().saveToken(token);
        }
        if (nomeCompleto != null && nomeCompleto.trim().isNotEmpty) {
          await StorageService().saveUserName(nomeCompleto.trim());
        }

        _exibirMensagem("Acesso autorizado!", Colors.green);

        Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
      } else {
        _exibirMensagem(corpo['detail']?.toString() ?? "Código inválido.", AppColors.error);
      }
    } catch (e) {
      _exibirMensagem("Erro de conexão com o servidor.", AppColors.error);
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
    final String? totpUri = widget.totpUri;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Segurança FallSense"),
        centerTitle: true,
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.white,
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
              color: AppColors.primary
              ),
              const SizedBox(height: 20),
              Text(
                modoConfiguracao ? "Configure seu Autenticador" : "Verificação de Segurança",
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 15),

              if (modoConfiguracao) ...[
                const Text(
                  "1. Escaneie o QR Code no Google Authenticator\n2. Ou copie a chave manual abaixo\n3. Digite o código de 6 dígitos gerado",
                  textAlign: TextAlign.center,
                style: TextStyle(color: AppColors.textPrimary),
                ),
                const SizedBox(height: 20),
                if (totpUri != null && totpUri.isNotEmpty) ...[
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppColors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
                    ),
                    child: QrImageView(
                      data: totpUri,
                      version: QrVersions.auto,
                      size: 220,
                      backgroundColor: AppColors.white,
                      semanticsLabel: "QR Code para configurar autenticador",
                      errorStateBuilder: (context, error) {
                        return const SizedBox(
                          width: 220,
                          height: 220,
                          child: Center(
                            child: Text(
                              "Não foi possível gerar o QR Code. Use a chave manual abaixo.",
                              textAlign: TextAlign.center,
                              style: TextStyle(color: AppColors.textSecondary),
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 20),
                ] else ...[
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.warning.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.warning.withValues(alpha: 0.3)),
                    ),
                    child: const Text(
                      "QR Code indisponível. Use a chave manual abaixo para configurar o autenticador.",
                      textAlign: TextAlign.center,
                      style: TextStyle(color: AppColors.textSecondary),
                    ),
                  ),
                  const SizedBox(height: 20),
                ],
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: SelectableText(
                          widget.secretKey!,
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontWeight: FontWeight.bold, 
                            fontSize: 18, 
                            letterSpacing: 1.2
                          ),
                        ),
                      ),
                      IconButton(
                      icon: const Icon(Icons.copy, color: AppColors.primary),
                        onPressed: () {
                          Clipboard.setData(ClipboardData(text: widget.secretKey!));
                        _exibirMensagem("Chave copiada!", AppColors.primary);
                        },
                      )
                    ],
                  ),
                ),
                // OS RECOVERY CODES FORAM REMOVIDOS DAQUI PARA LIMPAR A TELA
              ] else ...[
                const Text(
                  "Insira o código de 6 dígitos gerado no seu aplicativo de autenticação.",
                  textAlign: TextAlign.center,
                style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
                ),
              ],

              const SizedBox(height: 30),
              
              TextField(
                controller: _codeController,
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                maxLength: 6,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 32, letterSpacing: 15, fontWeight: FontWeight.bold),
                decoration: InputDecoration(
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  counterText: "", 
                  hintText: "000000",
                hintStyle: const TextStyle(color: AppColors.textTertiary, letterSpacing: 15)
                ),
              ),
              const SizedBox(height: 40),
              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton(
                  onPressed: _carregando ? null : _validarCodigo,
                  style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: _carregando 
                  ? const CircularProgressIndicator(color: AppColors.white)
                  : const Text("VERIFICAR E ENTRAR", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.white)),
                ),
              ),
              const SizedBox(height: 20),
              TextButton(
                onPressed: () => Navigator.pop(context),
              child: const Text("Cancelar", style: TextStyle(color: AppColors.textSecondary)),
              )
            ],
          ),
        ),
      ),
    );
  }
}
