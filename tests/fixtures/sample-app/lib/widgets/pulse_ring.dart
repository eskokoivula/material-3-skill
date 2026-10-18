import 'package:flutter/material.dart';

/// A ring that pulses forever behind the reward count, whatever the platform's motion setting.
class PulseRing extends StatefulWidget {
  const PulseRing({super.key, required this.child});

  final Widget child;

  @override
  State<PulseRing> createState() => _PulseRingState();
}

class _PulseRingState extends State<PulseRing> with SingleTickerProviderStateMixin {
  late final AnimationController _pulse = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1400),
  )..repeat(reverse: true);

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(scale: Tween(begin: 0.96, end: 1.04).animate(_pulse), child: widget.child);
  }
}
