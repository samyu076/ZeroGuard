import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))
print(f'Total records: {len(data)}')

labels = {}
for s in data:
    label = s['ground_truth_label']
    labels[label] = labels.get(label, 0) + 1

print(f'Label distribution: {labels}')

total = len(data)
print(f'Percentages:')
print(f'  SAFE: {labels.get("SAFE", 0)/total*100:.2f}%')
print(f'  WATCH: {labels.get("WATCH", 0)/total*100:.2f}%')
print(f'  WARNING: {labels.get("WARNING", 0)/total*100:.2f}%')
print(f'  COMPOUND_CRITICAL: {labels.get("COMPOUND_CRITICAL", 0)/total*100:.2f}%')

