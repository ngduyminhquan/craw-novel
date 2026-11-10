"""Quét raw tìm tên riêng / thuật ngữ / tên kỹ năng CHƯA có trong glossary.md và characters.md.

    python extract_terms.py <slug> <range> [--min 1] [--all]

<range>: 5 | 1-20 | 1,3,5-7. Dùng range rộng (vd 1-20) để dựng glossary ban đầu.
--all: in cả những từ đã có (kèm bản dịch) để soát.
Raw tiếng Nhật (novel.json "raw_lang": "ja", hoặc tự đoán): bắt cụm katakana, nội dung 【】『』《》
và kanji đứng trước kính ngữ (さん, 様, 殿...).
"""
import argparse
import re
from collections import Counter

from common import (KATA, contains, entries, get_row, has_cjk, load_novel, load_progress, parse_range, raw_lang,
                    raw_paragraphs, term_regex, utf8_stdout)

# Từ viết hoa thông dụng, không phải tên riêng.
STOP = set("""
I I'm I'll I'd I've A An The This That These Those There Then Than Though Thus Therefore However Moreover Meanwhile
He She It We They You Me Him Her Us Them My His Its Our Their Your Mine Yours Hers Ours Theirs
What Who Whom Whose Which When Where Why How Whatever Whoever Whichever Wherever However
And But Or Nor So Yet For Because Since As If Unless Although While Whether Even Just Only Also Still
Is Are Was Were Be Been Being Am Do Does Did Done Have Has Had Can Could Will Would Shall Should May Might Must
Not No Yes Yeah Yep Nope Oh Ah Eh Uh Um Hmm Huh Hey Well Okay OK Ok Wow Whoa Ha Haha Heh Hehe Kuk Kak Ugh Tsk Phew Hmph
At By In On Of To From With Without Into Onto Upon Over Under After Before About Above Below Between Through
All Any Some Each Every Both Either Neither Many Much More Most Few Less Least Other Another Such Same
Now Here Today Tomorrow Yesterday Soon Again Once Twice First Second Third Last Next Finally Suddenly Actually
Of-course Please Thank Thanks Sorry Right Like Let Let's Don't Didn't Can't Won't Isn't Wasn't It's That's What's
Mr Mrs Ms Sir Miss Lv Level Chapter Prologue Epilogue Afterword Extra
Monday Tuesday Wednesday Thursday Friday Saturday Sunday
""".split())

WORD = r"[A-Z][A-Za-z’'\-]*[A-Za-z]|[A-Z]"
CAP_SEQ = re.compile(rf"(?:{WORD})(?:\s+(?:of|the|de|von|van|and)?\s*(?:{WORD}))*")
BRACKET = re.compile(r"\[([^\[\]\n]{1,80})\]")
LEVEL = re.compile(r"\s*(?:Lv\.?|Level)\s*\d+.*$", re.IGNORECASE)
QUOTED = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”|‘[^’\n]*’|\[[^\]\n]*\]")


# ---------- Tiếng Nhật ----------

KATA_RUN = re.compile(rf"[{KATA}][{KATA}・]*[{KATA}]")
JA_BRACKET = re.compile(r"【([^【】\n]{1,30})】|『([^『』\n]{1,30})』|《([^《》\n]{1,30})》")
HONORIFIC = re.compile(r"([一-鿿々]{1,4})(?=さん|さま|様|殿下|殿|陛下|君|くん|ちゃん|先生|師匠|嬢)")
JA_QUOTED = re.compile(r"「[^」\n]*」|『[^』\n]*』|（[^）\n]*）")
JA_FIRST = re.compile(r"俺|僕|私|儂|あたし|わたし|おれ|ぼく|わし")
JA_THIRD = re.compile(r"彼女|彼")
SMALL_END = tuple("ァィゥェォッャュョ")
# Katakana thông dụng (đồ vật, từ mượn, từ tượng hình), không phải tên riêng hay thuật ngữ.
JA_STOP = set("""
ナイフ リスト ゲーム ローブ ベッド ドア ドアノブ イメージ ファンタジー パン ミス ダメージ ボード テーブル シルク
ウサギ ガキ シチュー アレ コレ ソレ タイミング リス マシ スペック グループ スペース ストレス リーダー スパイ
オーバー サブカルチャー プレート メイン レア シンボル ペンダント リンゴ デザート ブランク ポニーテール ワイン
コップ スープ パイ ケーキ ミルク コーヒー ジュース ビール フォーク スプーン ナプキン カップ ポケット ボタン
ベルト ブーツ コート マント フード ハンカチ タオル ロープ バッグ カバン ページ ノート ペン メモ ルール チーム
メンバー ペース ポイント チャンス ピンチ ミッション プラン ショック パニック ジョーク ユーモア センス マナー
ライバル ヒント サイズ スピード パワー エネルギー バランス コントロール テクニック ライン エリア ゾーン ルート
ゴール スタート ストップ トップ ベスト ラスト ワースト プロ アマ ファン ブーム アップ ダウン
テレビ ラジオ スマホ パソコン ネット メール カメラ バス タクシー トラック ビル ホテル レストラン カフェ
スーパー コンビニ アパート マンション トイレ キッチン リビング ガラス プラスチック ゴム ビニール
チラリ ピクリ ニヤリ ペコリ ペタリ ジロリ ギロリ ニコリ ポトリ コクリ ゴクリ ドサリ バサリ フワリ
ヒラリ キラリ ギクリ ビクリ ニッコリ ガックリ ズン ドン バン ガン ゴン
セット サイン カウンター アピール タイトル ズバリ
""".split())


