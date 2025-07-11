import 'dart:convert';
import 'package:http/http.dart' as http;
import 'auth_service.dart';

const String baseUrl = "http://127.0.0.1:8000"; // 🛠️ Use LAN IP for real device testing

class ApiService {
  /// 🔹 Fetch all active lobbies (GET /lobbies/)
  static Future<List<Map<String, dynamic>>> fetchLobbies() async {
    final token = await AuthService.getToken();
    if (token == null) throw Exception("⚠️ Missing auth token");

    final response = await http.get(
      Uri.parse('$baseUrl/lobbies/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> rawData = jsonDecode(response.body);
      return rawData.cast<Map<String, dynamic>>();
    } else {
      throw Exception("❌ Failed to fetch lobbies: ${response.statusCode} ${response.body}");
    }
  }

  /// 🔹 Create a new lobby (POST /lobbies/)
  /// Returns the created lobby object as Map, so you can access id, name, etc.
  static Future<Map<String, dynamic>> createLobby({
    required String name,
    bool isPrivate = false,
    int maxParticipants = 10,
    int aiBots = 0,
  }) async {
    final token = await AuthService.getToken();
    if (token == null) throw Exception("⚠️ Missing auth token");

    final response = await http.post(
      Uri.parse('$baseUrl/lobbies/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        "name": name,
        "is_private": isPrivate,
        "max_participants": maxParticipants,
        "ai_bots": aiBots,
      }),
    );

    if (response.statusCode == 201) {
      final Map<String, dynamic> data = jsonDecode(response.body);
      if (!data.containsKey('id')) {
        throw Exception("✅ Lobby created but no ID returned");
      }
      return data;
    } else {
      throw Exception("❌ Failed to create lobby: ${response.statusCode} ${response.body}");
    }
  }

  /// 🔹 Get leaderboard data (GET /leaderboard)
  static Future<List<Map<String, dynamic>>> getLeaderboard() async {
    final token = await AuthService.getToken();
    if (token == null) throw Exception("⚠️ Missing auth token");

    final response = await http.get(
      Uri.parse('$baseUrl/leaderboard'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception("❌ Failed to fetch leaderboard: ${response.statusCode} ${response.body}");
    }
  }
}
