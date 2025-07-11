import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

/// ✅ Use your LAN IP if testing on real device
const String baseUrl = "http://127.0.0.1:8000";

class AuthService {
  static const _storage = FlutterSecureStorage();
  static const _tokenKey = 'jwt_token';
  static const _userKey = 'username';

  /// 🔐 Save JWT and username securely
  static Future<void> saveToken(String token, String username) async {
    await _storage.write(key: _tokenKey, value: token);
    await _storage.write(key: _userKey, value: username);
  }

  /// 🔍 Retrieve saved JWT
  static Future<String?> getToken() => _storage.read(key: _tokenKey);

  /// 🔍 Retrieve saved username
  static Future<String?> getUsername() => _storage.read(key: _userKey);

  /// 🔓 Clear all saved data (logout)
  static Future<void> logout() async {
    await _storage.deleteAll();
  }

  /// ✅ Log in with credentials (POST /auth/login)
  static Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        "username": username,
        "password": password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['access_token'];
      if (token == null) throw Exception("Token missing from response");

      await saveToken(token, username);
      return {
        'token': token,
        'username': username,
      };
    } else {
      throw Exception(_parseError(response) ?? 'Login failed');
    }
  }

  /// ✅ Register new user (POST /auth/register)
  static Future<void> signup(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        "username": username,
        "password": password,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception(_parseError(response) ?? 'Signup failed');
    }
  }

  /// ✅ Guest login (POST /auth/guest-login)
  static Future<Map<String, dynamic>> guestLogin() async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/guest-login'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['access_token'];
      final username = data['username'] ?? 'guest';

      if (token == null) throw Exception("Guest token missing");

      await saveToken(token, username);
      return {
        'token': token,
        'username': username,
      };
    } else {
      throw Exception(_parseError(response) ?? 'Guest login failed');
    }
  }

  /// 🧼 Parses readable error message from backend
  static String? _parseError(http.Response response) {
    try {
      final data = jsonDecode(response.body);
      return data['detail']?.toString() ?? data.toString();
    } catch (_) {
      return response.body;
    }
  }
}
