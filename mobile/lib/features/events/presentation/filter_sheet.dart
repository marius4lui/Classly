import 'package:flutter/material.dart';

class FilterSheet extends StatelessWidget {
  const FilterSheet({
    required this.types,
    required this.subjects,
    this.selectedType,
    this.selectedSubject,
    this.onTypeSelected,
    this.onSubjectSelected,
    super.key,
  });

  final List<String> types;
  final List<String> subjects;
  final String? selectedType;
  final String? selectedSubject;
  final ValueChanged<String?>? onTypeSelected;
  final ValueChanged<String?>? onSubjectSelected;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Filter', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 20),
            Text('Typ', style: Theme.of(context).textTheme.labelMedium),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: types.map((type) {
                return ChoiceChip(
                  label: Text(type),
                  selected: selectedType == type,
                  onSelected: (_) =>
                      onTypeSelected?.call(selectedType == type ? null : type),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),
            Text('Fach', style: Theme.of(context).textTheme.labelMedium),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: subjects.map((subject) {
                return ChoiceChip(
                  label: Text(subject),
                  selected: selectedSubject == subject,
                  onSelected: (_) => onSubjectSelected?.call(
                    selectedSubject == subject ? null : subject,
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}
