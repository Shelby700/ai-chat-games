import 'package:flutter/material.dart';
import 'package:ai_chat_game/screens/home_screen.dart';
import 'package:ai_chat_game/screens/lobby_screen.dart';
import 'package:ai_chat_game/screens/chat_screen.dart';
import 'package:ai_chat_game/utils/auth.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Auth.init();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Chat Game',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue),
      initialRoute: '/',
      routes: {
        '/': (context) => const HomeScreen(),
        '/lobby': (context) => const LobbyScreen(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/chat') {
          final args = settings.arguments as Map<String, dynamic>;
          return MaterialPageRoute(
            builder: (_) => ChatScreen(
              lobbyId: args['lobbyId'],
              username: args['username'],
              token: args['token'],
            ),
          );
        }
        return null;
      },
    );
  }
}
