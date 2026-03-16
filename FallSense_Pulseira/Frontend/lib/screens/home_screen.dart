import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // Necessário para a vibração
import '../services/storage_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final StorageService _storageService = StorageService();
  bool _quedaDetectada = false;

  // Função para simular o alerta (Vibração + Mudança de Estado)
  void _acionarAlerta() {
    setState(() {
      _quedaDetectada = !_quedaDetectada;
    });

    if (_quedaDetectada) {
      // Faz o celular vibrar em um padrão de alerta (apenas se for uma queda)
      HapticFeedback.vibrate(); 
      debugPrint("Alerta de queda enviado ao servidor!");
    }
  }

  // Função de Logout
  Future<void> _fazerLogout() async {
    await _storageService.deleteToken();
    if (mounted) {
      Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: const Text("FallSense - Monitoramento"),
        centerTitle: true,
        backgroundColor: _quedaDetectada ? Colors.red : Colors.blueAccent,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: "Sair",
            onPressed: _fazerLogout,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // 1. Card de Status Principal
            _buildStatusCard(),
            
            const SizedBox(height: 25),
            
            // 2. Grid de Dados da Pulseira
            Row(
              children: [
                _buildInfoCard("Bateria", "88%", Icons.battery_std, Colors.green),
                const SizedBox(width: 15),
                _buildInfoCard("Sinal", "Excelente", Icons.bolt, Colors.amber),
              ],
            ),
            
            const SizedBox(height: 25),
            
            // 3. Botão de Ação (Simulador)
            SizedBox(
              width: double.infinity,
              height: 70,
              child: ElevatedButton.icon(
                onPressed: _acionarAlerta,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _quedaDetectada ? Colors.green : Colors.redAccent,
                  foregroundColor: Colors.white,
                  elevation: 8,
                  shadowColor: _quedaDetectada ? Colors.greenAccent : Colors.redAccent,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                ),
                icon: Icon(_quedaDetectada ? Icons.refresh : Icons.warning_rounded, size: 28),
                label: Text(
                  _quedaDetectada ? "NORMALIZAR SISTEMA" : "SIMULAR QUEDA AGORA",
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
              ),
            ),
            
            const SizedBox(height: 15),
            const Text(
              "O sistema está integrado com o acelerômetro da pulseira.\nEste botão serve para testes de software.",
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey, fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }

  // Widget: Card Dinâmico de Status
  Widget _buildStatusCard() {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 400),
      curve: Curves.easeInOut,
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
      decoration: BoxDecoration(
        color: _quedaDetectada ? Colors.red : Colors.white,
        borderRadius: BorderRadius.circular(30),
        boxShadow: [
          BoxShadow(
            color: _quedaDetectada ? Colors.red.withOpacity(0.4) : Colors.black12,
            blurRadius: 20,
            spreadRadius: 2,
            offset: const Offset(0, 8),
          )
        ],
      ),
      child: Column(
        children: [
          // Ícone animado
          TweenAnimationBuilder(
            tween: Tween<double>(begin: 0, end: _quedaDetectada ? 1.1 : 1.0),
            duration: const Duration(milliseconds: 300),
            builder: (context, double scale, child) {
              return Transform.scale(scale: scale, child: child);
            },
            child: Icon(
              _quedaDetectada ? Icons.warning_amber_rounded : Icons.health_and_safety,
              size: 100,
              color: _quedaDetectada ? Colors.white : Colors.blueAccent,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            _quedaDetectada ? "QUEDA DETECTADA!" : "STATUS: SEGURO",
            style: TextStyle(
              fontSize: 26,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
              color: _quedaDetectada ? Colors.white : Colors.black87,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            _quedaDetectada 
                ? "Cuidadores notificados via SMS/Push." 
                : "Monitoramento constante ativado.",
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: _quedaDetectada ? Colors.white70 : Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  // Widget: Cartões de Informação
  Widget _buildInfoCard(String titulo, String valor, IconData icone, Color cor) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(22),
          border: Border.all(color: Colors.grey.withOpacity(0.1)),
          boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, 4))],
        ),
        child: Column(
          children: [
            CircleAvatar(
              backgroundColor: cor.withOpacity(0.1),
              child: Icon(icone, color: cor),
            ),
            const SizedBox(height: 12),
            Text(titulo, style: const TextStyle(color: Colors.grey, fontSize: 14)),
            const SizedBox(height: 4),
            Text(valor, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
          ],
        ),
      ),
    );
  }
}