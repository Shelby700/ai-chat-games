import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/lobby.dart';
import '../utils/auth.dart';

class LobbyService {
  static const _baseUrl = 'http://10.0.2.2:8000';

  static Future<List<Lobby>> fetchLobbies() async {
    final token = await Auth.getToken();
    final response = await http.get(
      Uri.parse("$_baseUrl/lobbies/"),
      headers: {"Authorization": "Bearer $token"},
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as List;
      return data.map((e) => Lobby.fromJson(e)).toList();
    }
    return [];
  }

  static Future<Lobby?> createLobby() async {
    final token = await Auth.getToken();
    final response = await http.post(
      Uri.parse("$_baseUrl/lobbies/create"),
      headers: {"Authorization": "Bearer $token"},
    );
    if (response.statusCode == 200) {
      return Lobby.fromJson(jsonDecode(response.body));
    }
    return null;
  }
}
