import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:ai_chat_game/utils/auth.dart';

class WebSocketService {
  static WebSocketChannel? _channel;
  static Function(String)? _onMessage;

  static void connect(String lobbyId, Function(String) onMessage) async {
    final token = await Auth.getToken();
    final username = await Auth.getUsername();
    final url = Uri.parse(
        'ws://127.0.0.1:8000/ws/$lobbyId/$username?token=$token');

    _channel = WebSocketChannel.connect(url);
    _onMessage = onMessage;

    _channel!.stream.listen(
      (message) => _onMessage?.call(message),
      onError: (error) => print('WebSocket error: $error'),
      onDone: () => print('WebSocket closed.'),
    );
  }

  static void send(String message) {
    _channel?.sink.add(message);
  }

  static void disconnect() {
    _channel?.sink.close();
  }
}
