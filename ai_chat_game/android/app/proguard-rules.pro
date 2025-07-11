# Flutter and Dart
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }
-keep class io.flutter.embedding.** { *; }

# FlutterSecureStorage
-keep class com.it_nomads.fluttersecurestorage.** { *; }

# WebSocket and networking (if any)
-keep class okhttp3.** { *; }
-keep class okio.** { *; }

# Keep Firebase and Google Play Services (if used)
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.** { *; }

# General rules for reflection and JSON parsing
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-keepattributes Signature
-keepattributes *Annotation*
-keepclassmembers enum * {
    public static **[] values();
    public static ** valueOf(java.lang.String);
}

# Keep your own classes
-keep class com.example.ai_chat_game.** { *; }