# Kanji hay đứng trước kính ngữ mà không phải tên người.
JA_KANJI_STOP = {"受付", "お客", "皆", "皆様", "店員", "旦那", "奥", "神", "王", "王女", "王子", "姫"}


def _mimetic(term):
    """Từ tượng thanh/tượng hình: tiếng kêu kết thúc bằng kana nhỏ (グルゥ, ギィッ), hay lặp đôi (コリコリ)."""
    if term.endswith(SMALL_END):
        return True
    half = len(term) // 2
    return len(term) % 2 == 0 and half >= 2 and term[:half] == term[half:]


def mask_known(text, known):
    """Che các thuật ngữ đã có trong context (dài trước), để phần còn lại chỉ là chữ chưa có."""
    for t in sorted((t for t in known if has_cjk(t)), key=len, reverse=True):
        if t in text:
            text = term_regex(t).sub(lambda m: "　" * len(m.group(0)), text)
    return text


def candidates_ja(paragraphs, known):
    """Như candidates() nhưng cho raw tiếng Nhật. `known`: các thuật ngữ đã có, viết thường."""
    names, brackets = Counter(), Counter()
    for para in paragraphs:
        for m in JA_BRACKET.finditer(para):
            inner = next(g for g in m.groups() if g).strip()
            if len(inner) >= 2:
                brackets[inner] += 1
        masked = mask_known(para, known)
        for m in KATA_RUN.finditer(masked):
            t = m.group(0).strip("・")
            if len(t) >= 2 and t not in JA_STOP and not _mimetic(t):
                names[t] += 1
        for m in HONORIFIC.finditer(masked):
            if len(m.group(1)) >= 2 and m.group(1) not in JA_KANJI_STOP:
                names[m.group(1)] += 1
    # Cụm vừa đứng ngoài vừa nằm trong ngoặc thì chỉ liệt kê một lần ở mục tên.
    for t in [t for t in brackets if t in names]:
        names[t] += brackets.pop(t)
    return names, brackets


def known_terms(novel):
    ctx = novel["context"]
    out = {}
    for path in (ctx / "glossary.md", ctx / "characters.md"):
        for e in entries(path):
            for t in [e["en"], *e["aliases"]]:
                out[t.lower()] = e
    return out


def strip_possessive(s):
    return re.sub(r"(’s|'s|’|')$", "", s)


def candidates(paragraphs):
    """Trả về Counter tên riêng ứng viên và Counter nội dung trong [ ] ngắn."""
    names, initial_only, brackets = Counter(), Counter(), Counter()
    lower_words = set(re.findall(r"\b[a-z][a-z’'\-]+\b", "\n".join(paragraphs)))
    for para in paragraphs:
        for m in BRACKET.finditer(para):
            inner = LEVEL.sub("", m.group(1)).strip(" .!?")
            words = inner.split()
            # [You have become ...], [Of course ...] là câu thông báo, không phải tên
            if 0 < len(words) <= 6 and words[0] not in STOP and words[0][0].isupper():
                brackets[inner] += 1
        for m in CAP_SEQ.finditer(para):
            # "Yu IlHan's Earth" -> chỉ lấy "Yu IlHan"
            words = re.split(r"[’']s\s+", m.group(0))[0].split()
            while words and (words[0] in STOP or strip_possessive(words[0]) in STOP):
                words.pop(0)
            while words and words[-1].lower() in {"of", "the", "de", "von", "van", "and"}:
                words.pop()
            if not words:
                continue
            term = strip_possessive(" ".join(words))
            if len(term) < 2 or term in STOP:
                continue
            before = para[: m.start()].rstrip()
            sentence_start = not before or before[-1] in ".!?\"“‘'…:"
            names[term] += 1
            if sentence_start and len(words) == 1 and m.group(0).split()[0] == words[0]:
                initial_only[term] += 1
    for t in list(names):
        if " " in t or t in brackets:
            continue
        # Từ đơn chỉ xuất hiện ở đầu câu, có dạng viết thường ở chỗ khác, hoặc là dạng rút gọn
        # (You're, Wouldn't) thì là từ thường viết hoa, bỏ.
        if (initial_only[t] == names[t] or t.lower() in lower_words or len(t) < 3
                or re.search(r"(n[’']t|[’'](re|ve|ll|d|m|s))$", t)):
            del names[t]
    # Cụm vừa đứng ngoài vừa nằm trong [ ] thì là tên riêng, chỉ liệt kê một lần ở mục tên.
    for t in [t for t in brackets if t in names]:
        names[t] += brackets.pop(t)
    return names, brackets


