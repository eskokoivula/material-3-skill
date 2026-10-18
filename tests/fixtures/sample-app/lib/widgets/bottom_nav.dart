import 'package:flutter/material.dart';

import '../screens/hint_screen.dart';
import '../screens/reward_screen.dart';

/// The app's shell. A BottomNavigationBar named in a doc comment is not a use.
const String legacyNote = 'BottomNavigationBar() in a string is not a use either';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _index == 0 ? const RewardScreen() : const HintScreen(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _index,
        onTap: (i) => setState(() => _index = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.lightbulb), label: 'Hint'),
        ],
      ),
    );
  }
}
