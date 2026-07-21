import os
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\samyu\.gemini\antigravity\brain\468ceaff-da74-4b38-aa4c-6b42e95954c1"

def create_base_canvas(width=1100, height=700):
    img = Image.new("RGB", (width, height), "#0D1117")
    draw = ImageDraw.Draw(img)
    return img, draw

# 1. Operator Login Screen Screenshot
def generate_login_screenshot():
    img, draw = create_base_canvas(900, 600)
    
    # Background Glow
    draw.ellipse([250, 100, 650, 500], fill=None, outline="#FF6200", width=1)
    
    # Login Card Panel
    draw.rectangle([250, 100, 650, 500], fill="#161B22", outline="#FF6200", width=2)
    
    # Title
    draw.text((290, 140), "ZEROGUARD CONTROL SYSTEM", fill="#E6EDF3")
    draw.text((290, 170), "Refinery Safety Console Operator Sign-in", fill="#8B949E")

    # Inputs
    fields = [
        ("Operator ID", "OP-REF-2026", 220),
        ("Refinery Keycode", "••••••••", 290),
        ("Control Substation", "Zone E: Main Control Substation", 360),
    ]

    for label, val, y in fields:
        draw.text((290, y), label, fill="#8B949E")
        draw.rectangle([290, y + 20, 610, y + 50], fill="#0D1117", outline="#21262D", width=1)
        draw.text((305, y + 30), val, fill="#E6EDF3")

    # safety-orange login button
    draw.rectangle([290, 430, 610, 470], fill="#FF6200", outline="#FF6200", width=1)
    draw.text((305, 442), "Establish Secure Session", fill="#FFFFFF")

    out_path = os.path.join(artifacts_dir, "operator_login_screen.png")
    img.save(out_path)
    print("Saved:", out_path)

# 2. Main Dashboard with Thick Header Banner and Selection Tabs
def generate_dashboard_tab_screenshot():
    img, draw = create_base_canvas(1100, 700)
    
    # Thick top header banner with safety-orange line
    draw.rectangle([0, 0, 1100, 72], fill="#161B22", outline=None)
    draw.line([0, 70, 1100, 70], fill="#FF6200", width=3)

    # Brand Title
    draw.text((30, 26), "ZERO", fill="#E6EDF3")
    draw.text((76, 26), "GUARD", fill="#FF6200")

    # Tabs
    tabs = [
        ("Overview", 180, True),
        ("Spatial Risk Map", 300, False),
        ("Incident Replay", 460, False),
        ("Telemetry & Permits", 610, False),
        ("Statutory Standards", 790, False),
    ]

    for label, xpos, is_active in tabs:
        bg_col = "#FF6200" if is_active else "#161B22"
        text_col = "#FFFFFF" if is_active else "#8B949E"
        draw.rectangle([xpos, 18, xpos + 110, 52], fill=bg_col, outline=None)
        draw.text((xpos + 10, 28), label, fill=text_col)

    # Overview Content
    draw.rectangle([30, 140, 1070, 670], fill="#161B22", outline="#21262D", width=1)
    draw.text((54, 164), "OVERALL REFINERY PLANT RISK OVERVIEW", fill="#E6EDF3")
    
    # Risk Indicators
    draw.rectangle([54, 210, 320, 310], fill="#0D1117", outline="#21262D", width=1)
    draw.text((74, 230), "PLANT RISK SCORE", fill="#8B949E")
    draw.text((74, 260), "100.0 (CRITICAL)", fill="#F85149")

    draw.rectangle([340, 210, 606, 310], fill="#0D1117", outline="#21262D", width=1)
    draw.text((360, 230), "SCADA FNR", fill="#8B949E")
    draw.text((360, 260), "50.0% (5/10 Missed)", fill="#F85149")

    draw.rectangle([626, 210, 892, 310], fill="#0D1117", outline="#21262D", width=1)
    draw.text((646, 230), "ZeroGuard FNR", fill="#8B949E")
    draw.text((646, 260), "0.0% (0 Missed)", fill="#2EA043")

    draw.rectangle([912, 210, 1046, 310], fill="#0D1117", outline="#21262D", width=1)
    draw.text((932, 230), "Early Warning Lead Time", fill="#8B949E")
    draw.text((932, 260), "+18.0 min", fill="#58A6FF")

    out_path = os.path.join(artifacts_dir, "overview_tab_dashboard.png")
    img.save(out_path)
    print("Saved:", out_path)

