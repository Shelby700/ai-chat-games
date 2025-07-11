import 'package:web_socket_channel/web_socket_channel.dart';

class SimpleWebSocketService {
  final String lobbyId;
  final String username;
  final String token;
  late WebSocketChannel _channel;

  Function(String message)? onMessage;

  SimpleWebSocketService({
    required this.lobbyId,
    required this.username,
    required this.token,
  });

  void connect() {
    final uri = Uri.parse(
      'ws://127.0.0.1:8000/ws/$lobbyId/$username?token=$token',
    );

    _channel = WebSocketChannel.connect(uri);

    _channel.stream.listen(
      (event) {
        print('🔔 Message received: $event');
        if (onMessage != null) onMessage!(event);
      },
      onError: (error) => print('❌ WebSocket error: $error'),
      onDone: () => print('🔌 Connection closed.'),
    );
  }

  void sendMessage(String text) {
    _channel.sink.add(text);
  }

  void disconnect() {
    _channel.sink.close();
  }
}
