import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import 'styles/app_styles.dart';
import 'widgets/custom_button.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String latestFact = "Henüz veri yok";
  String latestLength = "Bekleniyor...";
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    // Sadece length verisini 5 saniyede bir getir
    _timer = Timer.periodic(const Duration(seconds: 5), (_) {
      fetchLengthOnly();
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> fetchLengthOnly() async {
    final response = await http.get(Uri.parse('https://catfact.ninja/fact'));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        latestLength = "API Length: ${data['length']}";
      });
    } else {
      setState(() {
        latestLength = "API hatası: ${response.statusCode}";
      });
    }
  }

  Future<void> fetchFact() async {
    final response = await http.get(Uri.parse('https://catfact.ninja/fact'));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        latestFact = data['fact'];
      });
    } else {
      setState(() {
        latestFact = "API hatası: ${response.statusCode}";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(kToolbarHeight + 3),
        child: Padding(
          padding: const EdgeInsets.only(top: 3),
          child: AppBar(
            centerTitle: true,
            title: const Text("Binance AI"),
            elevation: 0,
          ),
        ),
      ),
      body: Center(
        child: Container(
          decoration: AppStyles.cardBox,
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text("Api Detaylar", style: AppStyles.heading),
              const SizedBox(height: 10),
              Text(
                latestLength,
                style: AppStyles.heading.copyWith(fontSize: 14),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              CustomButton(
                text: "Veriyi Getir",
                onPressed: fetchFact,
              ),
              const SizedBox(height: 20),
              Text(
                "API Bilgisi:\n$latestFact",
                style: AppStyles.heading,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
