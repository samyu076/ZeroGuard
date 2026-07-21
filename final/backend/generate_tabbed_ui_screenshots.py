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

# 2. Main Dashboard with Vertical Left Navigation Sidebar (Gmail / Canva / Byju's Style)
def generate_dashboard_tab_screenshot():
    img, draw = create_base_canvas(1200, 700)
    
    # Left Navigation Sidebar Drawer
    draw.rectangle([0, 0, 260, 700], fill="#161B22", outline="#21262D", width=1)
    
    # Sidebar Brand
    draw.text((30, 30), "ZERO", fill="#E6EDF3")
    draw.text((76, 30), "GUARD", fill="#FF6200")
    draw.line([30, 60, 230, 60], fill="#21262D", width=1)

    # Vertical Sidebar Tabs list
    tabs = [
        ("Overview", 100, True),
        ("Spatial Risk Map", 150, False),
        ("Incident Replay", 200, False),
        ("Telemetry & Permits", 250, False),
        ("Statutory Compliance", 300, False),
    ]

    for label, ypos, is_active in tabs:
        bg_col = "#FF6200" if is_active else "#161B22"
        text_col = "#FFFFFF" if is_active else "#8B949E"
        draw.rectangle([20, ypos, 240, ypos + 36], fill=bg_col, outline=None)
        draw.text((40, ypos + 12), label, fill=text_col)

    # Sidebar Bottom Profile
    draw.line([30, 600, 230, 600], fill="#21262D", width=1)
    draw.text((30, 620), "Operator: OP-REF-2026", fill="#E6EDF3")
    draw.text((30, 640), "Substation: Zone E", fill="#8B949E")

    # Right Content Area Top Header Bar
    draw.rectangle([260, 0, 1200, 70], fill="#161B22", outline="#21262D", width=1)
    draw.text((290, 26), "CONSOLE MODAL: OVERVIEW", fill="#E6EDF3")

    # Header Controls (Scenario Dropdown & CTA)
    draw.rectangle([800, 18, 980, 48], fill="#0D1117", outline="#21262D")
    draw.text((820, 26), "SCEN-2026-0069", fill="#E6EDF3")
    
    draw.rectangle([1000, 18, 1170, 48], fill="#FF6200", outline="#FF6200")
    draw.text((1025, 26), "Emergency Report", fill="#FFFFFF")

    # Overview Right Content Panel
    draw.rectangle([290, 140, 1170, 670], fill="#161B22", outline="#21262D", width=1)
    draw.text((314, 164), "OVERALL REFINERY PLANT RISK OVERVIEW", fill="#E6EDF3")

    # Risk KPI Indicators
    draw.rectangle([314, 210, 500, 310], fill="#0D1117", outline="#21262D", width=1)
    draw.text((334, 230), "PLANT RISK SCORE", fill="#8B949E")
    draw.text((334, 260), "100.0 (CRITICAL)", fill="#F85149")

    draw.rectangle([520, 210, 710, 310], fill="#0D1117", outline="#21262D", width=1)
    draw.text((540, 230), "SCADA FNR", fill="#8B949E")
    draw.text((540, 260), "50.0% (5/10 Missed)", fill="#F85149")

    draw.rectangle([730, 210, 920, 310], fill="#0D1117", outline="#21262D", width=1)
    draw.text((750, 230), "ZeroGuard FNR", fill="#8B949E")
    draw.text((750, 260), "0.0% (0 Missed)", fill="#2EA043")

    draw.rectangle([940, 210, 1146, 310], fill="#0D1117", outline="#21262D", width=1)
    draw.text((960, 230), "Early Warning Lead Time", fill="#8B949E")
    draw.text((960, 260), "+18.0 min", fill="#58A6FF")

    out_path = os.path.join(artifacts_dir, "overview_tab_dashboard.png")
    img.save(out_path)
    print("Saved:", out_path)

if __name__ == "__main__":
    generate_login_screenshot()
    generate_dashboard_tab_screenshot()
