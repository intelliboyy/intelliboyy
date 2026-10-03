#!/usr/bin/env python3
"""Generates the animated SVG assets used by README.md.
Run:  python3 generate_assets.py [output_dir]   (default: ../assets)
Edit the DATA sections to change text; colours live in the PALETTE block."""
import os, sys, textwrap
from xml.sax.saxutils import escape as esc

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

# ----------------------------- PALETTE -----------------------------
BG0, PANEL, BORDER = "#020617", "#08131f", "#12324a"
TEAL, CYAN, VIOLET, AMBER, PINK, GREEN = "#00f5d4", "#22d3ee", "#a78bfa", "#fbbf24", "#f472b6", "#4ade80"
TXT, DIM = "#e2e8f0", "#7f93a8"
FONT = "'JetBrains Mono','Fira Code','SFMono-Regular',Menlo,Consolas,'DejaVu Sans Mono',monospace"
CW = 0.62  # approx glyph width / font-size for the monospace stack

COMMON_DEFS = f"""
<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glow2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="#0f2a3a" stroke-width="1" opacity="0.55"/></pattern>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#020617"/><stop offset="1" stop-color="#062029"/></linearGradient>
<linearGradient id="acc" x1="0" x2="1"><stop offset="0" stop-color="{TEAL}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
"""

def svg(w, h, body, defs=""):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{FONT}">\n'
            f'<defs>{COMMON_DEFS}{defs}</defs>\n{body}\n</svg>\n')

def save(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)

def tw(text, size):  # estimated text width
    return len(text) * size * CW

def panel(w, h, r=12, grid=True, cid="pc"):
    s = (f'<clipPath id="{cid}"><rect width="{w}" height="{h}" rx="{r}"/></clipPath>'
         f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" fill="url(#bg)" stroke="{BORDER}"/>')
    if grid:
        s += f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r}" fill="url(#grid)" opacity=".6"/>'
    return s

def titlebar(w, title):
    return (f'<rect x="1" y="1" width="{w-2}" height="32" rx="11" fill="#0a1b2b"/><rect x="1" y="22" width="{w-2}" height="12" fill="#0a1b2b"/>'
            f'<circle cx="22" cy="17" r="5" fill="#ff5f57"/><circle cx="40" cy="17" r="5" fill="#febc2e"/><circle cx="58" cy="17" r="5" fill="#28c840"/>'
            f'<text x="{w/2}" y="21" text-anchor="middle" font-size="12" fill="{DIM}">{esc(title)}</text>'
            f'<line x1="1" y1="33.5" x2="{w-1}" y2="33.5" stroke="{BORDER}"/>')

def sweep_def(color, sid="sw"):
    return (f'<linearGradient id="{sid}" x1="0" x2="1"><stop offset="0" stop-color="{color}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{color}" stop-opacity=".10"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>')

def sweep(h, color, dur=7, cid="pc", sid="sw", span=1060):
    return (f'<g clip-path="url(#{cid})"><rect x="-80" y="0" width="80" height="{h}" fill="url(#{sid})">'
            f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{span} 0" dur="{dur}s" repeatCount="indefinite"/></rect></g>')

def reveal(cid, x, y, w, h, t0, t1, T):
    kt = f"0;{t0/T:.4f};{t1/T:.4f};0.95;0.9501;1"
    vals = f"0;0;{w};{w};0;0"
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="0" height="{h}">'
            f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="{T}s" repeatCount="indefinite"/></rect></clipPath>')

def fade(t0, t1, T):
    return (f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{t0/T:.4f};{t1/T:.4f};0.95;0.9501;1" '
            f'dur="{T}s" repeatCount="indefinite"/>')

def chips(items, x, y, maxx, color, size=11, h=22, gap=8, pad=9):
    out, cx, cy = "", x, y
    for it in items:
        w = tw(it, size) + pad * 2
        if cx + w > maxx:
            cx, cy = x, cy + h + gap
        out += (f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="{h}" rx="5" fill="{color}" fill-opacity=".08" stroke="{color}" stroke-opacity=".4"/>'
                f'<text x="{cx+pad:.1f}" y="{cy+h/2+size*0.36:.1f}" font-size="{size}" fill="{TXT}">{esc(it)}</text>')
        cx += w + gap
    return out, cy + h

import textwrap

import math

def tri(x, y, d, c):
    pts = {"r": [(x, y), (x-6, y-3.5), (x-6, y+3.5)], "l": [(x, y), (x+6, y-3.5), (x+6, y+3.5)],
           "d": [(x, y), (x-3.5, y-6), (x+3.5, y-6)], "u": [(x, y), (x-3.5, y+6), (x+3.5, y+6)]}[d]
    return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a,b in pts)}" fill="{c}" fill-opacity=".85"/>'

def node(x, y, w, h, text, c, size=10, bold=False):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="6" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".6"/>'
            f'<text x="{x+w/2:.1f}" y="{y+h/2+size*0.36:.1f}" text-anchor="middle" font-size="{size}" fill="{TXT}"{" font-weight=\"700\"" if bold else ""}>{esc(text)}</text>')

