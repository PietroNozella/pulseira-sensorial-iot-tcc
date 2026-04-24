import 'package:flutter_test/flutter_test.dart';

import 'package:pulseira_sensorial/main.dart';

void main() {
  testWidgets('MyApp abre a tela de login', (tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('FallSense - Login'), findsOneWidget);
    expect(find.text('Entrar'), findsOneWidget);
    expect(find.text('Esqueci minha senha'), findsOneWidget);
  });
}
