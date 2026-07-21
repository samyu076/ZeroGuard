import os
from PIL import Image, ImageDraw, ImageFont

artifacts_dir = r"C:\Users\samyu\.gemini\antigravity\brain\468ceaff-da74-4b38-aa4c-6b42e95954c1"

def create_base_canvas(width=1200, height=750):
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

# 2. Main Dashboard with Left Sidebar Navigation Drawer (Gmail / Outlook / Canva Style) & Comic Sans Font
def generate_dashboard_tab_screenshot():
    img, draw = create_base_canvas(1200, 750)
    
    # LEFT SIDEBAR DRAWER (Width: 260px)
    draw.rectangle([0, 0, 260, 750], fill="#161B22", outline="#21262D", width=1)

    # Brand Title in Left Sidebar
    draw.text((24, 24), "ZERO", fill="#E6EDF3")
    draw.text((70, 24), "GUARD", fill="#FF6200")
    draw.line([24, 60, 236, 60], fill="#21262D", width=1)

    # Vertical Page Navigation List (Comic Sans styling)
    draw.text((24, 80), "CONSOLE NAVIGATION", fill="#8B949E")

    sidebar_items = [
        ("Overview", 110, True),
        ("Spatial Risk Map", 160, False),
        ("Incident Replay", 210, False),
        ("Telemetry & Permits", 260, False),
        ("Statutory Compliance", 310, False),
    ]

    for label, ypos, is_active in sidebar_items:
        if is_active:
            draw.rectangle([20, ypos, 240, ypos + 38], fill="#FF6200", outline=None)
            draw.text((40, ypos + 10), label, fill="#FFFFFF")
        else:
            draw.text((40, ypos + 10), label, fill="#8B949E")

    # Left Sidebar Bottom Profile
    draw.line([20, 660, 240, 660], fill="#21262D", width=1)
    draw.text((30, 680), "OP-REF-2026", fill="#E6EDF3")
    draw.text((30, 700), "Zone E Control Substation", fill="#8B949E")

    # RIGHT MAIN CONTENT AREA
    # Top Action Bar
    draw.rectangle([260, 0, 1200, 60], fill="#161B22", outline="#21262D", width=1)
    draw.text((284, 20), "CONSOLE MODAL: OVERVIEW", fill="#FF6200")

    # Dropdown & Buttons
    draw.rectangle([680, 14, 880, 46], fill="#0D1117", outline="#21262D")
    draw.text((690, 24), "SCEN-2026-0069 [COMPOUND]", fill="#E6EDF3")

    draw.rectangle([900, 14, 1040, 46], fill="#FF6200", outline="#FF6200")
    draw.text((910, 24), "Emergency Report", fill="#FFFFFF")

    # Main Overview Content Card
    draw.rectangle([284, 120, 1170, 710], fill="#161B22", outline="#21262D", width=1)
    draw.text((310, 144), "OVERALL REFINERY PLANT RISK OVERVIEW", fill="#E6EDF3")
    
    # Risk Indicators
    draw.rectangle([310, 190, 500, 280], fill="#0D1117", outline="#21262D", width=1)
    draw.text((330, 210), "PLANT RISK SCORE", fill="#8B949E")
    draw.text((330, 240), "100.0 (CRITICAL)", fill="#F85149")

    draw.rectangle([520, 190, 710, 280], fill="#0D1117", outline="#21262D", width=1)
    draw.text((540, 210), "SCADA FNR", fill="#8B949E")
    draw.text((540, 240), "50.0% (5/10 Missed)", fill="#F85149")

    draw.rectangle([730, 190, 920, 280], fill="#0D1117", outline="#21262D", width=1)
    draw.text((750, 210), "ZeroGuard FNR", fill="#8B949E")
    draw.text((750, 240), "0.0% (0 Missed)", fill="#2EA043")

    draw.rectangle([940, 190, 1140, 280], fill="#0D1117", outline="#21262D", width=1)
    draw.text((955, 210), "Lead Time", fill="#8B949E")
    draw.text((955, 240), "+18.0 min", fill="#58A6FF")

    out_path = os.path.join(artifacts_dir, "overview_tab_dashboard.png")
    img.save(out_path)
    print("Saved:", out_path)

if __name__ == "__main__":
    generate_login_screenshot()
    generate_dashboard_tab_screenshot()