def flow(nodes, x0, y, width, c, size=9.5, h=28, box=None, back=None):
    ws = [tw(n, size) + 14 for n in nodes]
    gap = (width - sum(ws)) / (len(nodes) - 1)
    xs, x = [], x0
    for w in ws:
        xs.append(x); x += w + gap
    cy = y + h / 2
    out = ""
    if box:
        i0, i1, label = box
        bx, bw = xs[i0] - 8, xs[i1] + ws[i1] - xs[i0] + 16
        out += (f'<rect x="{bx:.1f}" y="{y-18}" width="{bw:.1f}" height="{h+26}" rx="8" fill="none" stroke="{c}" stroke-opacity=".35" stroke-dasharray="4 4"/>'
                f'<text x="{bx+8:.1f}" y="{y-6}" font-size="8.5" fill="{c}" fill-opacity=".9" letter-spacing=".6">{esc(label)}</text>')
    for i, (n, w) in enumerate(zip(nodes, ws)):
        out += node(xs[i], y, w, h, n, c, size)
        if i < len(nodes) - 1:
            x1, x2 = xs[i] + w, xs[i+1]
            out += f'<line x1="{x1:.1f}" y1="{cy}" x2="{x2-5:.1f}" y2="{cy}" stroke="{c}" stroke-opacity=".7"/>' + tri(x2, cy, "r", c)
    out += (f'<circle r="2.6" fill="{c}" filter="url(#glow2)"><animateMotion dur="{len(nodes)*0.9:.1f}s" repeatCount="indefinite" '
            f'path="M{xs[0]:.1f} {cy} L{xs[-1]+ws[-1]:.1f} {cy}"/></circle>')
    if back:
        a, b, label = back
        ax, bx_ = xs[a] + ws[a] / 2, xs[b] + ws[b] / 2
        out += (f'<path d="M{ax:.1f} {y+h} Q{(ax+bx_)/2:.1f} {y+h+34} {bx_:.1f} {y+h+2}" fill="none" stroke="{c}" stroke-opacity=".6" stroke-dasharray="3 3"/>'
                + tri(bx_, y + h + 1, "u", c) +
                f'<text x="{(ax+bx_)/2:.1f}" y="{y+h+24}" text-anchor="middle" font-size="8.5" fill="{DIM}">{esc(label)}</text>')
    return out

def pill(x_right, y, text, c, size=9.5, h=20, ls=.8):
    w = len(text) * (size * 0.62 + ls * 0.9) + 26
    return (f'<rect x="{x_right-w:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".5"/>'
            f'<circle cx="{x_right-w+11:.1f}" cy="{y+h/2}" r="3" fill="{c}"><animate attributeName="opacity" values="1;.2;1" dur="1.8s" repeatCount="indefinite"/></circle>'
            f'<text x="{x_right-w+20:.1f}" y="{y+h/2+size*0.36:.1f}" font-size="{size}" fill="{c}" letter-spacing="{ls}">{esc(text)}</text>'), w

