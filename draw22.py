"""Draw the front page for Sunday 22 November 2026.

A pure-stdlib rasteriser: a small 5x7 bitmap font, filled rectangles,
circles and a hand-rolled PNG encoder (zlib + struct). No external
fonts, no network, no randomness -- two runs produce identical bytes.

Layout (1024 x 1024, newspaper front page):
  masthead band -> three lead stories -> three panels -> 46-story grid
  (two columns) -> UTC timeline -> Friday-close markets strip -> footer.
"""
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (24, 24, 24)
MUTED = (96, 90, 78)
NAVY = (18, 32, 60)
NAVY_LT = (38, 58, 96)
GOLD = (198, 148, 42)
RED = (172, 32, 28)
TEAL = (14, 110, 96)
RUST = (176, 84, 24)
CARD = (255, 255, 255)
LINE = (196, 188, 170)
GREEN = (28, 122, 54)
WHITE = (255, 255, 255)


# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one row per string, '#' = ink, '.' = clear.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': (".....", ".....", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': (".....", ".....", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': (".....", ".....", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01000", "01000", "11110", "01000", "01000", "01000"),
    'g': (".....", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", ".....", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", ".....", "00110", "00010", "00010", "00010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': (".....", ".....", "11010", "10101", "10101", "10101", "10101"),
    'n': (".....", ".....", "11110", "10001", "10001", "10001", "10001"),
    'o': (".....", ".....", "01110", "10001", "10001", "10001", "01110"),
    'p': (".....", ".....", "11110", "10001", "10001", "11110", "10000"),
    'q': (".....", ".....", "01111", "10001", "10001", "01111", "00001"),
    'r': (".....", ".....", "10110", "11001", "10000", "10000", "10000"),
    's': (".....", ".....", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    'u': (".....", ".....", "10001", "10001", "10001", "10011", "01101"),
    'v': (".....", ".....", "10001", "10001", "10001", "01010", "00100"),
    'w': (".....", ".....", "10001", "10101", "10101", "10101", "01010"),
    'x': (".....", ".....", "10001", "01010", "00100", "01010", "10001"),
    'y': (".....", ".....", "10001", "10001", "01111", "00001", "01110"),
    'z': (".....", ".....", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", "01100", "01100"),
    ',': (".....", ".....", ".....", ".....", "01100", "00100", "01000"),
    ':': (".....", "01100", "01100", ".....", "01100", "01100", "....."),
    ';': (".....", "01100", "01100", ".....", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", ".....", ".....", ".....", "....."),
    '"': ("01010", "01010", "01010", ".....", ".....", ".....", "....."),
    '!': ("00100", "00100", "00100", "00100", "00100", ".....", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", ".....", "00100"),
    '-': (".....", ".....", ".....", "01110", ".....", ".....", "....."),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': (".....", "00100", "00100", "01110", "00100", "00100", "....."),
    '=': (".....", ".....", "11111", ".....", "11111", ".....", "....."),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "11111"),
    '*': (".....", "10101", "01110", "10101", ".....", ".....", "....."),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '~': (".....", ".....", "01101", "10110", ".....", ".....", "....."),
    '^': ("00100", "01010", "10001", ".....", ".....", ".....", "....."),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '\\': ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    # bullet dot
    '\u2022': (".....", ".....", "01100", "01100", "01100", ".....", "....."),
    # em dash
    '\u2014': (".....", ".....", ".....", "11111", ".....", ".....", "....."),
    # ellipsis
    '\u2026': (".....", ".....", ".....", ".....", ".....", "10101", "10101"),
    # degree sign
    '\u00b0': ("01100", "10010", "01100", ".....", ".....", ".....", "....."),
}

# Normalise stray punctuation to glyphs we actually ship.
_CLEAN = {
    '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
    '\u2013': '-', '\u2212': '-', '\u00a0': ' ', '\u00e9': 'e',
    '\u00ed': 'i', '\u00f3': 'o', '\u00fa': 'u', '\u00f1': 'n',
    '\u00fc': 'u', '\u2011': '-', '\u00b7': '\u2022',
}


def clean(text):
    out = []
    for ch in text:
        ch = _CLEAN.get(ch, ch)
        out.append(ch if ch in FONT else ' ')
    return ''.join(out)


# ---------------------------------------------------------------- canvas
class Page:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.buf = bytearray(bg) * (w * h)

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def frame(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for dy in range(-rr, rr + 1):
                dx = int((rr * rr - dy * dy) ** 0.5)
                self.px(cx - dx, cy + dy, c)
                self.px(cx + dx, cy + dy, c)

    # -- text ------------------------------------------------------------
    def tw(self, text, scale=1):
        return sum(6 for _ in clean(text)) * scale - scale

    def text(self, x, y, text, scale=1, c=INK):
        cx = x
        for ch in clean(text):
            g = FONT.get(ch)
            if g is None:
                cx += 6 * scale
                continue
            for gy, row in enumerate(g):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        self.fill(cx + gx * scale, y + gy * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def centre(self, y, text, scale=1, c=INK, x0=0, x1=None):
        x1 = self.w if x1 is None else x1
        w = self.tw(text, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, text, scale, c)

    def wrap(self, text, scale, maxw):
        words = clean(text).split(' ')
        lines, cur = [], ''
        for wd in words:
            trial = wd if not cur else cur + ' ' + wd
            if self.tw(trial, scale) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, text, scale, maxw, c=INK, leading=None,
             max_lines=None):
        lead = (9 if scale == 1 else 9 * scale) if leading is None else leading
        lines = self.wrap(text, scale, maxw)
        if max_lines is not None:
            lines = lines[:max_lines]
        yy = y
        for ln in lines:
            self.text(x, yy, ln, scale, c)
            yy += lead
        return yy

    def trunc(self, text, scale, maxw):
        t = clean(text)
        if self.tw(t, scale) <= maxw:
            return t
        while t and self.tw(t + '\u2026', scale) > maxw:
            t = t[:-1]
        return t + '\u2026'


# ---------------------------------------------------------------- content
LEADS = [
    ("CLIMATE  •  ANTALYA", RED, "COP31 DEADLOCKED",
     "Climate talks spill into a second day of overtime, with fossil "
     "fuels the sticking point. The EU climate chief says the summit "
     "will produce a good deal or no deal at all. A draft drops "
     "fossil-fuel language and a $120bn adaptation-finance target.",
     "CONFIRMED", "Reuters, BBC"),
    ("MEXICO  •  JUSTICE", NAVY_LT, "'EL CHAPO ISIDRO' CAPTURED",
     "Mexican soldiers capture Fausto Isidro Meza Flores, 'El Chapo "
     "Isidro', on the FBI's 10 most-wanted list, in a shoot-out. "
     "Deadly cartel violence follows in Sinaloa.",
     "CONFIRMED", "Reuters, BBC 01:25 UTC"),
    ("LATIN AMERICA  •  QUAKE", RUST, "PERU QUAKE M6.7",
     "A magnitude 6.7 quake strikes the Junin Andes at 00:09 UTC, "
     "about 108-129 km deep. One dead, 16 injured. Felt in Lima, "
     "where a TV anchor kept reporting as the studio shook.",
     "CONFIRMED", "USGS, China Daily"),
]

PANELS = [
    ("SPACE", TEAL, "BEPICOLOMBO AT MERCURY",
     "ESA confirms overnight: after a 37-minute burn the probe was "
     "captured by Mercury's gravity. Only the second craft ever to "
     "orbit Mercury; $2bn, 8-year cruise.",
     "ESA, AP, Nature"),
    ("MIDDLE EAST", RED, "IRAN WAR: BAHRAIN HIT",
     "An Iranian attack hits an industrial facility in Bahrain. US "
     "Central Command denies Iran's claim it damaged a US F-16 over "
     "the Gulf. A Qatari delegation holds talks in Tehran.",
     "Reuters"),
    ("EUROPE", NAVY_LT, "RUSSIAN SHIP ABLAZE",
     "The Russian cargo ship Sparta II is hit by drones in the Baltic "
     "Sea, catches fire and drifts into Finnish waters. Its 16 crew "
     "evacuate; Finland says the attack was likely by Ukraine.",
     "Reuters"),
]

# (region tag, headline) -- 46 stories, in the order researched.
GRID = [
    ("EU", "NATO will defend every inch of Poland, Rutte says in Warsaw"),
    ("EU", "Denmark pushes EU to tighten travel curbs on Russians"),
    ("EU", "EU-Indonesia deal signed: 98.5% of tariffs cut after 10 years"),
    ("EU", "Sweden summons Russia's ambassador as Baltic tensions rise"),
    ("EU", "King Charles thanks Erdogan for hosting COP31"),
    ("EU", "Miliband: EU deal not tied to a tuition-fees agreement"),
    ("EU", "US 'willing to accept' a UN leader from Latin America - Waltz"),
    ("EU", "Hegseth memo curbs US-Canada defence ties, WaPo reports"),
    ("EU", "Trafalgar Square's Christmas tree felled in Norway"),
    ("ME", "Gaza: 4 Palestinians killed, 14 hurt in ceasefire violations"),
    ("ME", "UN warns Saudi-led strikes on Hodeidah threaten Yemen aid"),
    ("ME", "Pezeshkian: Iran faces a 'quiet economic war'"),
    ("ME", "Trump: only older chips may be sold to China"),
    ("ME", "Houthi missile hits a Riyadh tower (Fri)"),
    ("AF", "Al-Shabaab claims hundreds dead in ambush on Somali troops"),
    ("AF", "Kenya discharges its last Ebola patient; DRC toll tops 5,300"),
    ("AF", "Ghana unveils Heritage Series banknotes - Nkrumah, Kofi Annan"),
    ("AF", "Nigeria starts building naval ships to cut foreign dependence"),
    ("AF", "DRC enacts constitutional reform law amid high tensions"),
    ("AF", "Sahel states restart dialogue with the West Africa bloc"),
    ("AM", "FBI probes apparent hack of its NCIC criminal database"),
    ("AM", "US declassifies more UFO footage filmed in the Middle East"),
    ("AM", "Teen gamer and his mother help the FBI rescue a missing girl"),
    ("AM", "Indian-origin couple killed outside a Canada Walmart"),
    ("AM", "Democrats reclaim Congress in midterm victory (reported Sat)"),
    ("AM", "Trump: his next big Iran move may wait until 2027"),
    ("AP", "Modi opens the Nitish Setu bridge in Bihar (Sun)"),
    ("AP", "India passes 1 crore HPV vaccine doses (Sun)"),
    ("AP", "Manipur: illicit alcohol kills 11, sickens 180"),
    ("AP", "India-Japan defence pact: joint training, missile exercises"),
    ("AP", "Bangladesh: 30 Awami League houses torched"),
    ("AP", "JEE Main 2027 registration closes today (Sun)"),
    ("AP", "Gujarat crash: car splits in two; 7 killed incl. a baby"),
    ("AP", "BJP names cricketer Yuzvendra Chahal to OBC Morcha post (Sun)"),
    ("TE", "UN states agree talks to regulate 'killer robots' by 2028"),
    ("TE", "Voyager 1 now a light-day from Earth after 49 years"),
    ("TE", "Riemann proof claim still being checked; second proof claimed"),
    ("TE", "A lock of George Washington's hair sells for $4,000"),
    ("SP", "ATP Finals: Alcaraz beats Shelton; Zverev beats Medvedev"),
    ("SP", "F1 Las Vegas: Antonelli fastest, penalty hands Verstappen pole"),
    ("SP", "Premier League: Newcastle 2-2 Arsenal; Leeds stun Chelsea 4-1"),
    ("SP", "Wellington Test, Day 4: India dominate New Zealand"),
    ("SP", "Real Madrid 2-1 Celta Vigo"),
    ("SP", "Australia bowls first; injured Smith misses S. Africa decider"),
    ("SP", "France beat Argentina, reach Nations Championship final"),
    ("SP", "Australia beat Wales in the Nations Championship"),
]

TIMELINE = [
    ("00:09", "Peru quake M6.7 hits Junin"),
    ("00:10", "BBC: FBI hack; teen-gamer rescue"),
    ("01:25", "Mexico captures 'El Chapo Isidro'"),
    ("01:47", "EU-Indonesia deal signed"),
    ("02:06", "Lviv dashcam blast video"),
    ("04:00", "F1 Las Vegas GP; Verstappen on pole"),
    ("17:00", "TONIGHT: ATP final, Alcaraz v Zverev"),
]

MARKETS = [
    ("S&P 500", "6,910.39  -3.7%"),
    ("Nasdaq", "22,617.73  -5.3%"),
    ("Dow", "48,147.33  -1.9%"),
    ("VIX", "35.89  +86% wk"),
    ("Nvidia", "-14%"),
    ("Sensex", "+898 (Fri)"),
]


# ---------------------------------------------------------------- drawing
def draw_masthead(p):
    p.fill(0, 0, W, 92, NAVY)
    p.fill(0, 92, W, 4, GOLD)
    # globe mark: ring + meridians
    cx, cy, r = 52, 46, 30
    p.ring(cx, cy, r, GOLD, 3)
    p.vline(cx, cy - r, 2 * r, GOLD, 2)
    p.hline(cx - r, cy, 2 * r, GOLD, 2)
    p.fill(cx - 22, cy - 8, 44, 2, GOLD)
    p.fill(cx - 22, cy + 6, 44, 2, GOLD)
    p.text(96, 16, "THE WORLD IN ONE DAY", 3, WHITE)
    p.text(96, 62, "52 STORIES FROM EVERY REGION", 1, (200, 208, 224))
    # date block, right aligned
    p.text(700, 14, "SUNDAY", 2, GOLD)
    p.text(700, 40, "22 NOVEMBER 2026", 2, WHITE)
    p.text(700, 66, "ALL FIRST REPORTED TODAY", 1, (200, 208, 224))


def draw_lead(p, x, y, w, h, kicker, accent, title, body, conf, src):
    p.fill(x, y, w, h, CARD)
    p.frame(x, y, w, h, LINE, 1)
    p.fill(x, y, w, 8, accent)
    p.text(x + 12, y + 18, kicker, 1, accent)
    yy = p.para(x + 12, y + 34, title, 2, w - 24, INK, leading=20)
    p.hline(x + 12, yy + 4, w - 24, LINE, 1)
    yy = p.para(x + 12, yy + 12, body, 1, w - 24, INK, leading=11)
    # footer: confidence dot + source
    fy = y + h - 20
    p.disc(x + 18, fy + 4, 4, GREEN if conf == "CONFIRMED" else GOLD)
    p.text(x + 28, fy, conf, 1, MUTED)
    sw = p.tw(src, 1)
    p.text(x + w - 12 - sw, fy, src, 1, MUTED)


def draw_panel(p, x, y, w, h, kicker, accent, title, body, src):
    p.fill(x, y, w, h, CARD)
    p.frame(x, y, w, h, LINE, 1)
    p.fill(x, y, 6, h, accent)
    p.text(x + 16, y + 12, kicker, 1, accent)
    yy = p.para(x + 16, y + 26, title, 2, w - 32, INK, leading=20)
    p.para(x + 16, yy + 6, body, 1, w - 32, MUTED, leading=11)
    sw = p.tw(src, 1)
    p.text(x + w - 12 - sw, y + h - 18, src, 1, MUTED)


def draw_grid(p, x, y, w, h):
    p.text(x, y, "THE REST OF THE DAY", 2, INK)
    p.text(x + p.tw("THE REST OF THE DAY", 2) + 12, y + 2,
           "46 MORE STORIES, REGION BY REGION", 1, MUTED)
    p.hline(x, y + 24, w, INK, 2)
    col_w = (w - 24) // 2
    row_h = 13
    top = y + 32
    for i, (tag, head) in enumerate(GRID):
        col = i // 23
        row = i % 23
        gx = x + col * (col_w + 24)
        gy = top + row * row_h
        p.text(gx, gy, tag, 1, RED)
        line = p.trunc(head, 1, col_w - 34)
        p.text(gx + 30, gy, line, 1, INK)


def draw_timeline(p, x, y, w):
    p.text(x, y, "THE DAY IN UTC", 2, INK)
    p.text(x + p.tw("THE DAY IN UTC", 2) + 12, y + 2,
           "SEVEN MOMENTS, AS THEY WERE REPORTED", 1, MUTED)
    p.hline(x, y + 24, w, INK, 2)
    line_y = y + 46
    p.hline(x + 10, line_y, w - 20, NAVY_LT, 2)
    slot = (w - 20) / 7
    for i, (t, label) in enumerate(TIMELINE):
        cx = int(x + 10 + slot * i + slot / 2)
        p.disc(cx, line_y, 5, RED)
        p.ring(cx, line_y, 8, NAVY_LT, 1)
        tw = p.tw(t, 1)
        p.text(cx - tw // 2, line_y - 14, t, 1, NAVY)
        # label under the dot, wrapped to the slot width, max 2 lines so
        # it can never run into the markets strip below
        lx = int(cx - slot / 2 + 4)
        p.para(lx, line_y + 12, label, 1, int(slot) - 8, MUTED,
               leading=10, max_lines=2)


def draw_markets(p, x, y, w, h):
    p.fill(x, y, w, h, NAVY)
    p.text(x + 12, y + 10, "MARKETS", 2, GOLD)
    p.text(x + 12 + p.tw("MARKETS", 2) + 10, y + 12,
           "FRIDAY CLOSE, REPORTED SATURDAY", 1, (200, 208, 224))
    cell = (w - 24) / len(MARKETS)
    for i, (name, val) in enumerate(MARKETS):
        cx = int(x + 12 + cell * i)
        p.text(cx, y + 34, name, 1, (200, 208, 224))
        p.text(cx, y + 46, val, 1, WHITE)


def build_page():
    p = Page()
    draw_masthead(p)

    # three lead cards
    lx, lw, lh = 8, 328, 226
    for i, (kicker, accent, title, body, conf, src) in enumerate(LEADS):
        draw_lead(p, lx + i * (lw + 8), 108, lw, lh,
                  kicker, accent, title, body, conf, src)

    # three panels
    for i, (kicker, accent, title, body, src) in enumerate(PANELS):
        draw_panel(p, lx + i * (lw + 8), 346, lw, 140,
                   kicker, accent, title, body, src)

    # 46-story grid
    draw_grid(p, 8, 500, 1008, 0)

    # UTC timeline
    draw_timeline(p, 8, 838, 1008)

    # markets strip
    draw_markets(p, 8, 922, 1008, 66)

    # footer
    p.hline(8, 996, 1008, LINE, 1)
    p.centre(1004, "SOURCES: REUTERS  •  BBC  •  AP  •  USGS  •  ESA  •  ATP  •  F1  •  NPR",
             1, MUTED)
    return p


# ---------------------------------------------------------------- png out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(p):
    raw = bytearray()
    for yy in range(p.h):
        raw.append(0)  # filter: none
        raw += p.buf[yy * p.w * 3:(yy + 1) * p.w * 3]
    ihdr = struct.pack(">IIBBBBB", p.w, p.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


def build_png():
    return encode_png(build_page())


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    with open(out, "wb") as f:
        f.write(build_png())
    print("wrote", out)
