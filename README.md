📱 AI Chat Game – Build & Release Instructions
✅ Framework: Flutter
Language: Dart

Mobile SDK: Flutter

Target OS: Android 10+

Backend: FastAPI (optional)

State Management: setState / optionally provider

Signing: Custom keystore + release config

📦 Requirements
🔧 Tools to Install:
Tool	Version (Recommended)
Flutter SDK	>=3.10.0
Dart SDK	Included with Flutter
Android Studio	Latest with Android SDK & NDK
JDK	JDK 11 or 17
Git	Any recent version

✅ Confirm Flutter is installed:

flutter doctor
📁 Project Structure
lib/
 ┣ main.dart
 ┣ screens/
 ┃ ┣ home_screen.dart
 ┃ ┣ lobby_screen.dart     
 ┃ ┣ chat_screen.dart
 ┃ ┗ leaderboard_screen.dart
 ┣ services/
 ┃ ┣ websocket_service.dart
 ┃ ┗ lobby_service.dart    
 ┣ models/
 ┃ ┣ lobby.dart
 ┃ ┣ message.dart
 ┗ utils/
    ┗ auth.dart
🔐 Step 1: Keystore Setup
Generate the keystore:

keytool -genkey -v -keystore chatgame-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias chatgame
Move chatgame-key.jks to:

android/app/chatgame-key.jks
Create android/key.properties:

properties
storePassword=your_keystore_password
keyPassword=your_key_password
keyAlias=chatgame
storeFile=chatgame-key.jks
🧱 Step 2: Verify build.gradle.kts Setup
Ensure in android/app/build.gradle.kts:

signingConfigs {
    create("release") {
        keyAlias = keystoreProperties["keyAlias"] as String?
        keyPassword = keystoreProperties["keyPassword"] as String?
        storeFile = file(keystoreProperties["storeFile"] as String?)
        storePassword = keystoreProperties["storePassword"] as String?
    }
}
And release block:

kotlin
Copy
Edit
buildTypes {
    getByName("release") {
        signingConfig = signingConfigs.getByName("release")
        isMinifyEnabled = false
        isShrinkResources = false
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
🛠️ Step 3: Install Dependencies

flutter pub get
🚀 Step 4: Build APK

flutter clean
flutter build apk --release
✅ Output:

build/app/outputs/flutter-apk/app-release.apk
📤 Step 5: Share APK
Options:

Upload to Google Drive and share link

Create GitHub Release and attach APK

Use services like WeTransfer or AnonFiles

🧪 Optional: Build for Android App Bundle (.aab)

flutter build appbundle --release
✅ Output:

build/app/outputs/bundle/release/app-release.aab
Use .aab when publishing to Google Play Store.

❓Troubleshooting
Issue	Fix
keytool not found	Add Java JDK /bin to your system PATH
R8 errors / missing classes	Disable minifyEnabled or add ProGuard rules
APK not installing	Enable "Install unknown apps" in device settings
