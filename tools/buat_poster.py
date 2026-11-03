"""Buat gambar poster untuk soal game-poster (kelas 3 SD).

Pemakaian:
    python tools/buat_poster.py            # buat semua poster
    python tools/buat_poster.py sehat bazar  # buat poster tertentu

Hasil: assets/poster/<id>.jpg (800x600, JPEG kualitas 88).
Poster digambar sendiri (judul, ikon emoji, badge harga/jadwal) supaya
isi tiap poster pasti sesuai dengan data soal di js/logic.js.
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DST = os.path.join(ROOT, "assets", "poster")
W, H = 800, 600
QUALITY = 88

FONT_BOLD = [
    "C:/Windows/Fonts/ariblk.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/seguibl.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]
FONT_REG = [
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]
FONT_EMOJI = [
    "C:/Windows/Fonts/seguiemj.ttf",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
]

# id, judul poster, jenis, pesan (jawaban soal gambar), emoji, badge, warna latar
POSTER = [
    # --- poster ajakan (kata kunci: ayo, mari, yuk) ---
    ("sehat", "Ayo Hidup Sehat!", "ajakan", "Makan sayur dan buah setiap hari", "\U0001f966", None, "#2ec4b6"),
    ("baca", "Ayo Rajin Membaca!", "ajakan", "Rajin membaca buku setiap hari", "\U0001f4da", None, "#5b5fef"),
    ("olahraga", "Ayo Olahraga Pagi!", "ajakan", "Olahraga pagi agar tubuh kuat", "\U0001f3c3", None, "#f4845f"),
    ("cuci", "Yuk Cuci Tangan!", "ajakan", "Cuci tangan sebelum makan", "\U0001f9fc", None, "#9b5de5"),
    ("air", "Mari Hemat Air!", "ajakan", "Matikan keran setelah dipakai", "\U0001f4a7", None, "#00b4d8"),
    # --- poster himbauan (kata kunci: jangan, dilarang, hindari) ---
    ("bunga", "Dilarang Memetik Bunga!", "himbauan", "Biarkan bunga tumbuh di taman", "\U0001f338", None, "#ff70a6"),
    ("sungai", "Jangan Buang Sampah di Sungai!", "himbauan", "Sungai harus tetap bersih", "\U0001f30a", None, "#43c59e"),
    ("listrik", "Jangan Buang-Buang Listrik!", "himbauan", "Matikan lampu yang tidak terpakai", "\U0001f4a1", None, "#ffb703"),
    ("jajan", "Hindari Jajan Sembarangan!", "himbauan", "Pilih jajan yang sehat dan bersih", "\U0001f361", None, "#e63946"),
    ("berlari", "Jangan Berlari di Dalam Kelas!", "himbauan", "Berjalan tenang saat di dalam kelas", "\U0001f6b6", None, "#8ac926"),
    # --- poster iklan (ada harga/promo) ---
    ("cendol", "Es Cendol Segar!", "iklan", "Es cendol segar hanya Rp5.000", "\U0001f963", "Diskon 50%", "#4ea8de"),
    ("buku", "Buku Tulis Motif Lucu!", "iklan", "Buku tulis lucu hanya Rp3.000", "\U0001f4d3", "Rp3.000", "#ff9f1c"),
    ("jus", "Jus Buah Segar!", "iklan", "Jus buah asli tanpa pengawet", "\U0001f9c3", "Rp8.000", "#2a9d8f"),
    ("cokelat", "Bola-Bola Cokelat!", "iklan", "Bola-bola cokelat enak dan murah", "\U0001f36b", "Beli 2 Gratis 1", "#b5179e"),
    # --- poster kegiatan (ada hari/jam/tempat) ---
    ("bazar", "Bazar Sekolah", "kegiatan", "Bazar sekolah Sabtu pagi", "\U0001f6cd️", "Sabtu 08.00", "#f72585"),
    ("lomba", "Lomba 17 Agustus", "kegiatan", "Lomba di halaman sekolah", "\U0001f3c5", "17 Agustus", "#4cc9f0"),
    ("pentas", "Pentas Seni Sekolah", "kegiatan", "Pentas seni di aula sekolah", "\U0001f3ad", "Jumat 07.00", "#7209b7"),
]

FOOTER = "SD CERIA"


def find_font(cands):
    for p in cands:
        if os.path.isfile(p):
            return p
    return None


def font(path, size):
    return ImageFont.truetype(path, size) if path else ImageFont.load_default()


def hex_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def shade(color, k):
    """k>0 = lebih terang, k<0 = lebih gelap."""
    if k >= 0:
        return tuple(max(0, min(255, round(c + (255 - c) * k))) for c in color)
    return tuple(max(0, min(255, round(c * (1 + k)))) for c in color)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, bold, max_w, max_h, start, minimum):
    """Perkecil ukuran huruf sampai teks (maks 3 baris) muat di kotak."""
    size = start
    while size > minimum:
        fnt = font(bold, size)
        lines = wrap(draw, text.upper(), fnt, max_w)
        if len(lines) <= 3:
            bbox = draw.textbbox((0, 0), "\n".join(lines), font=fnt)
            h = (bbox[3] - bbox[1]) * 1.28
            if h <= max_h:
                return fnt, lines
        size -= 2
    fnt = font(bold, minimum)
    return fnt, wrap(draw, text.upper(), fnt, max_w)


def starburst(cx, cy, r_out, r_in, points=15):
    pts = []
    for i in range(points * 2):
        ang = math.pi * i / points - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def draw_emoji(img, emoji, cx, cy, size, emoji_path):
    if not emoji_path:
        return
    try:
        fnt = ImageFont.truetype(emoji_path, size)
        tmp = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        d.text((size, size), emoji, font=fnt, embedded_color=True, anchor="mm")
        bbox = tmp.getbbox()
        if not bbox:
            return
        glyph = tmp.crop(bbox)
        img.alpha_composite(glyph, (int(cx - glyph.width / 2), int(cy - glyph.height / 2)))
    except Exception:
        return


def make_poster(row, bold, regular, emoji_path):
    pid, title, jenis, pesan, emoji, badge, color = row
    base = hex_rgb(color)

    img = Image.new("RGBA", (W, H), base + (255,))
    d = ImageDraw.Draw(img, "RGBA")

    # hiasan latar: dua lingkaran lembut
    light = shade(base, 0.35)
    dark = shade(base, -0.28)
    d.ellipse((-120, -140, 300, 280), fill=light + (110,))
    d.ellipse((W - 260, H - 300, W + 140, H + 120), fill=dark + (90,))

    # panel putih (badan poster)
    panel = (16, 16, W - 16, H - 16)
    d.rounded_rectangle(panel, radius=28, fill=(255, 255, 255, 255))

    # ikon emoji
    draw_emoji(img, emoji, 400, 172, 190, emoji_path)

    # judul
    title_font, lines = fit_text(d, title, bold, 640, 175, 74, 40)
    fnt_h = (title_font.size) * 1.28
    total = fnt_h * len(lines)
    y = 300 + (195 - total) / 2
    for ln in lines:
        d.text((400, y), ln, font=title_font, fill=dark, anchor="ma")
        y += fnt_h

    # badge harga / jadwal
    if badge:
        cx, cy = 686, 106
        d.polygon(starburst(cx, cy, 88, 68), fill=(255, 214, 51, 255), outline=(30, 30, 30, 255))
        bf = font(bold, 26 if len(badge) <= 11 else 21)
        blines = wrap(d, badge.upper(), bf, 132)
        by = cy - (len(blines) * bf.size * 1.16) / 2
        for ln in blines:
            d.text((cx, by), ln, font=bf, fill=(40, 24, 60, 255), anchor="ma")
            by += bf.size * 1.16

    # pita bawah
    band = (16, H - 96, W - 16, H - 16)
    d.rounded_rectangle(band, radius=28, fill=base + (255,))
    ff = font(regular, 26)
    label = "  ".join(FOOTER)
    d.text((400, H - 62), label, font=ff, fill=(255, 255, 255, 235), anchor="mm")

    return img.convert("RGB")


def main():
    os.makedirs(DST, exist_ok=True)
    bold = find_font(FONT_BOLD)
    regular = find_font(FONT_REG)
    emoji_path = find_font(FONT_EMOJI)
    if not bold:
        print("font tebal tidak ditemukan")
        return 1
    print("font judul :", bold)
    print("font ikon  :", emoji_path or "(tidak ada - ikon dilewati)")

    only = set(sys.argv[1:])
    for row in POSTER:
        if only and row[0] not in only:
            continue
        img = make_poster(row, bold, regular, emoji_path)
        out = os.path.join(DST, row[0] + ".jpg")
        img.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        kb = os.path.getsize(out) // 1024
        print(f"OK  {row[0]:9s} {row[2]:9s} {row[1]} -> {out} {kb}KB")
    print("selesai:", DST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
