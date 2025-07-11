import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class Auth {
  static late SharedPreferences _prefs;
  static const _baseUrl = 'http://10.0.2.2:8000'; // emulator access to localhost

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  static Future<Map<String, String?>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse("$_baseUrl/auth/login"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"username": username, "password": password}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _prefs.setString('token', data['access_token']);
      await _prefs.setString('username', username);
      return {'token': data['access_token']};
    } else {
      return {'error': jsonDecode(response.body)['detail'].toString()};
    }
  }

  static Future<Map<String, String?>> signup(String username, String password) async {
    final response = await http.post(
      Uri.parse("$_baseUrl/auth/register"), // ✅ updated
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"username": username, "password": password}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _prefs.setString('token', data['access_token']);
      await _prefs.setString('username', username);
      return {'token': data['access_token']};
    } else {
      return {'error': jsonDecode(response.body)['detail'].toString()};
    }
  }

  static Future<Map<String, String?>> guest() async {
    final guestName = 'guest_${DateTime.now().millisecondsSinceEpoch}';
    final response = await http.post(
      Uri.parse("$_baseUrl/auth/guest-login"), // ✅ updated
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"username": guestName}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await _prefs.setString('token', data['access_token']);
      await _prefs.setString('username', guestName);
      return {'token': data['access_token']};
    } else {
      return {'error': jsonDecode(response.body)['detail'].toString()};
    }
  }

  static Future<String?> getToken() async {
    return _prefs.getString('token');
  }

  static Future<String?> getUsername() async {
    return _prefs.getString('username');
  }

  static Future<void> logout() async {
    await _prefs.remove('token');
    await _prefs.remove('username');
  }
}
