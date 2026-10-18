// Writes ColorScheme.fromSeed's colors for a set of seeds, every variant, both brightnesses and three contrast
// levels to the JSON file named by M3_REF_OUT. Run by tests/run_all.py --refresh-flutter.
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

String hex(Color c) => '#${c.toARGB32().toRadixString(16).padLeft(8, '0').substring(2).toUpperCase()}';

Map<String, String> roles(ColorScheme s) => {
      'primary': hex(s.primary), 'onPrimary': hex(s.onPrimary),
      'primaryContainer': hex(s.primaryContainer), 'onPrimaryContainer': hex(s.onPrimaryContainer),
      'primaryFixed': hex(s.primaryFixed), 'primaryFixedDim': hex(s.primaryFixedDim),
      'onPrimaryFixed': hex(s.onPrimaryFixed), 'onPrimaryFixedVariant': hex(s.onPrimaryFixedVariant),
      'secondary': hex(s.secondary), 'onSecondary': hex(s.onSecondary),
      'secondaryContainer': hex(s.secondaryContainer), 'onSecondaryContainer': hex(s.onSecondaryContainer),
      'secondaryFixed': hex(s.secondaryFixed), 'secondaryFixedDim': hex(s.secondaryFixedDim),
      'onSecondaryFixed': hex(s.onSecondaryFixed), 'onSecondaryFixedVariant': hex(s.onSecondaryFixedVariant),
      'tertiary': hex(s.tertiary), 'onTertiary': hex(s.onTertiary),
      'tertiaryContainer': hex(s.tertiaryContainer), 'onTertiaryContainer': hex(s.onTertiaryContainer),
      'tertiaryFixed': hex(s.tertiaryFixed), 'tertiaryFixedDim': hex(s.tertiaryFixedDim),
      'onTertiaryFixed': hex(s.onTertiaryFixed), 'onTertiaryFixedVariant': hex(s.onTertiaryFixedVariant),
      'error': hex(s.error), 'onError': hex(s.onError),
      'errorContainer': hex(s.errorContainer), 'onErrorContainer': hex(s.onErrorContainer),
      'surface': hex(s.surface), 'onSurface': hex(s.onSurface),
      'surfaceDim': hex(s.surfaceDim), 'surfaceBright': hex(s.surfaceBright),
      'surfaceContainerLowest': hex(s.surfaceContainerLowest), 'surfaceContainerLow': hex(s.surfaceContainerLow),
      'surfaceContainer': hex(s.surfaceContainer), 'surfaceContainerHigh': hex(s.surfaceContainerHigh),
      'surfaceContainerHighest': hex(s.surfaceContainerHighest), 'onSurfaceVariant': hex(s.onSurfaceVariant),
      'outline': hex(s.outline), 'outlineVariant': hex(s.outlineVariant),
      'shadow': hex(s.shadow), 'scrim': hex(s.scrim),
      'inverseSurface': hex(s.inverseSurface), 'inverseOnSurface': hex(s.onInverseSurface),
      'inversePrimary': hex(s.inversePrimary), 'surfaceTint': hex(s.surfaceTint),
    };

void main() {
  test('reference colors', () {
    const seeds = ['#6750A4', '#47DEFE', '#B33B15', '#0B57D0', '#386A20'];
    final out = <Map<String, Object>>[];
    for (final s in seeds) {
      final seed = Color(int.parse('FF${s.substring(1)}', radix: 16));
      for (final v in DynamicSchemeVariant.values) {
        for (final b in Brightness.values) {
          for (final contrast in [0.0, 0.5, 1.0]) {
            if (contrast != 0.0 && v != DynamicSchemeVariant.tonalSpot) continue;
            final cs = ColorScheme.fromSeed(
                seedColor: seed, brightness: b, dynamicSchemeVariant: v, contrastLevel: contrast);
            out.add({
              'seed': s, 'variant': v.name, 'mode': b == Brightness.dark ? 'dark' : 'light',
              'contrast': contrast, 'colors': roles(cs),
            });
          }
        }
      }
    }
    File(Platform.environment['M3_REF_OUT']!).writeAsStringSync(const JsonEncoder.withIndent(' ').convert(out));
  });
}
