from app.services.deduplication import annotate_duplicates

cases = [
    # text A, text B, location A, location B, expected duplicate
    ("Flood water rising fast near Rampur",
     "Flood water rising fast near Rampur", "Rampur", "Rampur", True),

    ("Urgent rescue needed for trapped people",
     "Urgent rescue needed for trapped people", "Rampur", "Rampur", True),

    ("Fire reported near the school",
     "Earthquake damage reported in the village", "Rampur", "Rampur", False),

    ("Flood water rising near Rampur",
     "Flood water rising near Rampur", "Rampur", "Shivpur", False),
]

tp = fp = fn = tn = 0

for index, (text_a, text_b, loc_a, loc_b, expected) in enumerate(cases, 1):
    reports = [
        {
            "incident_id": f"A{index}",
            "text": text_a,
            "location_name": loc_a,
            "incident_type": "general_emergency",
        },
        {
            "incident_id": f"B{index}",
            "text": text_b,
            "location_name": loc_b,
            "incident_type": "general_emergency",
        },
    ]

    result = annotate_duplicates(reports)
    predicted = result[1]["duplicate_of"] is not None

    if predicted and expected:
        tp += 1
    elif predicted and not expected:
        fp += 1
    elif not predicted and expected:
        fn += 1
    else:
        tn += 1

    print(
        f"Case {index}: expected={expected}, "
        f"predicted={predicted}, "
        f"result={'PASS' if predicted == expected else 'FAIL'}"
    )

precision = tp / (tp + fp) if tp + fp else 0
recall = tp / (tp + fn) if tp + fn else 0
accuracy = (tp + tn) / len(cases)

print("\nEvaluation cases:", len(cases))
print(f"TP: {tp} FP: {fp} FN: {fn} TN: {tn}")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"Accuracy: {accuracy:.2%}")
print("Note: Four controlled test cases; not a representative benchmark.")
