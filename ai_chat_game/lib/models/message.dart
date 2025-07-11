class Message {
  final String username;
  final String content;
  final bool isBot;

  Message({
    required this.username,
    required this.content,
    required this.isBot,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      username: json['username'] ?? 'Unknown',
      content: json['content'] ?? '',
      isBot: json['is_bot'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'content': content,
      'is_bot': isBot,
    };
  }
}
