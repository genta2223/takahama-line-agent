"""Generate standalone static HTML files for Lolipop hosting.
All Jinja2 templates are flattened and links converted to relative ./ paths.
Form submissions are routed directly to the Google Apps Script Webhook.
"""
import os
import re
from pathlib import Path

TEMPLATES_DIR = Path("templates")
DIST_DIR = Path("dist_lolipop")
DIST_DIR.mkdir(parents=True, exist_ok=True)

LIFF_ID = "2006733222-7qNnwwzR" # or fallback
GAS_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbxRH-6fQfevgFSVPwVC-jhs2VG6q6eLf76EAIkAC1_6GQNArTJ4Gzp_IVjJcqrdMtub/exec"

def get_base_html(title, content, scripts=""):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>{title}</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        navy: {{
                            800: '#243b67',
                            900: '#1A2B4C',
                            950: '#101c33'
                        }},
                        emerald: {{
                            500: '#10B981',
                            600: '#059669',
                            700: '#047857'
                        }},
                        amber: {{
                            500: '#F59E0B',
                            600: '#D97706'
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <!-- LINE Front-end Framework (LIFF) SDK -->
    <script charset="utf-8" src="https://static.line-scdn.net/liff/2.1/sdk.js"></script>
    <link rel="stylesheet" href="./css/style.css">
</head>
<body class="bg-slate-50 text-slate-900 antialiased min-h-screen flex flex-col font-sans selection:bg-emerald-500 selection:text-white">
    <!-- Header -->
    <header class="bg-navy-900 text-white shadow-lg sticky top-0 z-40 border-b border-navy-800">
        <div class="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
            <a href="./index.html" class="flex items-center space-x-2.5">
                <div class="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center font-extrabold text-white text-base shadow-sm">
                    源
                </div>
                <div>
                    <div class="flex items-center space-x-1.5">
                        <h1 class="text-sm font-extrabold tracking-tight">阪口 源太</h1>
                        <span class="text-[10px] text-slate-300 font-medium">後援会事務所</span>
                    </div>
                    <p class="text-[11px] text-emerald-400 font-semibold tracking-wide">安心な高浜を、次世代へ。</p>
                </div>
            </a>
            <button onclick="closeLiffOrRedirect()" class="text-xs bg-navy-800 hover:bg-navy-700 text-slate-200 px-3 py-1.5 rounded-full border border-slate-600/50 flex items-center space-x-1 transition-colors">
                <span>✕</span>
                <span>閉じる</span>
            </button>
        </div>
    </header>

    <!-- Main Content Container -->
    <main class="flex-grow max-w-md mx-auto w-full px-4 py-5 space-y-6">
{content}
    </main>

    <!-- Footer with LINE Navigation -->
    <footer class="bg-navy-950 text-slate-400 text-xs py-7 border-t border-navy-900 mt-auto">
        <div class="max-w-md mx-auto px-4 text-center space-y-4">
            <!-- Back to LINE action button -->
            <div>
                <button onclick="closeLiffOrRedirect()" class="w-full bg-navy-900 hover:bg-navy-800 text-white font-bold py-3 px-4 rounded-xl border border-slate-700 flex items-center justify-center space-x-2 shadow-sm transition-all">
                    <span>💬</span>
                    <span>LINEトーク画面に戻る</span>
                </button>
            </div>

            <!-- Supporter & Office Info -->
            <div class="space-y-1 text-slate-400 text-[11px]">
                <p class="font-bold text-slate-300">阪口源太 後援会事務所</p>
                <p>福井県大飯郡高浜町 横津海（青郷地区・阪口商店前）</p>
                <p class="text-[10px] text-slate-500 pt-1">
                    ※本公式Web/LIFFは公職選挙法・政治資金規正法に則った政治活動・政策広報ツールです。
                </p>
            </div>
            <p class="text-[10px] text-slate-600">© 2026-2027 Genta Sakaguchi Supporter Club.</p>
        </div>
    </footer>

    <!-- Universal Close & Fallback Script -->
    <script>
        function closeLiffOrRedirect() {{
            try {{
                if (typeof liff !== 'undefined' && liff.isInClient && liff.isInClient()) {{
                    liff.closeWindow();
                    return;
                }}
            }} catch (e) {{
                console.warn("LIFF close failed:", e);
            }}
            window.location.href = "https://line.me/R/oaMessage/@078lejir";
        }}

        // Initialize LIFF safely
        document.addEventListener('DOMContentLoaded', () => {{
            const liffId = "{LIFF_ID}";
            if (typeof liff !== 'undefined' && liffId && !liffId.includes('xxxx')) {{
                try {{
                    liff.init({{ liffId: liffId }}).catch((err) => {{
                        console.warn('LIFF init warning:', err);
                    }});
                }} catch (e) {{
                    console.warn('LIFF init bypass:', e);
                }}
            }}

            // Dynamic Age Calculation from Birthday: 1976-09-07 (JST)
            try {{
                const birthDate = new Date(1976, 8, 7); // Month is 0-indexed: 8 = September
                const today = new Date();
                let age = today.getFullYear() - birthDate.getFullYear();
                const m = today.getMonth() - birthDate.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {{
                    age--;
                }}
                document.querySelectorAll('.js-genta-age').forEach(el => {{
                    el.textContent = age;
                }});
            }} catch (err) {{
                console.warn('Age calculation fallback:', err);
            }}
        }});
    </script>
{scripts}
</body>
</html>"""

def extract_block(text, block_name):
    pattern = rf"{{% block {block_name} %}}(.*?){{% endblock %}}"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def generate():
    # 1. policies.html
    raw_policies = (TEMPLATES_DIR / "policies.html").read_text(encoding="utf-8")
    content_policies = extract_block(raw_policies, "content")
    scripts_policies = extract_block(raw_policies, "scripts")
    # Wrap script tag if needed
    if scripts_policies and not scripts_policies.startswith("<script>"):
        scripts_policies = f"<script>\n{scripts_policies}\n</script>"
    html_policies = get_base_html("重点政策10選｜討議資料v3ダイジェスト - 阪口源太", content_policies, scripts_policies)
    (DIST_DIR / "policies.html").write_text(html_policies, encoding="utf-8")
    print("Generated policies.html")

    # 2. profile.html
    raw_profile = (TEMPLATES_DIR / "profile.html").read_text(encoding="utf-8")
    content_profile = extract_block(raw_profile, "content")
    content_profile = content_profile.replace("/static/images/profile.png", "./images/profile.png")
    scripts_profile = extract_block(raw_profile, "scripts")
    if scripts_profile and not scripts_profile.startswith("<script>"):
        scripts_profile = f"<script>\n{scripts_profile}\n</script>"
    html_profile = get_base_html("プロフィール・活動理念｜阪口源太 公式情報", content_profile, scripts_profile)
    (DIST_DIR / "profile.html").write_text(html_profile, encoding="utf-8")
    print("Generated profile.html")

    # 3. index.html
    raw_index = (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")
    content_index = extract_block(raw_index, "content")
    # Replace navigation links
    content_index = content_index.replace('href="/policies"', 'href="./policies.html"')
    content_index = content_index.replace('href="/issues"', 'href="./issues.html"')
    content_index = content_index.replace('href="/profile"', 'href="./profile.html"')
    content_index = content_index.replace('href="/supporters"', 'href="./supporters.html"')
    content_index = content_index.replace('/static/images/profile.png', './images/profile.png')
    
    # AI widget fallback in static mode (points user to LINE talk)
    ai_widget_replacement = """    <!-- AI Guidance Widget -->
    <div class="bg-white p-5 rounded-2xl border border-slate-200 card-shadow space-y-3">
        <div class="flex items-center space-x-2">
            <span class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
            <h3 class="font-bold text-sm text-slate-900">AI阪口源太と24時間政策対話</h3>
        </div>
        <p class="text-xs text-slate-600 leading-relaxed">
            「財政や100億円基金についてどう考える？」「青郷の道路はどうなる？」「子育て支援は？」など、LINEトーク画面からいつでも直接質問・対話できます。
        </p>
        <div>
            <a href="https://line.me/R/oaMessage/@078lejir/?政策について教えて！" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs py-3 px-4 rounded-xl flex items-center justify-center space-x-2 shadow-sm transition-colors">
                <span>💬</span>
                <span>LINEでAI源太に質問する</span>
            </a>
        </div>
    </div>"""
    content_index = re.sub(r'<!-- AI Interactive Widget -->.*?</div>\s*</div>\s*</div>', ai_widget_replacement, content_index, flags=re.DOTALL)

    html_index = get_base_html("阪口源太 公式ポータル｜福井県高浜町", content_index, "")
    (DIST_DIR / "index.html").write_text(html_index, encoding="utf-8")
    print("Generated index.html")

    # 4. issues.html
    raw_issues = (TEMPLATES_DIR / "issues.html").read_text(encoding="utf-8")
    content_issues = extract_block(raw_issues, "content")
    
    scripts_issues = f"""<script>
    const GAS_WEBHOOK_URL = "{GAS_WEBHOOK_URL}";

    function previewImage(input) {{
        if (input.files && input.files[0]) {{
            const reader = new FileReader();
            reader.onload = function (e) {{
                document.getElementById('preview-img').src = e.target.result;
                document.getElementById('file-name').innerText = '添付中: ' + input.files[0].name;
                document.getElementById('image-preview').classList.remove('hidden');
            }}
            reader.readAsDataURL(input.files[0]);
        }}
    }}

    const form = document.getElementById('issue-form');
    const alertBox = document.getElementById('status-alert');
    const submitBtn = document.getElementById('submit-btn');
    const successModal = document.getElementById('success-modal');

    form.addEventListener('submit', async (e) => {{
        e.preventDefault();
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>送信中（画像暗号化中）...</span>';

        const district = form.querySelector('[name="district"]').value;
        const categoryElem = form.querySelector('[name="category"]:checked');
        const category = categoryElem ? categoryElem.value : "未選択";
        const location = form.querySelector('[name="location"]').value || "未指定";
        const description = form.querySelector('[name="description"]').value;
        const reporterName = form.querySelector('[name="reporter_name"]').value || "匿名町民";

        const photoInput = document.getElementById('photo-input');
        let file = null;
        let pureBase64 = "";

        if (photoInput.files && photoInput.files[0]) {{
            file = photoInput.files[0];
            try {{
                pureBase64 = await new Promise((resolve, reject) => {{
                    const reader = new FileReader();
                    reader.onload = () => {{
                        const res = reader.result;
                        const base64Index = res.indexOf(';base64,');
                        if (base64Index !== -1) {{
                            resolve(res.substring(base64Index + 8));
                        }} else {{
                            resolve(res);
                        }}
                    }};
                    reader.onerror = error => reject(error);
                    reader.readAsDataURL(file);
                }});
            }} catch (err) {{
                console.error("Base64 conversion failed:", err);
            }}
        }}

        const payload = {{
            type: "issue",
            district: district,
            category: category,
            details: "【場所・目印】" + location + "\\n【詳細】" + description,
            image_name: file ? file.name : "",
            image_mime: file ? file.type : "",
            image_base64: pureBase64,
            contact: reporterName,
            timestamp: new Date().toISOString()
        }};

        try {{
            await fetch(GAS_WEBHOOK_URL, {{
                method: "POST",
                mode: "no-cors",
                headers: {{ "Content-Type": "text/plain" }},
                body: JSON.stringify(payload)
            }});

            // In no-cors mode, completion means request dispatched successfully
            form.reset();
            document.getElementById('image-preview').classList.add('hidden');
            successModal.classList.remove('hidden');
        }} catch (err) {{
            alertBox.className = 'block p-3.5 rounded-xl text-xs font-bold bg-red-100 text-red-800 border border-red-300';
            alertBox.innerText = 'エラーが発生しました：' + err.message;
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }} finally {{
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>現場の声を送信する</span><span class="text-base">📨</span>';
        }}
    }});

    function dismissModal() {{
        successModal.classList.add('hidden');
    }}
</script>"""

    html_issues = get_base_html("まちの困りごと・現場通報｜阪口源太 公式情報", content_issues, scripts_issues)
    (DIST_DIR / "issues.html").write_text(html_issues, encoding="utf-8")
    print("Generated issues.html")

    # 5. supporters.html
    raw_supporters = (TEMPLATES_DIR / "supporters.html").read_text(encoding="utf-8")
    content_supporters = extract_block(raw_supporters, "content")

    scripts_supporters = f"""<script>
    const GAS_WEBHOOK_URL = "{GAS_WEBHOOK_URL}";

    const form = document.getElementById('supporter-form');
    const alertBox = document.getElementById('status-alert');
    const submitBtn = document.getElementById('submit-btn');
    const successModal = document.getElementById('success-modal');

    form.addEventListener('submit', async (e) => {{
        e.preventDefault();
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>送信中...</span>';

        const supports = [];
        form.querySelectorAll('input[name="support_type"]:checked').forEach(cb => supports.push(cb.value));

        if (supports.length === 0) {{
            alert('応援メニューを1つ以上選択してください。');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>後援会サポーターに登録する</span><span class="text-base">✨</span>';
            return;
        }}

        const payload = {{
            type: "supporter",
            name: form.querySelector('[name="name"]').value,
            contact: form.querySelector('[name="contact"]').value,
            address: form.querySelector('[name="address"]').value || '',
            menus: supports,
            message: form.querySelector('[name="message"]').value || '',
            timestamp: new Date().toISOString()
        }};

        try {{
            await fetch(GAS_WEBHOOK_URL, {{
                method: "POST",
                mode: "no-cors",
                headers: {{ "Content-Type": "text/plain" }},
                body: JSON.stringify(payload)
            }});

            form.reset();
            successModal.classList.remove('hidden');
        }} catch (err) {{
            alertBox.className = 'block p-3.5 rounded-xl text-xs font-bold bg-red-100 text-red-800 border border-red-300';
            alertBox.innerText = 'エラーが発生しました：' + err.message;
            window.scrollTo({{top: 0, behavior: 'smooth'}});
        }} finally {{
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>後援会サポーターに登録する</span><span class="text-base">✨</span>';
        }}
    }});

    function dismissModal() {{
        successModal.classList.add('hidden');
    }}
</script>"""

    html_supporters = get_base_html("阪口源太 後援会サポーター登録・仲間入り", content_supporters, scripts_supporters)
    (DIST_DIR / "supporters.html").write_text(html_supporters, encoding="utf-8")
    print("Generated supporters.html")

if __name__ == "__main__":
    generate()