def pov_hint(paragraphs, lang="en"):
    if lang == "ja":
        narration = " ".join(JA_QUOTED.sub(" ", p) for p in paragraphs)
        first, third = len(JA_FIRST.findall(narration)), len(JA_THIRD.findall(narration))
        # Văn ngôi 3 vẫn lẻ tẻ có 俺/私 ngoài 「」 (độc thoại không ngoặc), nên cần đủ dày mới tính là ngôi 1.
        first_person = first >= max(3, 0.05 * len(paragraphs)) and first > third * 0.5
        return {"pov": "NGÔI 1 (người kể xưng 'tôi')" if first_person else "NGÔI 3",
                "first": first, "third": third, "first_label": "俺/僕/私", "third_label": "彼/彼女",
                "dialogue": sum(1 for p in paragraphs if p.startswith(("「", "『"))),
                "system": sum(1 for p in paragraphs if p.startswith(("【", "["))), "system_label": "【】/[ ]",
                "paragraphs": len(paragraphs)}
    narration = " ".join(QUOTED.sub(" ", p) for p in paragraphs)
    first = len(re.findall(r"\b(I|me|my|myself)\b", narration))
    third = len(re.findall(r"\b(he|she|him|his|her|himself|herself)\b", narration, re.IGNORECASE))
    dialogue = sum(1 for p in paragraphs if p.startswith(("\"", "“")))
    system = sum(1 for p in paragraphs if p.startswith("["))
    if first > third * 0.5:
        pov = "NGÔI 1 (người kể xưng 'tôi')"
    else:
        pov = "NGÔI 3"
    return {"pov": pov, "first": first, "third": third, "dialogue": dialogue,
            "system": system, "paragraphs": len(paragraphs),
            "first_label": "I/me/my", "third_label": "he/she", "system_label": "[ ]"}


def load_paragraphs(novel, rows, idxs):
    paras = []
    for idx in idxs:
        r = get_row(rows, idx)
        if r["trạng thái"] == "skip":
            continue
        paras.extend(raw_paragraphs(novel, r))
    return paras


def report(novel, paragraphs, min_count=1, show_all=False, lang=None):
    known = known_terms(novel)
    text = "\n".join(paragraphs)
    ja = (lang or raw_lang(novel, text)) == "ja"
    names, brackets = candidates_ja(paragraphs, known) if ja else candidates(paragraphs)

    def is_known(term):
        return term.lower() in known

    new_b = [(t, c) for t, c in brackets.most_common() if c >= min_count and not is_known(t)]
    new_n = [(t, c) for t, c in names.most_common() if c >= min_count and not is_known(t)]

    print("== Trong 【】『』《》 (kỹ năng / danh hiệu / vật phẩm / thông báo) — CHƯA có ==" if ja else
          "== Trong [ ] (kỹ năng / danh hiệu / vật phẩm / thông báo) — CHƯA có ==")
    print("\n".join(f"  {c:>3}  [{t}]" for t, c in new_b) or "  (không có)")
    print("\n== Katakana / kanji trước kính ngữ — CHƯA có ==" if ja else "\n== Tên riêng / cụm viết hoa — CHƯA có ==")
    print("\n".join(f"  {c:>3}  {t}" for t, c in new_n) or "  (không có)")

    if show_all:
        seen = {}
        for e in known.values():
            if any(contains(text, t) for t in [e["en"], *e["aliases"]]):
                seen[e["en"]] = e["vi"]
        print("\n== Đã có trong context và xuất hiện ở đây ==")
        print("\n".join(f"  {en} -> {vi or '(chưa có bản dịch)'}" for en, vi in sorted(seen.items())) or "  (không có)")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("range")
    ap.add_argument("--min", type=int, default=1, help="chỉ in từ xuất hiện >= N lần")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    novel = load_novel(args.slug)
    rows = load_progress(novel)
    paras = load_paragraphs(novel, rows, parse_range(args.range))
    lang = raw_lang(novel, "\n".join(paras))
    h = pov_hint(paras, lang)
    print(f"Góc nhìn (ước lượng): {h['pov']} — {h['first_label']} ngoài thoại: {h['first']}, "
          f"{h['third_label']} ngoài thoại: {h['third']}")
    print(f"Đoạn: {h['paragraphs']} · đoạn thoại: {h['dialogue']} · đoạn {h['system_label']}: {h['system']}\n")
    report(novel, paras, args.min, args.all, lang)


if __name__ == "__main__":
    main()
