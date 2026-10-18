import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Shows how to hold the phone: an arrow that swings forever, on a screen locked to portrait.
class HintScreen extends StatefulWidget {
  const HintScreen({super.key});

  @override
  State<HintScreen> createState() => _HintScreenState();
}

class _HintScreenState extends State<HintScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _swing;

  @override
  void initState() {
    super.initState();
    SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
    _swing = AnimationController(vsync: this, duration: const Duration(seconds: 1));
    _swing.repeat(reverse: true);
  }

  @override
  void dispose() {
    _swing.dispose();
    SystemChrome.setPreferredOrientations(DeviceOrientation.values);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RotationTransition(
      turns: Tween(begin: -0.02, end: 0.02).animate(_swing),
      child: const Icon(Icons.screen_rotation, size: 96),
    );
  }
}
