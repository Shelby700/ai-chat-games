import 'package:flutter/material.dart';
import 'package:ai_chat_game/utils/auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class LobbyScreen extends StatefulWidget {
  const LobbyScreen({Key? key}) : super(key: key);

  @override
  State<LobbyScreen> createState() => _LobbyScreenState();
}

class _LobbyScreenState extends State<LobbyScreen> {
  List<dynamic> lobbies = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchLobbies();
  }

  Future<void> fetchLobbies() async {
    setState(() => isLoading = true);
    final token = await Auth.getToken();
    final response = await http.get(
      Uri.parse('http://10.0.2.2:8000/lobbies/'),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (response.statusCode == 200) {
      setState(() {
        lobbies = jsonDecode(response.body);
        isLoading = false;
      });
    } else {
      setState(() => isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load lobbies')),
      );
    }
  }

  Future<void> createLobby() async {
    final token = await Auth.getToken();
    final nameController = TextEditingController();
    final maxParticipantsController = TextEditingController(text: '4');

    await showDialog(
      context: context,
      builder: (_) {
        return AlertDialog(
          title: Text('Create Lobby'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: InputDecoration(labelText: 'Lobby Name'),
              ),
              TextField(
                controller: maxParticipantsController,
                decoration: InputDecoration(labelText: 'Max Participants'),
                keyboardType: TextInputType.number,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                final response = await http.post(
                  Uri.parse('http://10.0.2.2:8000/lobbies/'),
                  headers: {
                    'Authorization': 'Bearer $token',
                    'Content-Type': 'application/json',
                  },
                  body: jsonEncode({
                    'name': nameController.text,
                    'is_private': false,
                    'max_participants': int.parse(maxParticipantsController.text),
                    'ai_bots': 1,
                  }),
                );

                Navigator.pop(context);
                if (response.statusCode == 201) {
                  await fetchLobbies();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Failed to create lobby')),
                  );
                }
              },
              child: Text('Create'),
            ),
          ],
        );
      },
    );
  }

  Future<void> joinLobby(String lobbyId) async {
    final token = await Auth.getToken();
    final username = await Auth.getUsername();

    final response = await http.post(
      Uri.parse('http://10.0.2.2:8000/lobbies/$lobbyId/join'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      Navigator.pushNamed(
        context,
        '/chat',
        arguments: {
          'lobbyId': lobbyId,
          'username': username,
          'token': token,
        },
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to join lobby')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Lobbies')),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : lobbies.isEmpty
              ? Center(child: Text('No lobbies available'))
              : ListView.builder(
                  itemCount: lobbies.length,
                  itemBuilder: (context, index) {
                    final lobby = lobbies[index];
                    final participants = lobby['participants'] ?? [];
                    return ListTile(
                      title: Text(lobby['name']),
                      subtitle: Text(
                        '${participants.length}/${lobby['max_participants']} participants',
                      ),
                      trailing: Icon(Icons.arrow_forward),
                      onTap: () => joinLobby(lobby['id']),
                    );
                  },
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: createLobby,
        child: Icon(Icons.add),
      ),
    );
  }
}
