import re

def update_dashboard():
    with open("dashboard/index.html", "r", encoding="utf-8") as f:
        content = f.read()

    replacements = [
        ("#39B54A", "#0A6CBE"),
        ("#2B9138", "#00549E"),
        ("#EAF7EC", "#EAF3FA"),
        ("#BBF7D0", "#A9D3EF"),
        ("bg-green-50", "bg-[#EAF3FA]"),
        ("bg-green-100", "bg-[#EAF3FA]"),
        ("bg-green-950/40", "bg-blue-950/40"),
        ("bg-green-950/30", "bg-blue-950/30"),
        ("text-green-800", "text-[#00549E]"),
        ("text-green-700", "text-[#0A6CBE]"),
        ("text-green-600", "text-[#0A6CBE]"),
        ("text-green-400", "text-[#3893D2]"),
        ("text-green-300", "text-[#A9D3EF]"),
        ("border-green-200", "border-[#A9D3EF]"),
        ("border-green-800", "border-blue-800"),
        ("border-green-300", "border-[#A9D3EF]"),
        ('worstStatus.color === "green"', 'worstStatus.color === "blue" || worstStatus.color === "green"'),
        ('worstStatus.color === \'green\'', 'worstStatus.color === "blue" || worstStatus.color === "green"'),
        ('color: "green"', 'color: "blue"'),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    with open("dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("dashboard/index.html updated.")

if __name__ == "__main__":
    update_dashboard()
