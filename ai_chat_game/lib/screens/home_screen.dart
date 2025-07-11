import 'package:flutter/material.dart';
import '../utils/auth.dart';
import 'lobby_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  @override
  void initState() {
    super.initState();
    Auth.init(); // Initializes shared preferences
  }

  void _handleLogin() async {
    final result = await Auth.login(_usernameController.text, _passwordController.text);
    if (result['token'] != null) {
      Navigator.push(context, MaterialPageRoute(builder: (_) => const LobbyScreen()));
    } else {
      _showError(result['error'] ?? "Login failed");
    }
  }

  void _handleSignup() async {
    final result = await Auth.signup(_usernameController.text, _passwordController.text);
    if (result['token'] != null) {
      Navigator.push(context, MaterialPageRoute(builder: (_) => const LobbyScreen()));
    } else {
      _showError(result['error'] ?? "Signup failed");
    }
  }

  void _handleGuest() async {
    final result = await Auth.guest();
    if (result['token'] != null) {
      Navigator.push(context, MaterialPageRoute(builder: (_) => const LobbyScreen()));
    } else {
      _showError(result['error'] ?? "Guest login failed");
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Login / Signup")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: _usernameController, decoration: const InputDecoration(labelText: "Username")),
            TextField(controller: _passwordController, decoration: const InputDecoration(labelText: "Password"), obscureText: true),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: _handleLogin, child: const Text("Login")),
            ElevatedButton(onPressed: _handleSignup, child: const Text("Signup")),
            ElevatedButton(onPressed: _handleGuest, child: const Text("Continue as Guest")),
          ],
        ),
      ),
    );
  }
}
