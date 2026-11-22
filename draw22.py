"""Draw the Sunday 22 November 2026 front page and write entry.png.

Pure Pillow drawing: no browser, no network, deterministic. Every story,
figure and time comes from research-22nov.md in this repository.
Run: python3 draw22.py [output-path]   (default: entry.png beside this file)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")

W, H = 1024, 1024
M = 18                        # side margin
CW = W - 2 * M                # content width = 988

INK = (26, 26, 26)
PAPER = (247, 242, 231)
CARD = (255, 250, 240)
PANEL = (255, 253, 246)
RED = (167, 30, 34)
MUTED = (107, 98, 80)
RULE = (201, 192, 170)
GOLD = (232, 182, 76)
BLUE = (49, 81, 125)
GREEN = (158, 214, 163)
PINK = (255, 138, 122)
FAINT = (51, 51, 51)

FD = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

OK = "\u25cf"        # ● confirmed
DEV = "\u25d0"       # ◐ developing
DUE = "\u2606"       # ☆ due today


def wrap(text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, lines, fnt, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def hline(d, x0, y, x1, width=1, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- data
BARS = [("Nasdaq", "-5.3%", 100, RED), ("Nasdaq 100", "-5.6%", 100, RED),
        ("S&P 500", "-3.7%", 66, BLUE), ("Dow", "-1.9%", 34, BLUE)]

STRIP = [("6,910.39", "S&P 500 -3.7%", PINK), ("22,617.73", "Nasdaq -5.3%", PINK),
         ("48,147.33", "Dow -1.9%", PINK), ("35.89", "VIX, +86% on week", PINK),
         ("-14%", "Nvidia", PINK), ("$88.91", "Anthropic -9%", PINK),
         ("+898", "Sensex (Fri)", GREEN), ("-$8.7tn", "Nasdaq since Oct peak", PINK)]

PANELS = [
    ("Space · Science", OK,
     "BepiColombo is captured by Mercury",
     "ESA confirms overnight: the $2bn probe slipped into orbit after a "
     "37-minute burn — only the 2nd craft ever to orbit Mercury. "
     "Probes split 9 Dec.",
     "ESA · AP · Nature"),
    ("Middle East · War", OK,
     "Iran hits Bahrain; US denies F-16 claim",
     "An Iranian attack hits an industrial facility in Bahrain; the US "
     "denies Tehran's claim it damaged a US F-16. Qatar holds talks "
     "in Tehran.",
     "Reuters"),
    ("Europe · Baltic", OK,
     "Russian ship ablaze after drone strike",
     "The cargo ship Sparta II is hit by drones in the Baltic, catches "
     "fire and drifts into Finnish waters. Its 16 crew evacuate; "
     "Finland blames Ukraine.",
     "Reuters"),
]

# (mark, headline, fact + source) — 46 items, 4 columns x 12 rows
GRID = [
    (OK, "NATO: defend 'every inch'", "Rutte in Warsaw: NATO will defend every inch of Polish territory. Reuters"),
    (OK, "Denmark pushes EU curbs", "Tighten travel curbs on Russians after the foiled assassination plot. Reuters"),
    (OK, "EU–Indonesia deal signed", "98.5% of tariffs cut after 10 years of talks. EU"),
    (DEV, "Sweden summons envoy", "Russia's ambassador called in as Baltic tensions rise. Sweden"),
    (OK, "King Charles thanks Türkiye", "Praises Erdoğan for hosting COP31; urges urgent climate action. Palace"),
    (DEV, "Miliband on EU deal", "Deal not tied to a tuition-fees agreement, minister says. UK"),
    (DEV, "US open to Latin UN chief", "Washington 'willing to accept' a UN leader from Latin America. Waltz"),
    (DEV, "Hegseth memo curbs Canada", "Secret memo restricts the US–Canada defence relationship. WaPo"),
    (OK, "Trafalgar tree felled", "London's Christmas tree cut down in Norway. BBC"),
    (DEV, "Gaza: 4 killed, 14 hurt", "Palestinians killed in Israeli ceasefire violations across Gaza. Gaza"),
    (DEV, "UN warns on Hodeidah", "Saudi-led strikes threaten Yemen's aid lifeline, the UN says. UN"),
    (OK, "Pezeshkian: 'quiet war'", "Iran faces a 'quiet economic war', harder than missiles. Iran"),
    (DEV, "Trump: older chips only", "Only older chips may be sold to China, Trump says. US"),
    (DEV, "Houthi missile hits Riyadh", "A tower struck on Friday; Saudi coalition hits back. AP"),
    (DEV, "Al-Shabaab ambush claim", "Group claims hundreds dead in an ambush on Somali troops. Somalia"),
    (OK, "Kenya clears last Ebola case", "Last patient discharged; DRC death toll passes 5,300. Kenya"),
    (OK, "Ghana's new banknotes", "Heritage Series honours Nkrumah and Kofi Annan. Ghana"),
    (OK, "Nigeria builds naval ships", "Home-built warships to cut foreign dependence. Nigeria"),
    (DEV, "DRC reform law enacted", "Tshisekedi enacts constitutional reform amid high tensions. DRC"),
    (DEV, "Sahel talks resume", "Sahel states restart dialogue with the West Africa bloc. ECOWAS"),
    (OK, "FBI probes database hack", "Apparent hack of the NCIC criminal database; Trump: 'not good'. AP/CNN"),
    (DEV, "US releases UFO footage", "More declassified footage filmed in the Middle East. Pentagon"),
    (OK, "Teen gamer aids FBI rescue", "A 16-year-old and his mother help rescue a missing girl. BBC"),
    (DEV, "Couple killed in Canada", "Indian-origin couple shot outside a Walmart; targeted attack likely. Canada"),
    (DEV, "Democrats retake Congress", "Midterm victory reported on Saturday; Republicans lose the House. US"),
    (DEV, "Trump: Iran move may wait", "Next big Iran move may not come until 2027, Trump signals. US"),
    (OK, "Modi opens Nitish Setu", "Bridge links Patna and Vaishali districts in Bihar. India"),
    (OK, "India passes 1 cr HPV jabs", "One-crore milestone in the national vaccination drive. India"),
    (OK, "Manipur liquor kills 11", "Illicit alcohol kills 11 and sickens 180 in the state. India"),
    (DEV, "India–Japan defence pact", "Joint training and missile exercises agreed at 2+2 talks. India"),
    (DEV, "30 Awami houses torched", "Houses of Awami League members set on fire in Bangladesh. Dhaka"),
    (OK, "JEE Main 2027 closes today", "Registration for Session 1 ends on Sunday. NTA"),
    (DEV, "Gujarat crash kills 7", "Car splits in two after hitting a truck; a baby among the dead. India"),
    (DEV, "Chahal joins BJP panel", "Cricketer named to the OBC Morcha executive committee. BJP"),
    (OK, "UN agrees 'killer robot' talks", "States to negotiate rules on autonomous weapons by 2028. UN"),
    (OK, "Voyager 1 a light-day out", "After 49 years, the probe is one light-day from Earth. NASA"),
    (DEV, "Riemann proof still checked", "Claim stands unverified; a second, human-only proof claimed. Science"),
    (OK, "Washington's hair: $4,000", "A lock of George Washington's hair sells at auction. BBC"),
    (OK, "Alcaraz v Zverev tonight", "Alcaraz beats Shelton; Zverev beats Medvedev. Final 18:00 CET. ATP"),
    (OK, "Verstappen on Vegas pole", "Antonelli fastest (1:33.893) but a penalty drops him to 6th. F1"),
    (OK, "Arsenal held; City held", "Newcastle 2-2 Arsenal; Man City 1-1 Fulham; Leeds stun Chelsea 4-1. AFP"),
    (DEV, "India dominate in Wellington", "Day 4 of the Test: India on top against New Zealand. Test"),
    (OK, "Real Madrid 2-1 Celta", "Madrid win at home in La Liga on Saturday. La Liga"),
    (OK, "Smith out of SA decider", "Injured Smith misses; Australia bowl first. Cricket"),
    (OK, "France reach rugby final", "Beat Argentina; face South Africa in the Nations final. Rugby"),
    (OK, "Australia beat Wales", "Win in the Nations Championship on Saturday. Rugby"),
]

TIMELINE = [
    ("00:09", "Peru quake M6.7 strikes Junín; felt in Lima"),
    ("00:10", "BBC publishes FBI hack + teen-gamer rescue"),
    ("01:25", "Mexico captures 'El Chapo Isidro'"),
    ("01:47", "EU–Indonesia trade deal signed after 10 years"),
    ("02:06", "Euronews publishes Lviv dashcam blast video"),
    ("04:00", "F1 Las Vegas GP under lights; Verstappen on pole"),
    ("17:00 " + DUE, "Tonight: ATP Finals final, Alcaraz v Zverev"),
]


def draw_topbar(d, y):
    f = SANS_B(11)
    hline(d, M, y, M + CW, 3)
    d.text((M, y + 5), "ONE PAGE · THE WHOLE DAY", font=f, fill=MUTED)
    mid = "52 SOURCED STORIES"
    d.text((M + CW // 2 - f.getlength(mid) // 2, y + 5), mid, font=f, fill=MUTED)
    right = "MORNING EDITION"
    d.text((M + CW - f.getlength(right), y + 5), right, font=f, fill=MUTED)
    hline(d, M, y + 24, M + CW, 1)
    return y + 26


def draw_masthead(d, y):
    name = "THE WORLD IN ONE IMAGE"
    f = SERIF_B(40)
    d.text((M + CW // 2 - f.getlength(name) // 2, y), name, font=f, fill=INK)
    y += 46
    date = "SUNDAY 22 NOVEMBER 2026"
    df = SERIF_B(24)
    tag = "— 52 stories, 7 regions, every story marked how sure"
    tf = SERIF(13)
    dw = df.getlength(date)
    tw = tf.getlength(tag)
    total = dw + 12 + tw
    x = M + (CW - total) // 2
    d.text((x, y), date, font=df, fill=INK)
    d.text((x + dw + 12, y + 7), tag, font=tf, fill=(76, 70, 58))
    y += 34
    hline(d, M, y, M + CW, 1)
    hline(d, M, y + 4, M + CW, 3)
    return y + 8


def draw_leads(d, y):
    h = 180
    left_w = 600
    gap = 6
    right_x = M + left_w + gap
    right_w = CW - left_w - gap
    kf = SANS_B(11)
    # --- main lead: COP31
    d.rectangle([M, y, M + left_w, y + h], outline=INK, width=3, fill=CARD)
    x = M + 12
    yy = y + 8
    d.text((x, yy), "LEAD · CLIMATE · ANTALYA  " + OK, font=kf, fill=RED)
    yy += 18
    yy = para(d, x, yy,
              wrap("COP31 deadlocked: talks spill into a second day of overtime",
                   SERIF_B(26), left_w - 24), SERIF_B(26), INK, 28)
    yy += 3
    yy = para(d, x, yy,
              wrap("Nearly 200 nations still split over fossil fuels; the EU says "
                   "the summit will produce a good deal or no deal at all.",
                   SANS(13), left_w - 24), SANS(13), FAINT, 16)
    yy += 5
    for lab, val, pct, col in BARS:
        bl, bv = SANS_B(11), SERIF_B(11)
        d.text((x + 118 - bl.getlength(lab), yy), lab, font=bl, fill=INK)
        tx = x + 124
        tw = 300
        d.rectangle([tx, yy + 1, tx + tw, yy + 10], outline=INK, width=1,
                    fill=(233, 225, 204))
        d.rectangle([tx, yy + 1, tx + int(tw * pct / 100), yy + 10], fill=col)
        d.text((tx + tw + 6, yy), val, font=bv, fill=INK)
        yy += 13
    # --- right column: two stacked leads
    half = (h - gap) // 2
    d.rectangle([right_x, y, right_x + right_w, y + half], outline=INK, width=3,
                fill=CARD)
    sx = right_x + 11
    sy = y + 8
    d.text((sx, sy), "LEAD · MEXICO  " + OK, font=kf, fill=RED)
    sy += 18
    sy = para(d, sx, sy,
              wrap("'El Chapo Isidro' captured", SERIF_B(16), right_w - 22),
              SERIF_B(16), INK, 18)
    para(d, sx, sy,
         wrap("Mexico's army seizes Fausto Isidro Meza Flores, on the FBI's "
              "10 most-wanted list, in a shoot-out; deadly cartel violence "
              "follows in Sinaloa.",
              SANS(11), right_w - 22), SANS(11), FAINT, 13)
    y2 = y + half + gap
    d.rectangle([right_x, y2, right_x + right_w, y2 + half], outline=INK, width=3,
                fill=CARD)
    sy = y2 + 8
    d.text((sx, sy), "LEAD · PERU  " + OK, font=kf, fill=RED)
    sy += 18
    sy = para(d, sx, sy,
              wrap("Peru quake M6.7 kills 1, hurts 16", SERIF_B(16), right_w - 22),
              SERIF_B(16), INK, 18)
    para(d, sx, sy,
         wrap("00:09 UTC: the Junín Andes shake; felt in Lima, where a TV "
              "anchor kept reporting as the studio shook.",
              SANS(11), right_w - 22), SANS(11), FAINT, 13)
    return y + h


def draw_strip(d, y):
    h = 38
    d.rectangle([M, y, M + CW, y + h], fill=INK, outline=INK, width=2)
    lx = M + 10
    lf = SANS_B(11)
    ly = y + 8
    for ln in ("MARKETS", "FRI CLOSE"):
        d.text((lx, ly), ln, font=lf, fill=GOLD)
        ly += 13
    x = M + 92
    cell_w = (CW - 92) / len(STRIP)
    vf, cf = SERIF_B(15), SANS(9)
    for i, (val, cap, col) in enumerate(STRIP):
        cx = x + i * cell_w
        if i:
            d.line([(cx, y + 4), (cx, y + h - 4)], fill=(76, 70, 54), width=1)
        d.text((cx + cell_w / 2 - vf.getlength(val) / 2, y + 4), val, font=vf,
               fill=col)
        d.text((cx + cell_w / 2 - cf.getlength(cap) / 2, y + 23), cap, font=cf,
               fill=(207, 199, 174))
    return y + h


def draw_panels(d, y):
    h = 118
    pw = (CW - 12) / 3
    kf = SANS_B(11)
    hf = SERIF_B(16)
    bf = SANS(11)
    sf = SANS_B(10)
    for i, (kick, mark, head, body, src) in enumerate(PANELS):
        x0 = M + i * (pw + 6)
        d.rectangle([x0, y, x0 + pw, y + h], outline=INK, width=2, fill=PANEL)
        x = x0 + 10
        yy = y + 6
        d.text((x, yy), kick.upper() + "  " + mark, font=kf, fill=RED)
        yy += 17
        yy = para(d, x, yy, wrap(head, hf, pw - 20), hf, INK, 18)
        yy += 2
        yy = para(d, x, yy, wrap(body, bf, pw - 20), bf, FAINT, 13)
        d.text((x, y + h - 16), src.upper(), font=sf, fill=MUTED)
    return y + h


def draw_grid(d, y):
    hf = SERIF_B(13)
    d.text((M, y), "THE DAY IN 46 MORE STORIES", font=hf, fill=INK)
    right = "● confirmed  ·  ◐ developing  ·  ☆ due today"
    rf = SERIF(11)
    d.text((M + CW - rf.getlength(right), y + 1), right, font=rf, fill=(76, 70, 58))
    y += 19
    hline(d, M, y, M + CW, 2)
    y += 4
    cols = 4
    col_w = (CW - (cols - 1) * 13) / cols
    rows = (len(GRID) + cols - 1) // cols
    row_h = 34.0
    kh = SANS_B(11)
    ff = SANS(9)
    for idx, (mark, head, fact) in enumerate(GRID):
        r, c = divmod(idx, cols)
        x0 = M + c * (col_w + 13)
        yy = y + r * row_h
        hline(d, x0, yy, x0 + col_w, 1, fill=RULE)
        yy += 2
        d.text((x0, yy), mark + " " + head, font=kh, fill=INK)
        yy += 13
        flines = wrap(fact, ff, col_w)
        para(d, x0, yy, flines[:2], ff, FAINT, 10)
    return y + rows * row_h


def draw_timeline(d, y):
    h = 82
    d.rectangle([M, y, M + CW, y + h], outline=INK, width=2, fill=CARD)
    tf = SANS_B(11)
    d.text((M + 10, y + 4), "THE DAY SO FAR · UTC · SUNDAY 22 NOVEMBER 2026",
           font=tf, fill=RED)
    cell_w = (CW - 20) / len(TIMELINE)
    tf2 = SERIF_B(12)
    df = SANS(9)
    yy = y + 24
    for i, (t, txt) in enumerate(TIMELINE):
        x0 = M + 10 + i * cell_w
        if i:
            d.line([(x0 - 5, yy + 2), (x0 - 5, y + h - 8)], fill=RULE, width=1)
        d.text((x0, yy), t, font=tf2, fill=RED)
        para(d, x0, yy + 16, wrap(txt, df, cell_w - 10), df, FAINT, 11)
    return y + h


def draw_footer(d, y):
    f = SANS(10)
    hline(d, M, y, M + CW, 1)
    left = ("52 stories · 7 regions · Friday items tagged Fri; tonight's items "
            "marked ☆ · date-checked 22 Nov 2026")
    d.text((M, y + 4), left, font=f, fill=MUTED)
    right = "Sources in each item · v1 morning edition, to 05:30 UTC"
    d.text((M + CW - f.getlength(right), y + 4), right, font=f, fill=MUTED)
    return y + 18


def main():
    assert len(GRID) == 46, "grid must hold 46 stories, got %d" % len(GRID)
    assert len(PANELS) == 3 and len(TIMELINE) == 7
    assert len(BARS) == 4 and len(STRIP) == 8
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 10
    y = draw_topbar(d, y) + 2
    y = draw_masthead(d, y) + 2
    y = draw_leads(d, y) + 6
    y = draw_strip(d, y) + 6
    y = draw_panels(d, y) + 6
    y = draw_grid(d, y) + 6
    y = draw_timeline(d, y) + 4
    y = draw_footer(d, y)
    assert y <= H, "layout overflow: ended at y=%d" % y
    img.save(OUT, format="PNG", optimize=True)
    n = os.path.getsize(OUT)
    print("wrote %s: %dx%d, %d bytes (layout ended y=%d)" % (OUT, W, H, n, y))
    if n > 1_048_576:
        raise SystemExit("oversize: %d bytes" % n)


if __name__ == "__main__":
    main()
