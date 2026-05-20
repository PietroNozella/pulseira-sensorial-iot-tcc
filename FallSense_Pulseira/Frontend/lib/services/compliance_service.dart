import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:open_file/open_file.dart';

class ComplianceService {
  // URL base do backend no Render
  final String baseUrl = "https://fallsense-api.onrender.com"; 

  Future<void> baixarTermosUso(String usuarioEmail) async {
    try {
      // Endpoint do backend recebendo o e-mail do usuário logado
      final url = Uri.parse('$baseUrl/termos/download?usuario_id=$usuarioEmail');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        // pasta interna do celular para salvar o arquivo temporariamente
        final directory = await getApplicationDocumentsDirectory();
        final filePath = "${directory.path}/FallSense_Termos_de_Uso.pdf";
        
        // bytes salvando o PDF no aparelho
        final file = File(filePath);
        await file.writeAsBytes(response.bodyBytes);

        // Abre o PDF na tela do celular automaticamente
        await OpenFile.open(filePath);
      } else {
        throw Exception("Erro ao buscar documento: ${response.statusCode}");
      }
    } catch (e) {
      throw Exception("Falha no download: $e");
    }
  }
}