def plate(x, y, w, h, c=None, r=10, cid=None):
    s = (f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{r}" fill="url(#bg)" stroke="{BORDER}"/>'
         f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="{h-2}" rx="{r}" fill="url(#grid)" opacity=".6"/>')
    if c:
        s += f'<rect x="{x+14}" y="{y}" width="{w-28}" height="3" rx="1.5" fill="{c}" filter="url(#glow2)"/>'
    return s

# ============================== HERO ==============================
def hero():
    W, H, T = 900, 304, 18.0
    defs = (reveal("c1", 36, 52, 330, 28, 0.3, 1.6, T) + reveal("c2", 36, 134, 720, 28, 2.4, 4.4, T) +
            reveal("c3", 36, 168, 330, 24, 4.8, 5.8, T) + reveal("c4", 36, 194, 720, 24, 6.2, 9.0, T) +
            reveal("c5", 36, 228, 330, 24, 9.4, 10.4, T) + reveal("c6", 36, 254, 720, 24, 10.8, 13.0, T) +
            '<radialGradient id="rs" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(0 0) scale(62)"><stop offset="0" stop-color="#00f5d4" stop-opacity=".55"/><stop offset="1" stop-color="#00f5d4" stop-opacity="0"/></radialGradient>'
            + sweep_def(TEAL))
    prompt = lambda cmd: (f'<tspan fill="{GREEN}">anshuman@psit</tspan><tspan fill="{DIM}">:~$ </tspan><tspan fill="{TXT}">{cmd}</tspan>')
    b = panel(W, H) + titlebar(W, "anshuman@psit-vyomnauts: ~/portfolio  —  bash") + sweep(H, TEAL, 9, sid="sw")
    b += f'<text x="36" y="72" font-size="14" clip-path="url(#c1)">{prompt("whoami")}</text>'
    b += f'<text x="36" y="116" font-size="40" font-weight="700" letter-spacing="3" fill="{TEAL}" filter="url(#glow)">ANSHUMAN PATHAK{fade(1.6, 2.4, T)}</text>'
    b += f'<text x="36" y="148" font-size="16" fill="{CYAN}" clip-path="url(#c2)">Research Engineer · Retrieval, Reasoning &amp; Self-Hosted LLMs</text>'
    b += f'<text x="36" y="184" font-size="14" clip-path="url(#c3)">{prompt("cat focus.txt")}</text>'
    b += f'<text x="36" y="210" font-size="13" fill="{TXT}" clip-path="url(#c4)">on-device multimodal AI · uncertainty-aware models · TensorRT INT8 · agentic systems</text>'
    b += f'<text x="36" y="244" font-size="14" clip-path="url(#c5)">{prompt("status --now")}</text>'
    b += f'<text x="36" y="270" font-size="13" fill="{TXT}" clip-path="url(#c6)"><tspan fill="{GREEN}">●</tspan> open to internships from 2027-01 · relocation: yes</text>'
    cx = 36 + tw("● open to internships from 2027-01 · relocation: yes", 13) + 6
    b += (f'<g opacity="0">{fade(13.0, 13.1, T)}<rect x="{cx:.1f}" y="258" width="8" height="15" fill="{TEAL}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect></g>')
    b += '<g transform="translate(800 176)">'
    for r in (20, 40, 60):
        b += f'<circle r="{r}" fill="none" stroke="{TEAL}" stroke-opacity=".28"/>'
    b += (f'<line x1="-66" y1="0" x2="66" y2="0" stroke="{TEAL}" stroke-opacity=".25"/><line x1="0" y1="-66" x2="0" y2="66" stroke="{TEAL}" stroke-opacity=".25"/>'
          f'<g><path d="M0 0 L62 0 A62 62 0 0 0 53.7 -31 Z" fill="url(#rs)"/><line x1="0" y1="0" x2="62" y2="0" stroke="{TEAL}" stroke-width="1.5" filter="url(#glow2)"/>'
          f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" repeatCount="indefinite"/></g>')
    for (bx, by, d) in ((24, -30, 0.2), (-34, 18, 1.3), (10, 42, 2.4), (-12, -44, 3.1)):
        b += f'<circle cx="{bx}" cy="{by}" r="3" fill="{AMBER}" filter="url(#glow2)"><animate attributeName="opacity" values="0;1;0" dur="4s" begin="{d}s" repeatCount="indefinite"/></circle>'
    b += '</g>'
    b += (f'<circle cx="742" cy="262" r="3.5" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>'
          f'<text x="752" y="266" font-size="10" fill="{DIM}" letter-spacing="1">TELEMETRY · LIVE</text>')
    save("hero.svg", svg(W, H, b, defs))

# ============================== NAV TABS ==============================
def nav():
    tabs = [("01", "SNAPSHOT", TEAL), ("02", "EXPERTISE", CYAN), ("03", "WORK", VIOLET), ("04", "RECORD", AMBER), ("05", "LIVE", PINK)]
    for i, (n, label, c) in enumerate(tabs, 1):
        W, H = 176, 46
        b = (f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="url(#bg)" stroke="{BORDER}"/>'
             f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="8" fill="url(#grid)" opacity=".6"/>'
             f'<text x="16" y="28" font-size="11" fill="{DIM}">{n}</text>'
             f'<text x="40" y="28" font-size="13" font-weight="700" fill="{TXT}" letter-spacing="1">{label}</text>'
             f'<rect x="12" y="38" width="{W-24}" height="2" rx="1" fill="{c}" fill-opacity=".25"/>'
             f'<rect x="12" y="38" width="30" height="2" rx="1" fill="{c}" filter="url(#glow2)"><animate attributeName="x" values="12;{W-42};12" dur="{3+i*.4:.1f}s" repeatCount="indefinite"/></rect>'
             f'<circle cx="{W-16}" cy="16" r="3" fill="{c}"><animate attributeName="opacity" values="1;.2;1" dur="{1.5+i*.3:.1f}s" repeatCount="indefinite"/></circle>')
        save(f"nav-{i}.svg", svg(W, H, b))

# ============================== CLUSTER HEADERS ==============================
def cluster_header(slug, num, title, sub, c):
    W, H = 900, 76
    defs = f'<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{c}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>' + sweep_def(c)
    b = plate(0, 0, W, H) + sweep(H, c, 8, cid="hc")
    b = f'<clipPath id="hc"><rect width="{W}" height="{H}" rx="10"/></clipPath>' + b
    b += (f'<rect x="0" y="14" width="4" height="{H-28}" rx="2" fill="{c}" filter="url(#glow2)"/>'
          f'<text x="26" y="52" font-size="36" font-weight="700" fill="none" stroke="{c}" stroke-width="1.2" filter="url(#glow2)">{num}</text>'
          f'<text x="92" y="40" font-size="21" font-weight="700" fill="{TXT}" letter-spacing="1.5">{esc(title)}</text>'
          f'<text x="92" y="60" font-size="11.5" fill="{DIM}">{esc(sub)}</text>')
    for k in range(6):
        bx = 808 + k * 12
        b += (f'<rect x="{bx}" y="22" width="6" height="32" rx="2" fill="{c}" fill-opacity=".85"><animate attributeName="y" values="{40-k*2};{16+k*2};{40-k*2}" dur="{1.2+k*.17:.2f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="height" values="{14+k*2};{40-k*2};{14+k*2}" dur="{1.2+k*.17:.2f}s" repeatCount="indefinite"/></rect>')
    save(f"c-{slug}.svg", svg(W, H, b, defs))

# ============================== SNAPSHOT ==============================
def snapshot():
    W, H = 900, 400
    LW, RX, RW = 456, 472, 428
    defs = "".join(sweep_def(c, f"s{i}") for i, c in enumerate((TEAL, CYAN, VIOLET, AMBER, PINK, GREEN)))
    b = ""
    # profile
    b += plate(0, 0, LW, 252, TEAL)
    b += f'<text x="24" y="34" font-size="11" fill="{DIM}" letter-spacing="1.5">▸ PROFILE.YML</text>'
    rows = [("role", "Research Engineer candidate · AI/ML & systems"), ("education", "B.Tech CSE (AI) · PSIT Kanpur · 2027"),
            ("focus", "Retrieval · Reasoning · Self-hosted LLMs"), ("edge", "Jetson Nano · TensorRT INT8 · <200 ms"),
            ("stack", "PyTorch · FastAPI · React · PostgreSQL"), ("leads", "GCS software · PSIT VYOMNAUTS"),
            ("location", "Kanpur, India · open to relocation"), ("available", "internships from January 2027")]
    y = 62
    for k, v in rows:
        b += (f'<text x="24" y="{y}" font-size="12" font-weight="700" fill="{TEAL}">{k}</text><text x="104" y="{y}" font-size="12" fill="{DIM}">:</text>'
              f'<text x="118" y="{y}" font-size="12" fill="{TXT}">{esc(v)}</text>')
        y += 23
    # metrics
    metrics = [("<200ms", "INT8 INFERENCE · JETSON NANO", TEAL), ("<2s", "ON-DEVICE VOICE AGENT", CYAN), ("90%", "ViT-B/16 VALIDATION ACC.", VIOLET),
               ("2 + TPC", "PAPERS · IEEE · IJECS", AMBER), ("1,000+", "STUDENTS TAUGHT", PINK), ("AIR-1", "TEKNOFEST · + BEST DATA AWARD", GREEN)]
    tw_, th_, gx, gy = 204, 78, 20, 9
    for i, (num, lab, c) in enumerate(metrics):
        x = RX + (i % 2) * (tw_ + gx); y = (i // 2) * (th_ + gy)
        b += (f'<clipPath id="m{i}"><rect x="{x}" y="{y}" width="{tw_}" height="{th_}" rx="10"/></clipPath>' + plate(x, y, tw_, th_, c) +
              f'<text x="{x+18}" y="{y+44}" font-size="{26 if len(num)<8 else 22}" font-weight="700" fill="{c}" filter="url(#glow2)">{esc(num)}</text>'
              f'<text x="{x+18}" y="{y+64}" font-size="9" fill="{DIM}" letter-spacing=".8">{esc(lab)}</text>'
              f'<circle cx="{x+tw_-14}" cy="{y+16}" r="3" fill="{c}"><animate attributeName="opacity" values="1;.2;1" dur="{1.6+i*.25:.2f}s" repeatCount="indefinite"/></circle>'
              f'<g clip-path="url(#m{i})"><rect x="{x-60}" y="{y}" width="60" height="{th_}" fill="url(#s{i})"><animateTransform attributeName="transform" type="translate" from="0 0" to="{tw_+60} 0" dur="{5+i*.7:.1f}s" repeatCount="indefinite"/></rect></g>')
    # open-to roles
    y0 = 268
    b += plate(0, y0, W, 132)
    b += (f'<text x="24" y="{y0+28}" font-size="11" fill="{DIM}" letter-spacing="1.5">▸ OPEN TO · INTERNSHIPS FROM JAN 2027 · RELOCATION OK</text>'
          f'<circle cx="{W-28}" cy="{y0+24}" r="4" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="1.4s" repeatCount="indefinite"/></circle>')
    roles = [("ML / CV ENGINEER", TEAL, "edge inference · quantization · evals", "proof: DR screening · VAMAN"),
             ("GENAI & AGENTIC SYSTEMS", VIOLET, "RAG · LangGraph · MCP · fine-tuning", "proof: FinTech agents · Oracle cert"),
             ("BACKEND / FULL-STACK", AMBER, "FastAPI · PostgreSQL · React · Electron", "proof: GCS used in competitions")]
    cw = 276
    for i, (t, c, kw, pf) in enumerate(roles):
        x = 16 + i * (cw + 10)
        b += (f'<rect x="{x}" y="{y0+44}" width="{cw}" height="74" rx="8" fill="{c}" fill-opacity=".07" stroke="{c}" stroke-opacity=".4"/>'
              f'<rect x="{x}" y="{y0+44}" width="3" height="74" rx="1.5" fill="{c}"/>'
              f'<text x="{x+16}" y="{y0+66}" font-size="12" font-weight="700" fill="{c}" letter-spacing=".8">{esc(t)}</text>'
              f'<text x="{x+16}" y="{y0+88}" font-size="10.5" fill="{TXT}">{esc(kw)}</text>'
              f'<text x="{x+16}" y="{y0+106}" font-size="10" fill="{DIM}">{esc(pf)}</text>')
    save("snapshot.svg", svg(W, H, b, defs))

# ============================== EXPERTISE → EVIDENCE ==============================
EXPERTISE = [
    ("Retrieval & Agents", TEAL, ["RAG (vector & vectorless)", "ChromaDB", "LangChain", "LangGraph", "LangSmith", "MCP", "Agentic memory", "Claude Code", "OpenClaw", "Hermes"],
     ["Multi-agent FinTech pipeline", "Oracle Agentic AI cert", "AI Eng track: RAG, agents"]),
    ("LLM / VLM", CYAN, ["PyTorch", "HF Transformers", "SFT", "PEFT / LoRA", "vLLM", "Whisper", "Prompt engineering"],
     ["Raman LLM benchmarks", "VARUNA ViT-B/16 · 90%", "VAMAN LLM pipeline"]),
    ("Computer Vision", VIOLET, ["OpenCV", "Vision Transformers", "CNN-Transformer hybrids", "Diffusion models", "GANs"],
     ["DR lesion grading", "VARUNA fisheries ViT"]),
    ("Efficient & Edge AI", AMBER, ["TensorRT INT8", "PTQ (bitsandbytes, HF AutoTrain)", "CUDA", "Jetson Nano / JetPack", "On-device profiling"],
     ["<200 ms INT8 on Jetson", "<2 s on-device voice agent"]),
    ("Uncertainty & Evals", PINK, ["Monte Carlo Dropout", "Custom eval harnesses", "Benchmarking"],
     ["Specialist routing in DR", "Raman eval scripts"]),
    ("Backend & Systems", GREEN, ["FastAPI", "Flask", "PostgreSQL", "WebSocket", "REST", "Electron", "React / Vite", "Docker", "Linux", "Bash", "Git", "AWS", "CI/CD"],
     ["GCS in production use", "Multiple competition cycles"]),
    ("Languages & Data", TEAL, ["Python", "Java", "SQL", "Bash", "NumPy", "Pandas", "scikit-learn"],
     ["Python in every project", "Java + SQL fundamentals"]),
]

def expertise():
    W = 900
    TX0, TMAX, PX0, PMAX = 196, 596, 640, 876
    defs = sweep_def(CYAN)
    rows, y = [], 70
    for (dom, c, tools, proof) in EXPERTISE:
        tch, tb = chips(tools, TX0, y + 8, TMAX, c, size=10.5, h=21, gap=7, pad=8)
        pch, pb = chips(["✓ " + p for p in proof], PX0, y + 8, PMAX, c, size=10, h=21, gap=7, pad=8)
        bottom = max(tb, pb)
        rows.append((dom, c, tch, pch, y, bottom))
        y = bottom + 16
    H = y + 4
    b = panel(W, H, cid="pc") + titlebar(W, "expertise.map — domain → tools → evidence") + sweep(H, CYAN, 12)
    b += (f'<text x="28" y="58" font-size="9.5" fill="{DIM}" letter-spacing="1.5">DOMAIN</text><text x="{TX0}" y="58" font-size="9.5" fill="{DIM}" letter-spacing="1.5">TOOLS &amp; METHODS</text>'
          f'<text x="{PX0}" y="58" font-size="9.5" fill="{DIM}" letter-spacing="1.5">PROVEN BY</text>')
    for (dom, c, tch, pch, ry, bottom) in rows:
        mid = (ry + 8 + bottom) / 2
        b += (f'<rect x="24" y="{ry+4}" width="3" height="{bottom-ry-4}" rx="1.5" fill="{c}"/>'
              f'<text x="38" y="{ry+24}" font-size="12.5" font-weight="700" fill="{c}">{esc(dom)}</text>' + tch +
              f'<line x1="{TMAX+10}" y1="{mid:.1f}" x2="{PX0-14}" y2="{mid:.1f}" stroke="{c}" stroke-opacity=".5" stroke-dasharray="4 4"><animate attributeName="stroke-dashoffset" from="16" to="0" dur="1.6s" repeatCount="indefinite"/></line>'
              + tri(PX0 - 8, mid, "r", c) + pch +
              f'<line x1="24" y1="{bottom+8}" x2="{W-24}" y2="{bottom+8}" stroke="{BORDER}" stroke-dasharray="3 5"/>')
    save("expertise.svg", svg(W, H, b, defs))

def principles():
    W, H = 900, 104
    cards = [("bars", "MEASURE FIRST", TEAL, ["eval harnesses before", "any performance", "claim is made"]),
             ("chip", "RUN ON-DEVICE", CYAN, ["INT8 on a Jetson,", "zero external", "API dependency"]),
             ("target", "KNOW WHEN UNSURE", VIOLET, ["MC Dropout routes", "doubtful cases to a", "specialist"]),
             ("stack", "SHIP THE SYSTEM", AMBER, ["UI + API + DB used", "by real competition", "teams"])]
    cw, gap = 207, 24
    defs, b = "", ""
    for i, (g, t, c, lines) in enumerate(cards):
        x = i * (cw + gap)
        defs += sweep_def(c, f"s{i}")
        b += (f'<clipPath id="k{i}"><rect x="{x}" width="{cw}" height="{H}" rx="10"/></clipPath>' + plate(x, 0, cw, H) +
              f'<rect x="{x}" y="14" width="3" height="{H-28}" fill="{c}"/>' + glyph(g, x + 16, 16, c).replace("<rect", "<rect") +
              f'<text x="{x+58}" y="34" font-size="11.5" font-weight="700" fill="{c}" letter-spacing=".8">{esc(t)}</text>')
        for j, ln in enumerate(lines):
            b += f'<text x="{x+58}" y="{54+j*14}" font-size="10.5" fill="{TXT}" fill-opacity=".85">{esc(ln)}</text>'
        b += f'<g clip-path="url(#k{i})"><rect x="{x-60}" width="60" height="{H}" fill="url(#s{i})"><animateTransform attributeName="transform" type="translate" from="0 0" to="{cw+60} 0" dur="{6+i}s" repeatCount="indefinite"/></rect></g>'
    save("principles.svg", svg(W, H, b, defs))

def glyph(kind, x, y, c):
    if kind == "bars":
        return "".join(f'<rect x="{x+i*10}" y="{y+28-hh}" width="6" height="{hh}" rx="1.5" fill="{c}"/>' for i, hh in enumerate((10, 18, 28)))
    if kind == "chip":
        s = f'<rect x="{x+5}" y="{y+5}" width="20" height="20" rx="3" fill="none" stroke="{c}" stroke-width="2"/>'
        for i in range(3):
            p = 9 + i * 6
            s += (f'<line x1="{x+p}" y1="{y}" x2="{x+p}" y2="{y+5}" stroke="{c}" stroke-width="2"/><line x1="{x+p}" y1="{y+25}" x2="{x+p}" y2="{y+30}" stroke="{c}" stroke-width="2"/>'
                  f'<line x1="{x}" y1="{y+p}" x2="{x+5}" y2="{y+p}" stroke="{c}" stroke-width="2"/><line x1="{x+25}" y1="{y+p}" x2="{x+30}" y2="{y+p}" stroke="{c}" stroke-width="2"/>')
        return s
    if kind == "target":
        return (f'<circle cx="{x+15}" cy="{y+15}" r="13" fill="none" stroke="{c}" stroke-width="2"/><circle cx="{x+15}" cy="{y+15}" r="7" fill="none" stroke="{c}" stroke-width="2"/>'
                f'<circle cx="{x+15}" cy="{y+15}" r="2.5" fill="{c}"/>')
    return "".join(f'<rect x="{x+(i%2)*4}" y="{y+i*10}" width="24" height="7" rx="2" fill="{c}" fill-opacity="{1-i*.25}"/>' for i in range(3))

# ============================== PROJECT CARDS ==============================
def card(slug, c, metric, label, title, tag, desc, nodes, chipitems, box=None, back=None):
    W, H, PAD = 440, 300, 12
    defs = sweep_def(c)
    b = f'<clipPath id="pc"><rect width="{W}" height="{H}" rx="12"/></clipPath>' + plate(0, 0, W, H, c, r=12) + sweep(H, c, 8, span=520)
    msize = 28 if len(metric) <= 7 else 21
    b += (f'<text x="24" y="62" font-size="{msize}" font-weight="700" fill="{c}" filter="url(#glow2)">{esc(metric)}</text>'
          f'<text x="24" y="80" font-size="9" fill="{DIM}" letter-spacing="1">{esc(label)}</text>')
    pl, _ = pill(W - 20, 34, tag, c, size=8.5)
    b += pl
    b += f'<text x="24" y="112" font-size="15" font-weight="700" fill="{TXT}">{esc(title)}</text>'
    for i, ln in enumerate(desc):
        b += f'<text x="24" y="{134+i*16}" font-size="11" fill="{DIM}">{esc(ln)}</text>'
    b += flow(nodes, 24, 194, W - 48, c, size=9.5, box=box, back=back)
    ch, _ = chips(chipitems, 24, 258, W - 20, c, size=10, h=22, gap=7, pad=7)
    b += ch
    save(f"card-{slug}.svg", svg(W, H + PAD, b, defs))

def card_dr():
    W, H, PAD = 900, 316, 12
    c = TEAL
    defs = sweep_def(c) + f'<marker id="x"/>'
    b = f'<clipPath id="pc"><rect width="{W}" height="{H}" rx="12"/></clipPath>' + plate(0, 0, W, H, c, r=12) + sweep(H, c, 9, span=1060)
    b += (f'<text x="24" y="66" font-size="34" font-weight="700" fill="{c}" filter="url(#glow2)">&lt;200ms</text>'
          f'<text x="24" y="86" font-size="9" fill="{DIM}" letter-spacing="1">INT8 INFERENCE · JETSON NANO · FULLY ON-DEVICE</text>')
    pl, _ = pill(500, 34, "2026 · FLAGSHIP · UNCERTAINTY-AWARE", c, size=8.5)
    b += pl
    b += f'<text x="24" y="124" font-size="18" font-weight="700" fill="{TXT}">Adaptive TransUNet · DR Screening</text>'
    b += f'<text x="24" y="146" font-size="11.5" fill="{DIM}">Lesion localization and ordinal grading that flags its own doubt.</text>'
    bullets = ["100k+ fundus images, self-supervised pre-training",
               "Monte Carlo Dropout routes low-confidence cases onward",
               "TensorRT INT8: sub-200 ms on Jetson Nano, fully on-device"]
    y = 182
    for t in bullets:
        b += f'<text x="24" y="{y}" font-size="11.5" fill="{c}">▸</text><text x="42" y="{y}" font-size="11.5" fill="{TXT}" fill-opacity=".9">{esc(t)}</text>'
        y += 24
    ch, _ = chips(["PyTorch", "ViT", "OpenCV", "TensorRT INT8", "MC Dropout", "Jetson Nano", "Gradio"], 24, 268, 520, c, size=10, h=22, gap=7, pad=7)
    b += ch
    # diagram
    b += (f'<rect x="548" y="20" width="328" height="276" rx="10" fill="none" stroke="{c}" stroke-opacity=".35" stroke-dasharray="4 4"/>'
          f'<text x="560" y="38" font-size="8.5" fill="{c}" letter-spacing=".6">JETSON NANO · TENSORRT INT8 · &lt;200 MS</text>')
    b += node(560, 50, 82, 28, "Fundus image", c, 9.5) + node(668, 50, 196, 28, "Dual-scale encoder", c, 9.5, True)
    b += f'<line x1="642" y1="64" x2="663" y2="64" stroke="{c}" stroke-opacity=".7"/>' + tri(668, 64, "r", c)
    b += node(560, 118, 150, 28, "Lesion localization", c, 9.5) + node(718, 118, 146, 28, "Ordinal DR grading", c, 9.5)
    for (x1, x2) in ((766, 635), (766, 791)):
        b += f'<line x1="{x1}" y1="78" x2="{x2}" y2="113" stroke="{c}" stroke-opacity=".7"/>' + tri(x2, 118, "d", c)
    b += node(610, 184, 214, 30, "Monte Carlo Dropout · uncertainty", VIOLET, 9.5, True)
    for x1 in (635, 791):
        b += f'<line x1="{x1}" y1="146" x2="717" y2="180" stroke="{VIOLET}" stroke-opacity=".7"/>'
    b += tri(717, 184, "d", VIOLET)
    b += node(560, 250, 150, 28, "Automated result", GREEN, 9.5) + node(718, 250, 146, 28, "Specialist review", AMBER, 9.5)
    b += (f'<line x1="690" y1="214" x2="635" y2="245" stroke="{GREEN}" stroke-opacity=".7"/>' + tri(635, 250, "d", GREEN) +
          f'<line x1="744" y1="214" x2="791" y2="245" stroke="{AMBER}" stroke-opacity=".7"/>' + tri(791, 250, "d", AMBER) +
          f'<text x="632" y="236" text-anchor="end" font-size="8.5" fill="{GREEN}">confident</text><text x="796" y="236" font-size="8.5" fill="{AMBER}">ambiguous</text>')
    b += (f'<circle r="3" fill="{c}" filter="url(#glow2)"><animateMotion dur="4s" repeatCount="indefinite" path="M642 64 L668 64 L766 98 L635 118 L717 184 L690 214 L635 250"/></circle>')
    save("card-dr.svg", svg(W, H + PAD, b, defs))

def cards():
    card_dr()
    card("gcs", CYAN, "REAL-TIME", "TELEMETRY · TELECOMMAND", "Ground Control Station · PSIT VYOMNAUTS", "2025–26 · IN PRODUCTION",
         ["Electron/React desktop app on FastAPI + PostgreSQL:", "live telemetry, SVG instruments, replay, telecommand."],
         ["CanSat", "FastAPI", "PostgreSQL", "WebSocket", "React UI"], ["Electron", "React", "FastAPI", "PostgreSQL", "WebSocket"], back=(4, 1, "telecommand"))
    card("vaman", VIOLET, "<2s", "ON-DEVICE END-TO-END", "VAMAN · Autonomous Multimodal AI Pipeline", "2025 · FULLY ON-DEVICE",
         ["Whisper → LLM → TTS on a Jetson Nano for a dog robot,", "custom inter-module comms, zero external API calls."],
         ["Mic", "Whisper", "LLM", "TTS", "Speaker"], ["PyTorch", "Whisper", "LLMs", "TTS", "Jetson Nano"], box=(1, 3, "JETSON NANO · ON-DEVICE"))
    card("varuna", AMBER, "90%", "VALIDATION ACCURACY", "VARUNA · ViT on Noisy Real-World Data", "2025 · SMART INDIA HACKATHON",
         ["CMLRE marine platform: ViT-B/16 fisheries classifier that", "beats CNN baselines on noisy, label-scarce data."],
         ["Raw images", "Auto label + clean", "ViT-B/16", "Robustness eval"], ["PyTorch", "ViT-B/16", "Hugging Face"])
    card("fintech", PINK, "MULTI-AGENT", "NO HUMAN IN THE LOOP", "Autonomous FinTech Engagement Pipeline", "2026 · HACKATHON",
         ["Poonawala Fincorp build: agents turn student signals into", "career insights, EMI calculators and loan offers."],
         ["Student data", "Insight agents", "Offer agents", "EMI + loan"], ["Claude Code", "Multi-agent", "Tool-calling", "PostgreSQL"])

# ============================== TRACK RECORD ==============================
def track():
    W = 900
    LW, RX, RW = 440, 460, 440
    exp = [("Team Lead · Ground Control Station", "PSIT VYOMNAUTS · CanSat / rocketry", "2025 → now", AMBER,
            ["Own the telemetry + telecommand app from architecture to deployment", "Used across multiple TEKNOFEST / satellite competition cycles", "Write handoff docs so incoming teams can run it unaided"]),
           ("AI/ML Research Intern", "Raman Research and Innovation Pvt. Ltd.", "Apr – Jun 2025", GREEN,
            ["Benchmarked LLM/Transformer variants for context-window and retrieval efficiency", "Built custom PyTorch eval scripts for convergence, latency and benchmarks", "Tuned generative text + speech models to raise synthesis precision"]),
           ("Technical Lecturer & Mentor", "India Space Week · remote", "Apr 2025 – Jan 2026", CYAN,
            ["Taught Computer Vision and optimization algorithms to 1,000+ students", "Mentored PyTorch implementation and edge-case debugging"])]
    # layout left
    ly, left = 66, ""
    for (role, org, date, c, buls) in exp:
        left += (f'<circle cx="30" cy="{ly-4}" r="5.5" fill="#020617" stroke="{c}" stroke-width="2.5"/>'
                 f'<text x="48" y="{ly}" font-size="13" font-weight="700" fill="{TXT}">{esc(role)}</text>')
        dw = len(date) * 6.3 + 18
        left += (f'<rect x="{LW-16-dw:.1f}" y="{ly-14}" width="{dw:.1f}" height="19" rx="9.5" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".5"/>'
                 f'<text x="{LW-16-dw/2:.1f}" y="{ly-1}" text-anchor="middle" font-size="9.5" fill="{c}">{esc(date)}</text>')
        ly += 18
        left += f'<text x="48" y="{ly}" font-size="11" fill="{c}">{esc(org)}</text>'
        ly += 20
        for bl in buls:
            for j, ln in enumerate(textwrap.wrap(bl, 54)):
                left += (f'<text x="48" y="{ly}" font-size="10.5" fill="{DIM}">{"›" if j == 0 else " "}</text>' if j == 0 else "") + f'<text x="60" y="{ly}" font-size="10.5" fill="{TXT}" fill-opacity=".88">{esc(ln)}</text>'
                ly += 15
            ly += 3
        ly += 20
    left_h = ly - 6
    H = max(left_h, 384)
    spine_end = ly - 40
    b = ""
    b += plate(0, 0, LW, H, AMBER)
    b += f'<text x="24" y="34" font-size="11" fill="{DIM}" letter-spacing="1.5">▸ EXPERIENCE &amp; LEADERSHIP</text>'
    b += f'<line x1="30" y1="62" x2="30" y2="{spine_end}" stroke="{AMBER}" stroke-opacity=".35" stroke-width="2"/>' + left
    # right
    def section(y, h, label, c, rows):
        s_ = plate(RX, y, RW, h, c) + f'<text x="{RX+20}" y="{y+28}" font-size="11" fill="{DIM}" letter-spacing="1.5">▸ {label}</text>'
        ry = y + 56
        for r in rows:
            tag, text, tc = r[0], r[1], r[2]
            sub = r[3] if len(r) > 3 else None
            tw_ = len(tag) * 6.6 + 18
            s_ += (f'<rect x="{RX+20}" y="{ry-14}" width="{tw_:.1f}" height="20" rx="5" fill="{tc}" fill-opacity=".12" stroke="{tc}" stroke-opacity=".5"/>'
                   f'<text x="{RX+20+tw_/2:.1f}" y="{ry}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{tc}">{esc(tag)}</text>'
                   f'<text x="{RX+20+tw_+12:.1f}" y="{ry}" font-size="11" fill="{TXT}">{esc(text)}</text>')
            if sub:
                s_ += f'<text x="{RX+20+tw_+12:.1f}" y="{ry+15}" font-size="9.5" fill="{DIM}">{esc(sub)}</text>'
            ry += 40 if sub else 30
        return s_
    gaps = 12
    rh = [30 + 3 * 40 + 14, 30 + 2 * 40 + 14, 30 + 3 * 30 + 14]
    extra = (H - sum(rh) - 2 * gaps) / 3
    ys, y = [], 0
    for h in rh:
        ys.append((y, h + extra)); y += h + extra + gaps
    b += section(ys[0][0], ys[0][1], "RESEARCH", CYAN, [("IEEE", "Neuro-Feedback VR · IEEE CE2CT 2025", CYAN, "real-time emotion manipulation, adaptive VR environments"),
                                                       ("JOURNAL", "Dynamic VR Environment Synthesis · IJECS 2025", VIOLET, "ML for real-time 3D object integration · DOAJ, SINTA"),
                                                       ("TPC", "Program Committee & Reviewer · IEEE AUTOCOM 2026", PINK, "peer review of submitted research papers")])
    b += section(ys[1][0], ys[1][1], "AWARDS", AMBER, [("AIR-1", "TEKNOFEST TÜRKSAT Model Satellite · CDR", AMBER, "Critical Design Review · 2025, 2026 cycle"),
                                                      ("BEST DATA", "ISRO / IN-SPACe Model Satellite · 2025", TEAL, "Best Data Award winner")])
    b += section(ys[2][0], ys[2][1], "CREDENTIALS", VIOLET, [("ORACLE", "Agentic AI Foundations Associate · Aug 2026", TEAL), ("UDEMY", "AI Engineer Core Track · LLM, RAG, QLoRA, agents", VIOLET), ("B.TECH", "CSE (AI) · PSIT Kanpur · 2023 – 2027", CYAN)])
    save("track.svg", svg(W, H, b, sweep_def(AMBER)))

# ============================== FOOTER ==============================
def footer():
    W, H, T = 900, 130, 10.0
    defs = (reveal("f1", 36, 40, 720, 24, 0.4, 3.6, T) + reveal("f2", 36, 72, 720, 24, 4.2, 5.4, T) + sweep_def(TEAL))
    b = panel(W, H) + sweep(H, TEAL, 8)
    b += (f'<text x="36" y="58" font-size="15" clip-path="url(#f1)"><tspan fill="{GREEN}">anshuman@psit</tspan><tspan fill="{DIM}">:~$ </tspan>'
          f'<tspan fill="{TXT}">./hire_me.sh --role=intern --start=2027-01 --relocate=yes</tspan></text>'
          f'<text x="36" y="90" font-size="13" fill="{TEAL}" clip-path="url(#f2)">✔ build passing · open to opportunities · let\'s talk</text>')
    for k, (col, amp, spd) in enumerate(((TEAL, 8, 7), (CYAN, 6, 11))):
        d = "M0 112 " + " ".join(f"Q{x+30} {112-amp} {x+60} 112 T{x+120} 112" for x in range(0, 1200, 120))
        b += (f'<g clip-path="url(#pc)"><path d="{d}" fill="none" stroke="{col}" stroke-opacity="{.5-k*.2}" stroke-width="1.5">'
              f'<animateTransform attributeName="transform" type="translate" from="-120 0" to="0 0" dur="{spd/4}s" repeatCount="indefinite"/></path></g>')
    save("footer.svg", svg(W, H, b, defs))

if __name__ == "__main__":
    import textwrap
    hero(); nav(); snapshot(); expertise(); principles(); cards(); track(); footer()
    for slug, num, title, sub, col in [("snapshot", "01", "SNAPSHOT", "who I am, at a glance", TEAL),
                                       ("expertise", "02", "EXPERTISE → EVIDENCE", "every skill tied to something I have shipped", CYAN),
                                       ("work", "03", "SELECTED WORK", "five systems, from edge inference to multi-agent apps", VIOLET),
                                       ("record", "04", "TRACK RECORD", "experience, research, awards and credentials", AMBER),
                                       ("live", "05", "LIVE & CONTACT", "open-source activity and how to reach me", PINK)]:
        cluster_header(slug, num, title, sub, col)
    print("generated:", len(os.listdir(OUT)), "files in", os.path.abspath(OUT))
