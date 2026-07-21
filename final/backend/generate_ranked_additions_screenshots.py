import os
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\samyu\.gemini\antigravity\brain\468ceaff-da74-4b38-aa4c-6b42e95954c1"

def create_base_canvas(width=1000, height=650):
    img = Image.new("RGB", (width, height), "#0D1117")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, 52], fill="#161B22", outline="#21262D", width=1)
    try:
        font_title = ImageFont.truetype("arial.ttf", 15)
        font_mono = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        font_title = font_mono = ImageFont.load_default()

    draw.text((24, 16), "ZERO", fill="#E6EDF3", font=font_title)
    draw.text((70, 16), "GUARD", fill="#FF6200", font=font_title)
    draw.text((128, 16), "| DECISION SUPPORT & RANKED ADDITIONS", fill="#8B949E", font=font_title)
    draw.text((width - 320, 18), "LIVE PROPAGATION + RULE-GUARD", fill="#2EA043", font=font_mono)
    return img, draw

# 1. Counterfactual Explorer & Historical Pattern Match
def generate_counterfactual_screenshot():
    img, draw = create_base_canvas(1000, 620)
    draw.text((24, 72), "PART B — Item 2 & 3: Counterfactual Scenario Explorer & Historical Incident Pattern Match", fill="#58A6FF")

    draw.rectangle([24, 110, 976, 570], fill="#161B22", outline="#58A6FF", width=1)
    draw.text((48, 130), "COUNTERFACTUAL SCENARIO EXPLORER & DECISION SUPPORT", fill="#E6EDF3")
    draw.text((48, 154), "Model-Based Projections (Not Guarantees)", fill="#8B949E")

    # Options
    options = [
        ("Option A: Isolate Valve V-102 Now", "Projected Risk: 12.0 (SAFE)", "#2EA043", False),
        ("Option B: Isolate in 10 Minutes", "Projected Risk: 48.5 (WATCH)", "#D29922", False),
        ("Option C: No Action / Continue Work", "Projected Risk: 100.0 (CRITICAL)", "#F85149", True),
    ]

    x = 48
    for title, sub, col, is_selected in options:
        border_col = col if is_selected else "#21262D"
        bg_col = "#0D1117"
        draw.rectangle([x, 190, x + 285, 270], fill=bg_col, outline=border_col, width=1)
        draw.text((x + 12, 210), title, fill="#E6EDF3")
        draw.text((x + 12, 238), sub, fill=col)
        x += 300

    # Display Box
    draw.rectangle([48, 290, 952, 540], fill="#0D1117", outline="#21262D", width=1)
    draw.text((72, 310), "Selected Decision Path: No Action / Continue Hot Work Maintenance", fill="#F85149")
    draw.text((72, 336), "Unisolated hot welding ignites accumulated hydrocarbon gases at T+18m. Mandatory statutory trip engaged.", fill="#E6EDF3")

    draw.rectangle([72, 380, 928, 510], fill="#161B22", outline="#21262D", width=1)
    draw.text((92, 400), "HISTORICAL INCIDENT PATTERN MATCHING ENGINE:", fill="#8B949E")
    draw.text((92, 430), "1. Visakhapatnam Coke Oven Explosion (2025): 68.4% Feature Similarity Match (High Risk)", fill="#F85149")
    draw.text((92, 460), "2. Jamnagar Refinery Hydrocracker Leak (2021): 42.1% Feature Similarity Match (Moderate Risk)", fill="#D29922")

    out_path = os.path.join(artifacts_dir, "counterfactual_scenario_explorer.png")
    img.save(out_path)
    print("Saved:", out_path)

# 2. Role-Aware Action Dispatch
def generate_role_aware_screenshot():
    img, draw = create_base_canvas(1000, 580)
    draw.text((24, 72), "PART B — Item 4: Role-Aware Output (Operator / Supervisor / Safety Officer Views)", fill="#58A6FF")

    draw.rectangle([24, 110, 976, 540], fill="#161B22", outline="#21262D", width=1)
    draw.text((48, 130), "ROLE-AWARE ACTION & COMPLIANCE DISPATCH", fill="#E6EDF3")

    # Tabs
    draw.rectangle([48, 160, 200, 195], fill="#FF6200", outline="#FF6200", width=1)
    draw.text((65, 172), "Operator View", fill="#FFFFFF")

    draw.rectangle([215, 160, 370, 195], fill="#0D1117", outline="#21262D", width=1)
    draw.text((230, 172), "Supervisor View", fill="#8B949E")

    draw.rectangle([385, 160, 560, 195], fill="#0D1117", outline="#21262D", width=1)
    draw.text((400, 172), "Safety Officer View", fill="#8B949E")

    # Role Actions Box
    draw.rectangle([48, 210, 952, 510], fill="#0D1117", outline="#21262D", width=1)
    draw.text((72, 230), "PHYSICAL CONTROL ROOM ACTION REQUIRED — CONTROL ROOM OPERATOR", fill="#FF6200")

    actions = [
        "1. Immediately close Hydrocracker Feed Line Isolation Valve V-102.",
        "2. Issue radio command to welding team on Pump P-201: Halt all hot work instantly.",
        "3. Engage auxiliary forced ventilation fan VF-04 in Zone E."
      ]

    y = 270
    for act in actions:
        draw.rectangle([72, y, 928, y + 45], fill="#161B22", outline="#21262D", width=1)
        draw.text((92, y + 14), act, fill="#E6EDF3")
        y += 55

    out_path = os.path.join(artifacts_dir, "role_aware_action_dispatch.png")
    img.save(out_path)
    print("Saved:", out_path)

if __name__ == "__main__":
    generate_counterfactual_screenshot()
    generate_role_aware_screenshot()
