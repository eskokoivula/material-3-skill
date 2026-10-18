import 'package:flutter/material.dart';

/// The brand's colors as a hand-made scheme: nine roles set, the surface containers left to Flutter's fallbacks.
const ColorScheme appColors = ColorScheme(
  brightness: Brightness.dark,
  primary: Color(0xFFFF8A3D),
  onPrimary: Color(0xFF1A0A00),
  secondary: Color(0xFF3D5AFE),
  onSecondary: Color(0xFFFFFFFF),
  error: Color(0xFFFF5252),
  onError: Color(0xFF1A0000),
  surface: Color(0xFF101418),
  onSurface: Color(0xFFF2F5F8),
  onSurfaceVariant: Color(0xFF7A8A99),
);

ThemeData appTheme() => ThemeData(useMaterial3: true, colorScheme: appColors);