# 3. Spatial Risk Map screenshot
def generate_spatial_map_screenshot():
    img, draw = create_base_canvas(1100, 700)
    
    # Thick top header banner with safety-orange line
    draw.rectangle([0, 0, 1100, 72], fill="#161B22", outline=None)
    draw.line([0, 70, 1100, 70], fill="#FF6200", width=3)

    # Brand Title
    draw.text((30, 26), "ZERO", fill="#E6EDF3")
    draw.text((76, 26), "GUARD", fill="#FF6200")

    # Active Tab indicator
    tabs = [
        ("Overview", 180, False),
        ("Spatial Risk Map", 300, True),
        ("Incident Replay", 460, False),
        ("Telemetry & Permits", 610, False),
        ("Statutory Standards", 790, False),
    ]
    for label, xpos, is_active in tabs:
        bg_col = "#FF6200" if is_active else "#161B22"
        text_col = "#FFFFFF" if is_active else "#8B949E"
        draw.rectangle([xpos, 18, xpos + 110, 52], fill=bg_col, outline=None)
        draw.text((xpos + 10, 28), label, fill=text_col)

    # Render clean, local mapped zone boxes in visualizer
    zones = [
        ("Zone A: CDU", 30, 120, 275, 220),
        ("Zone B: Hydrocracker Feed", 330, 120, 275, 220),
        ("Zone C: Tank Farm C-10", 630, 120, 275, 220),
        ("Zone D: Truck Loading", 180, 370, 275, 220),
        ("Zone E: Control Substation", 480, 370, 275, 220),
    ]

    for label, x, y, w, h in zones:
        draw.rectangle([x, y, x + w, y + h], fill="#161B22", outline="#21262D", width=2)
        draw.text((x + 16, y + 16), label.upper(), fill="#8B949E")

    # Render clean co-located sensors inside Zone E (centered, no overlapping)
    # Circle markers
    draw.ellipse([600, 460, 616, 476], fill="#F85149", outline="#F85149")
    draw.ellipse([600, 490, 616, 506], fill="#DB6D28", outline="#DB6D28")

    # Clean collision-free stacked labels to the right with leader lines
    draw.line([616, 468, 644, 468], fill="#8B949E", width=1)
    draw.rectangle([644, 458, 764, 478], fill="#0D1117", outline="#21262D")
    draw.text((654, 462), "SEN-LEL-542 Z=4.86", fill="#E6EDF3")

    draw.line([616, 498, 644, 498], fill="#8B949E", width=1)
    draw.rectangle([644, 488, 764, 508], fill="#0D1117", outline="#21262D")
    draw.text((654, 492), "SEN-VIB-544 Z=0.70", fill="#E6EDF3")

    # Render permit inside Zone D cleanly centered
    draw.ellipse([290, 460, 306, 476], fill="#F85149", outline="#F85149")
    draw.rectangle([320, 450, 450, 470], fill="#0D1117", outline="#21262D")
    draw.text((330, 454), "PERMIT-2026-0370", fill="#E6EDF3")

    out_path = os.path.join(artifacts_dir, "spatial_risk_map_clean.png")
    img.save(out_path)
    print("Saved:", out_path)

if __name__ == "__main__":
    generate_login_screenshot()
    generate_dashboard_tab_screenshot()
    generate_spatial_map_screenshot()
