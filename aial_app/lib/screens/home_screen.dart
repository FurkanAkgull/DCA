// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import '../styles/app_styles.dart';
import '../widgets/custom_button.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Ana Sayfa")),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text("Merhaba Flutter!", style: AppStyles.heading),
            const SizedBox(height: 16),
            CustomButton(
              text: "Devam Et",
              onPressed: () {
                print("Devam Et butonuna basıldı.");
              },
            ),
          ],
        ),
      ),
    );
  }
}
