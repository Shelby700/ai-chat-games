import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

class ChatScreen extends StatefulWidget {
  final String lobbyId;
  final String username;
  final String token;

  const ChatScreen({
    Key? key,
    required this.lobbyId,
    required this.username,
    required this.token,
  }) : super(key: key);

  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  late WebSocketChannel channel;
  final messageController = TextEditingController();
  final scrollController = ScrollController();
  List<String> messages = [];

  @override
  void initState() {
    super.initState();
    connectWebSocket();
  }

  void connectWebSocket() {
    channel = WebSocketChannel.connect(
      Uri.parse(
        'ws://10.0.2.2:8000/ws/${widget.lobbyId}/${widget.username}?token=${widget.token}',
      ),
    );
    channel.stream.listen(
      (msg) {
        setState(() {
          messages.add(msg);
        });
        scrollToBottom();
      },
      onError: (err) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('WebSocket error: $err')),
        );
      },
      onDone: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Connection closed')),
        );
      },
    );
  }

  void sendMessage() {
    final text = messageController.text.trim();
    if (text.isNotEmpty) {
      final payload = jsonEncode({
        'action': 'send_message',
        'text': text,
      });
      channel.sink.add(payload);
      messageController.clear();
    }
  }

  void scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (scrollController.hasClients) {
        scrollController.animateTo(
          scrollController.position.maxScrollExtent,
          duration: Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    channel.sink.close(status.goingAway);
    messageController.dispose();
    scrollController.dispose();
    super.dispose();
  }

  Widget buildMessageBubble(String msg) {
    final isTrivia = msg.toLowerCase().contains('trivia') ||
        msg.toLowerCase().contains('🧠');
    final isScore = msg.toLowerCase().contains('score') ||
        msg.toLowerCase().contains('leaderboard') ||
        msg.toLowerCase().contains('🏆');
    final isBot = msg.toLowerCase().startsWith('gpt-muse');

    final color = isTrivia
        ? Colors.orange.shade100
        : isScore
            ? Colors.green.shade100
            : isBot
                ? Colors.purple.shade100
                : Colors.blue.shade100;

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        msg,
        style: TextStyle(
          fontWeight: (isTrivia || isScore) ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Lobby Chat - ${widget.lobbyId.substring(0, 6)}'),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: scrollController,
              itemCount: messages.length,
              itemBuilder: (context, index) =>
                  buildMessageBubble(messages[index]),
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: messageController,
                      decoration: InputDecoration(
                        hintText: 'Type a message or answer...',
                        border: OutlineInputBorder(),
                      ),
                      onSubmitted: (_) => sendMessage(),
                    ),
                  ),
                  SizedBox(width: 8),
                  IconButton(
                    icon: Icon(Icons.send),
                    onPressed: sendMessage,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
