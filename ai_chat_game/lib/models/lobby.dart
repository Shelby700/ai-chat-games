
class Lobby {
  final String id;
  final String name;
  final int playerCount;

  Lobby({
    required this.id,
    required this.name,
    required this.playerCount,
  });

  factory Lobby.fromJson(Map<String, dynamic> json) {
    return Lobby(
      id: json['id'],
      name: json['name'],
      playerCount: json['player_count'] ?? 0,
    );
  }
}
