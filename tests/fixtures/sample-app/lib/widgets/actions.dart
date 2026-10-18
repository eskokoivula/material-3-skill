import 'package:flutter/material.dart';

/// Three ways to name an icon button: a tooltip, a Semantics label, the icon's semanticLabel. One button has none.
class ActionsRow extends StatelessWidget {
  const ActionsRow({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        IconButton(tooltip: 'Share', icon: const Icon(Icons.share), onPressed: () {}),
        Semantics(
          label: 'Add item',
          child: IconButton(icon: const Icon(Icons.add), onPressed: () {}),
        ),
        IconButton(icon: const Icon(Icons.more_vert), onPressed: () {}),
        IconButton(icon: const Icon(Icons.delete, semanticLabel: 'Delete'), onPressed: () {}),
      ],
    );
  }
}
