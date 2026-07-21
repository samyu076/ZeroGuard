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

if __name__ == "__main__":
    generate_login_screenshot()
    generate_dashboard_tab_screenshot()
