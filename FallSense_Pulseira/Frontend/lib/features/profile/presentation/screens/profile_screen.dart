import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;

// Bibliotecas condicionais para evitar erros de compilação cruzada
import 'dart:io' as io;
import 'package:path_provider/path_provider.dart';
import 'package:open_file/open_file.dart';

// Componente nativo do Flutter para web que lida com downloads no navegador
import 'package:universal_html/html.dart' as html; 

import '../widgets/logout_button_widget.dart';
import '../widgets/profile_header_widget.dart';
import '../widgets/profile_menu_item_widget.dart';
import 'edit_profile_screen.dart';
import '../../../auth/presentation/providers/auth_provider.dart'; 

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  bool _baixandoPdf = false;

  void _mostrarFuncionalidadeEmDesenvolvimento(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Funcionalidade em desenvolvimento.')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final asyncUserProfile = ref.watch(userProfileProvider);

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Perfil',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              const ProfileHeaderWidget(),
              const SizedBox(height: 24),
              Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(18),
                  child: Column(
                    children: [
                      ProfileMenuItemWidget(
                        title: 'Editar Perfil',
                        icon: Icons.edit,
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const EditProfileScreen(),
                            ),
                          );
                        },
                      ),
                      ProfileMenuItemWidget(
                        title: 'Contatos de Emergência',
                        icon: Icons.contact_phone,
                        onTap: () => _mostrarFuncionalidadeEmDesenvolvimento(context),
                      ),
                      
                      // Função Unificada de Download (Indiferente de Chrome ou Celular)
                      _baixandoPdf
                          ? const Padding(
                              padding: EdgeInsets.symmetric(vertical: 14.0),
                              child: SizedBox(
                                height: 24,
                                width: 24,
                                child: CircularProgressIndicator(strokeWidth: 2.5),
                              ),
                            )
                          : ProfileMenuItemWidget(
                              title: 'Segurança e Privacidade',
                              icon: Icons.security,
                              onTap: () async {
                                setState(() => _baixandoPdf = true);
                                
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('Fazendo download dos Termos de Uso (LGPD)...')),
                                );

                                try {
                                  final usuarioEmail = asyncUserProfile.value?.email ?? 'usuario.teste@fallsense.com';
                                  final url = Uri.parse('https://fallsense-api.onrender.com/compliance/termos/download?usuario_id=$usuarioEmail');

                                  // AMBOS fazem exatamente a mesma requisição HTTP para obter os bytes do PDF
                                  final response = await http.get(url);

                                  if (response.statusCode == 200) {
                                    final bytes = response.bodyBytes;
                                    const nomeArquivo = "FallSense_Termos_de_Uso.pdf";

                                    if (kIsWeb) {
                                      // 🌐 FLUXO CHROME: Transforma os bytes recebidos em um download nativo do navegador
                                      final blob = html.Blob([bytes], 'application/pdf');
                                      final urlBlob = html.Url.createObjectUrlFromBlob(blob);
                                      
                                      html.AnchorElement(href: urlBlob)
                                        ..setAttribute("download", nomeArquivo)
                                        ..click(); // Simula o clique de download
                                        
                                      html.Url.revokeObjectUrl(urlBlob); // Limpa a memória
                                    } else {
                                      // 📱 FLUXO CELULAR: Salva os bytes recebidos na pasta do aparelho e abre
                                      final directory = await getTemporaryDirectory();
                                      final filePath = "${directory.path}/$nomeArquivo";
                                      
                                      final file = io.File(filePath);
                                      await file.writeAsBytes(bytes);

                                      await OpenFile.open(filePath);
                                    }

                                    if (!mounted) return;
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(content: Text('Download concluído com sucesso!')),
                                    );
                                  } else {
                                    throw Exception("Erro na API: ${response.statusCode}");
                                  }
                                } catch (e) {
                                  if (!mounted) return;
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(content: Text('Falha ao baixar PDF: $e')),
                                  );
                                } finally {
                                  if (mounted) {
                                    setState(() => _baixandoPdf = false);
                                  }
                                }
                              },
                            ),
                            
                      ProfileMenuItemWidget(
                        title: 'Permissões do App',
                        icon: Icons.phonelink_lock_rounded,
                        onTap: () => _mostrarFuncionalidadeEmDesenvolvimento(context),
                      ),
                      ProfileMenuItemWidget(
                        title: 'Registro Completo de Eventos',
                        icon: Icons.history,
                        onTap: () => _mostrarFuncionalidadeEmDesenvolvimento(context),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 28),
              const LogoutButtonWidget(),
            ],
          ),
        ),
      ),
    );
  }
}