---
name: novel-translate
description: Dịch truyện (webnovel) từ raw tiếng Anh hoặc tiếng Nhật sang tiếng Việt theo từng chương, giữ nhất quán tên nhân vật, xưng hô, thuật ngữ, tên kỹ năng và văn phong qua các file context. Dùng khi user bảo "dịch chương N", "dịch tiếp", "dịch 5 chương", "khởi tạo truyện mới để dịch", "cập nhật glossary/nhân vật", hoặc nhắc tới thư mục translations/.
---

# Dịch truyện theo chương

Mỗi truyện có một thư mục `translations/<slug>/`. Các script nằm ở `.agents/skills/novel-translate/scripts/`, đường dẫn tính từ repo root, chỉ dùng thư viện chuẩn Python, chạy được cả bash lẫn PowerShell:

```
python .agents/skills/novel-translate/scripts/<script>.py <slug> ...
```

Các script đã được kiểm thử. Gọi thẳng theo cú pháp bên dưới, không đọc mã. Chỉ khi script báo lỗi mới đọc thông báo và xử lý.

## Cấu trúc thư mục

```
translations/<slug>/
  novel.json            # tên truyện, đường dẫn raw, raw_ignore_lines (dòng raw không phải truyện, script bỏ qua khi đếm đoạn),
                        # layout, raw_lang, arc_rule (xem "Layout của truyện")
  progress.md           # bảng tiến độ (todo/done/reviewed/skip); layout 1 có thêm "Cần user xác nhận" + "Đã quyết"
  questions.md          # (layout 2) câu hỏi chờ quyết
  decisions/            # (layout 2) câu đã quyết, mỗi file một khoảng 100 chương: 0001-0100.md...
  context/
    rules.md            # quy tắc cứng: tên riêng, thuật ngữ, định dạng, T/N. Ưu tiên cao nhất
    style.md            # góc nhìn, giọng kể, nguyên tắc văn phong, bảng cảm thán
    characters.md       # bảng nhân vật (EN | Alias | VI) + tính cách, cách nói chuyện
    pronouns.md         # người kể gọi nhân vật + xưng hô từng cặp, có mốc chương
    glossary.md         # thuật ngữ, kỹ năng, danh hiệu, vật phẩm, địa danh
    summaries.md        # (layout 1) tóm tắt 3–5 dòng mỗi chương
    summaries/arc-NNN.md  # (layout 2) tóm tắt arc + tóm tắt từng chương của arc đó
    story-so-far.md     # (layout 2) toàn bộ câu chuyện tới giờ, tối đa 6000 ký tự, viết lại sau mỗi arc
  vi/Chapter_001.md     # bản dịch, đánh số theo cột # của progress.md
  vi/images/            # ảnh nhúng trong chương (mục E), vd ch012-ban-do-tang-1.webp
```

## Layout của truyện

Xem `"layout"` trong `novel.json`. Không có khoá này là layout 1.

- **Layout 1** (truyện cũ, vd `the-unwanted-undead-adventurer`): làm như các bước bên dưới, đọc và sửa thẳng các file context; câu hỏi ghi vào `## Cần user xác nhận` trong `progress.md`.
- **Layout 2** (Legend trở đi và mọi truyện khởi tạo mới): truyện dài hàng nghìn chương, context rất lớn. **Không Read/Edit** `characters.md`, `glossary.md`, `pronouns.md`, `summaries/`, `story-so-far.md`, `questions.md`, `decisions/`. Tra và ghi bằng `ctx.py` (bảng dưới) và `progress.py ask`. Lệnh ghi tự kiểm tra trùng, ký tự `|`, tên xưng hô không có trong `characters.md`...; phạm lỗi thì không ghi gì và in lý do, sửa theo lý do đó. Chỉ khi cần một thay đổi mà không lệnh nào làm được (gộp hai dòng trùng, xoá một dòng sai) mới mở file, và chỉ sửa đúng chỗ đó. `rules.md`, `style.md` vẫn đọc và sửa thẳng như cũ.

```
python .agents/skills/novel-translate/scripts/ctx.py <slug> <lệnh> ...
```

| Lệnh | Việc |
|---|---|
| `find <từ>` | tìm theo EN / Alias / VI (chuỗi con) trong glossary + characters, kể cả mục "Đã loại" |
| `show-char <tên>` | dòng bảng + mục chi tiết của một nhân vật (tên là EN, Alias hoặc VI; một phần tên cũng được nếu chỉ khớp một nhân vật, áp dụng cho mọi lệnh nhận tên) |
| `pronouns <tên> [<tên 2>]` | mọi dòng xưng hô liên quan tới nhân vật, hoặc của một cặp |
| `show-summaries <range>` | tóm tắt các chương |
| `arc [N]` | arc chứa chương N; bỏ N thì in các arc đã xong mà thiếu tóm tắt |
| `add-term --en X [--alias "a; b"] --vi Y --kind <loại> --ch N [--note ...]` | thêm thuật ngữ vào glossary (`--force` khi trùng VI với mục khác mà thật sự là hai thứ khác nhau) |
| `add-char --en X [--alias ...] --vi Y --role ... --ch N [--detail "..."]...` | thêm nhân vật; mỗi `--detail` là một dòng của mục chi tiết |
| `char-note <tên> "..."` | thêm một dòng vào mục chi tiết của nhân vật (tạo mục nếu chưa có) |
| `add-alias <tên/thuật ngữ> "<alias>"` | thêm alias cho một mục đã có |
| `set <glossary\|characters> <tên> <cột> "<giá trị>"` | đổi một ô (vd `vai trò`, `ghi chú`, `loại`); không đổi được EN/Alias |
| `add-narrator <tên> "<người kể gọi>" N ["ghi chú"]` | thêm dòng "người kể gọi nhân vật" |
| `add-pronoun <A> <B\|*> "<A xưng>" "<A gọi B>" N ["ghi chú"]` | thêm dòng xưng hô một chiều A → B |
| `add-summary N "..."` | ghi tóm tắt chương N vào đúng file arc (`--replace` để ghi đè) |
| `set-arc-summary <arc> "..."` / `set-story <arc> --file F` | mục F |

Nội dung có dấu `"` hay dài thì ghi vào một file UTF-8 trong `.herdr/` (hoặc thư mục tạm) rồi truyền `--file <file>` (có ở `char-note`, `add-summary`, `set-arc-summary`, `set-story`, `progress.py ask`).

### Raw tiếng Nhật

`novel.json` có `"raw_lang": "ja"` (không có thì script tự đoán). Khác với raw tiếng Anh:
- `characters.md`: cột `EN` là **tên khoá viết Latin** (romaji hoặc tên chính thức, thường trùng `VI`), `pronouns.md` tham chiếu tới giá trị này. **Mọi** cách viết tiếng Nhật của nhân vật (`レイ; 佐伯玲二; 玲二`) ghi ở `Alias`, vì script dò tên trong raw theo các chữ này.
- `glossary.md`: cột `EN` là dạng chuẩn trong raw (tiếng Nhật, vd `魔獣術`), cách viết khác (`死神の大鎌` cho `デスサイズ`) ghi ở `Alias`.
- Script tìm tên tiếng Nhật theo chuỗi con, riêng tên katakana không khớp khi dính liền katakana khác (`レイ` không khớp trong `スレイプニル`).
- `prepare.py` và `extract_terms.py` liệt kê thuật ngữ mới là cụm katakana, nội dung `【】『』《》` và kanji đứng trước kính ngữ (`さん`, `様`, `殿`...). Danh sách lẫn từ thường (đồ vật, từ mượn): chỉ thêm tên riêng và thuật ngữ cố định.
- Độ dài tính bằng ký tự. QA cảnh báo đoạn dịch còn sót chữ Nhật.
- Raw hay gọi nhân vật bằng tên ngắn (`タクム` cho `タクム・スズノセ`). Bản dịch dùng một chữ trong tên VI (`Takumu`) là được, QA không cảnh báo.

File chương được app Novel Reader đọc **theo từng dòng, không render Markdown** (chi tiết: `chapter-image-guide.md` ở repo root):
- dòng có chữ đầu tiên `# ...` là tiêu đề; dòng trống bị bỏ qua;
- dòng điều hướng `[<chữ>](Chapter_<số>.md)`, nhiều link ngăn bằng ` | `, bị bỏ qua. Sai định dạng thì app hiện nó như một đoạn văn;
- dòng chỉ gồm đúng một `![chú thích](đường dẫn)` là một khối ảnh;
- mọi dòng khác là một đoạn văn, hiển thị nguyên từng ký tự: `*`, `_` không thành in đậm/in nghiêng, `[...]` không phải link.

Các bảng trong context được script đọc. Giữ đúng tên cột, mỗi dòng một mục, không thêm `|` trong ô.

## A. Khởi tạo truyện mới (một lần)

1. Chạy:
   ```
   python .agents/skills/novel-translate/scripts/init_novel.py --raw "<thư mục raw>" --slug <slug> --title "<tên truyện>"
   ```
   Raw phải có dạng `Chapter_XXX - <tiêu đề>.txt`. Script đánh dấu `skip` các chương nghi trùng (cùng tiêu đề). Mở raw các cặp đó, đối chiếu vài đoạn để xác nhận trùng thật; không trùng thì sửa lại `todo`.
   Truyện mới luôn là layout 2. Script ghi vào `novel.json` các khoá `raw_lang` (`en`/`ja`, đoán từ raw) và `arc_rule`, rồi in ra. Kiểm tra `arc_rule`: `pattern` là regex lấy tên arc (group 1) từ cột `Tiêu đề` của `progress.md`, `max` là số chương tối đa một arc (arc dài hơn bị chia thành nhiều phần). Tiêu đề raw không có tên arc thì để không có `pattern`: cứ `max` chương là một arc.
2. Dựng context ban đầu:
   ```
   python .agents/skills/novel-translate/scripts/extract_terms.py <slug> 1-15 --min 2
   ```
   Đọc lướt 3–5 chương đầu, rồi điền: `style.md` (thể loại, góc nhìn, giọng kể), `characters.md` (nhân vật chính và tính cách), `pronouns.md` (người kể gọi nhân vật chính là gì, xưng hô các cặp chính), `glossary.md` (thuật ngữ xuất hiện nhiều). Lúc này các file còn nhỏ nên điền thẳng được; layout 2 cũng có thể dùng các lệnh `ctx.py add-*`.
3. Báo user các quyết định quan trọng (đại từ người kể dùng cho nhân vật chính, xưng hô các cặp chính, 10–20 thuật ngữ chính) và chờ duyệt trước khi dịch chương đầu tiên.

## B. Dịch một chương

Làm đủ 5 bước cho từng chương. Dịch nhiều chương thì làm **tuần tự** từng chương một, xong bước 5 của chương này mới sang chương sau. Không dịch song song nhiều chương, vì chương sau dùng context do chương trước cập nhật.

### Bước 1 — Chuẩn bị

```
python .agents/skills/novel-translate/scripts/prepare.py <slug> [N]
```

Bỏ `N` thì script lấy chương `todo` kế tiếp. Output gồm: đường dẫn raw và file bản dịch, góc nhìn ước lượng, nhân vật đã biết xuất hiện kèm xưng hô liên quan, thuật ngữ **chưa có** trong context, mạch truyện. Mạch truyện ở layout 1 là tóm tắt 3 chương trước; ở layout 2 là `story-so-far`, tóm tắt 2 arc trước và tóm tắt các chương đã dịch của arc hiện tại.

Sau đó:

1. Đọc `rules.md` và `style.md`. Đọc mục chi tiết trong `characters.md` của các nhân vật script liệt kê (layout 2: `ctx.py <slug> show-char <tên>` cho từng nhân vật).
2. Đọc toàn bộ raw của chương.
3. **Thuật ngữ mới**: với mỗi mục script liệt kê là tên riêng/kỹ năng thật (bỏ qua từ thường bị bắt nhầm), chốt bản dịch theo `rules.md` và thêm vào `glossary.md` hoặc `characters.md` **trước khi dịch** (layout 2: `ctx.py find` để kiểm tra đã có mục cùng nghĩa chưa, rồi `add-term` / `add-char` / `add-alias`). Tên chưa chắc là ai, hoặc là cách viết khác của tên đã có, thì thêm vào cột Alias của mục cũ. Alias chỉ ghi cách viết tiếng Anh khác **dịch ra đúng chữ ở cột VI** (lỗi chính tả, viết hoa/thường khác); biệt danh, tên gọi tắt hay tước vị dịch thành chữ khác thì thêm **dòng riêng**, và không đưa từ đơn chung (`Normal`, `Princess`...) vào Alias vì QA sẽ báo sai ở mọi chương có từ đó. Mục nằm trong `## Đã loại (không thêm lại)` ở đầu `glossary.md` thì **không thêm lại**, cứ dịch tự nhiên theo ngữ cảnh.
4. **Góc nhìn và xưng hô**: xác nhận góc nhìn của chương (có chương đổi sang góc nhìn nhân vật khác). Với mỗi cặp nhân vật có hội thoại mà `pronouns.md` chưa có, quyết định xưng hô dựa trên tuổi, địa vị, quan hệ, tính cách và ghi vào `pronouns.md` (layout 2: `ctx.py add-pronoun` / `add-narrator`; cần xem lịch sử xưng hô của một nhân vật thì `ctx.py pronouns <tên>`).
5. **Mạch truyện**: đọc tóm tắt script in ra. Chương mở đầu nối tiếp cảnh của chương trước (cùng arc, cảnh chưa kết thúc) thì đọc phần cuối bản dịch liền trước để giữ giọng và chi tiết. Chương nhắc lại chi tiết cũ mà tóm tắt không đủ thì đọc thêm bản dịch của 2–3 chương trước đó. Chưa có chương nào đã dịch thì bỏ qua.

### Bước 2 — Dịch

Ghi vào file bản dịch script đã in ra (`translations/<slug>/vi/Chapter_NNN.md`).

- Dòng đầu: `# Chương N: <tiêu đề dịch>`, rồi một dòng trống.
- Dịch **đủ từng đoạn**, theo đúng thứ tự. Mỗi đoạn raw thành một đoạn dịch **trên một dòng**, cách nhau dòng trống. Không ngắt một đoạn ra nhiều dòng. Không tóm tắt, không bỏ câu, không thêm nội dung.
- Không tự thêm ảnh ngoài raw. Raw hoặc file chương đã có dòng ảnh (`![...](images/...)`) thì giữ nguyên dòng đó và vị trí tương ứng của nó giữa các đoạn dịch.
- Bỏ ghi chú translator (T/N) của raw. T/N kẹp trong câu thì chỉ bỏ phần ghi chú, vẫn dịch phần truyện của câu đó.
- Quyết định bỏ hẳn một dòng raw không phải truyện (vd bảng chú giải ký hiệu của bản EN) thì ghi lý do vào `rules.md` và thêm nguyên văn dòng đó vào `raw_ignore_lines` trong `novel.json`, để QA không báo thiếu đoạn.
- Theo `rules.md` (tên, thuật ngữ, định dạng) và `style.md` (giọng văn). Đọc `natural-vietnamese.md` (cùng thư mục với skill này) trước khi dịch: viết tiếng Việt tự nhiên ngay từ bản đầu, không dịch bám chữ rồi để sửa sau. Mỗi lời thoại phải đúng xưng hô trong `pronouns.md` cho cặp người nói/người nghe ở thời điểm của chương.
- Chương dài thì ghi file theo nhiều phần nối tiếp, nhưng mỗi phần vẫn dịch đủ.

### Bước 3 — QA

```
python .agents/skills/novel-translate/scripts/qa_check.py <slug> N
```

- `[LỖI]` thì bắt buộc sửa rồi chạy lại. Lệch số đoạn theo hướng thiếu nghĩa là gần như chắc chắn đã bỏ sót: đối chiếu từng đoạn với raw để tìm chỗ thiếu. `qa_check.py <slug> N --side` in từng cặp đoạn raw / bản dịch theo đúng cách QA đếm (đã bỏ tiêu đề, T/N, ảnh), chỗ hai bên bắt đầu lệch nghĩa là chỗ sót hoặc gộp. Không tự viết code đếm đoạn.
- `[cảnh báo]` thì xem từng cái. Sửa những cái là lỗi thật; cái nào là báo nhầm (ví dụ thuật ngữ được diễn đạt lại hợp lý) thì bỏ qua.

Sau khi script sạch, tự đọc lại bản dịch một lượt và kiểm tra:
- đại từ người kể dùng cho từng nhân vật có nhất quán không;
- xưng hô trong mọi lời thoại có đúng cặp và đúng thời điểm không;
- có câu nào còn văn dịch máy, cứng, sai nghĩa không, soát theo `natural-vietnamese.md`;
- câu đùa có còn buồn cười không.

### Bước 4 — Cập nhật context

Xem lại chương vừa dịch và cập nhật. Layout 2 dùng lệnh `ctx.py` ghi ở từng mục, không mở file.

- `summaries.md`: **bắt buộc**, thêm mục `## N` gồm 3–5 dòng: diễn biến chính, nhân vật/kỹ năng mới, cảnh kết thúc (layout 2: `ctx.py add-summary N --file <file>`, script tự ghi vào đúng file arc).
- `characters.md`: nhân vật mới; tính cách hoặc cách nói chuyện mới lộ ra; thay đổi lớn về trạng thái hay quan hệ (ghi "tính đến chương N"). Nhân vật lộ tên thật sau một thời gian chỉ được gọi bằng biệt danh thì **thêm dòng riêng** cho tên thật, giữ dòng biệt danh, và ghi chú liên kết hai dòng. Không nhét tên thật vào Alias của dòng biệt danh. (Layout 2: `add-char`, `char-note`, `set characters <tên> "vai trò" ...`.)
- `pronouns.md`: cặp xưng hô mới dùng trong chương. Quan hệ thay đổi (thân hơn, trở mặt, lộ thân phận) thì **thêm dòng mới** với `Từ chương` = N, không sửa dòng cũ. Tên trong cột `A`, `B`, `Nhân vật` phải đúng giá trị cột `EN` của một dòng trong `characters.md`. Không thêm đám đông hay vật phẩm. (Layout 2: `add-pronoun` / `add-narrator`; truyền EN, Alias hay VI đều được, script tự đổi về EN.)
- `glossary.md`: thuật ngữ đã thêm ở bước 1 mà còn thiếu loại hoặc ghi chú. Chỉ thêm tên riêng và thuật ngữ cố định, không thêm cụm miêu tả chung (vd "black leopard" chỉ để tả một con báo đen). Cột `VI` chỉ ghi **một** bản dịch. Không ghi hai dạng ngăn bằng `/`: tên gọi tắt (vd `Thunderhammer` của một vũ khí tên dài) là một dòng riêng. Trước khi thêm dòng mới, tìm cột VI xem đã có mục cùng nghĩa chưa (vd `God of blacksmithing` và `God of Smithing`); có rồi thì thêm vào Alias của mục đó. (Layout 2: `find`, `add-term`, `add-alias`, `set glossary <thuật ngữ> "ghi chú" ...`.)
- `style.md`: đặc điểm giọng kể mới đáng giữ; cảm thán mới vào bảng cảm thán.
- `rules.md`, mục "Riêng truyện này": trường hợp mới cần xử lý thống nhất về sau.

Cập nhật xong thì chạy `python .agents/skills/novel-translate/scripts/lint_context.py <slug>` và sửa hết `[LỖI]`.

**Không tự ghi đè quyết định cũ.** Thấy một thuật ngữ, tên hay xưng hô đã chốt có vẻ sai, hoặc mâu thuẫn với raw chương mới:
1. giữ nguyên cách cũ trong bản dịch;
2. ghi câu hỏi gồm số chương, vấn đề và đề xuất. Layout 2: `python .agents/skills/novel-translate/scripts/progress.py <slug> ask N "<vấn đề> — đề xuất <...>"`. Layout 1: ghi vào mục `## Cần user xác nhận` **đã có** trong `progress.md` (nằm ngay trên mục `## Đã quyết`, không phải cuối file; không tạo mục mới);
3. báo user ở cuối lượt.

### Bước 5 — Đánh dấu xong

```
python .agents/skills/novel-translate/scripts/progress.py <slug> set N done
```

### Sau khi dịch xong lượt — cập nhật `index.json`

Dịch xong mọi chương của lượt (hoặc sau mục D), chạy từ repo root:

```
python scripts/build_index.py
```

Script ghi lại `index.json` ở gốc repo (danh sách truyện và chương cho app đọc, spec ở `index-json-spec.md`). Thoát với `[LỖI]` (trùng số chương, `novel.json` sai JSON, dòng ảnh sai theo mục E...) thì sửa đúng file được nêu rồi chạy lại. `[cảnh báo] ... chưa git add` là bình thường khi chưa stage: khi commit thì commit `index.json` **cùng lúc** với các chương đó để `sha` khớp. Đã `git add` chương thì chạy lại script trước khi commit.

Chạy dưới orchestrator thì **bỏ qua** bước này: orchestrator tự sinh `index.json` lúc commit.

## C. Review một loạt chương (chỉ đọc)

Dùng khi được giao review, thường là 3 chương vừa dịch. **Không sửa file bản dịch hay file context.** Kết quả duy nhất là báo cáo.

1. Đọc `rules.md`, `style.md`, `pronouns.md`, cùng các mục liên quan trong `characters.md` và `glossary.md`. Đọc `natural-vietnamese.md` (cùng thư mục với skill này). Layout 2: không đọc trọn `pronouns.md`, `characters.md`, `glossary.md`; thay vào đó chạy `prepare.py <slug> N` cho từng chương được giao (chỉ đọc, in nhân vật, xưng hô và thuật ngữ liên quan), cần thêm thì dùng `ctx.py pronouns`, `show-char`, `find`.
2. Với từng chương, đối chiếu **từng đoạn** bản dịch với raw (đoạn K của bản dịch ứng với đoạn K của raw sau khi bỏ tiêu đề và T/N). Tìm:
   - sai nghĩa, bỏ sót hoặc thêm thắt nội dung;
   - sai xưng hô (sai cặp, sai thời điểm, lệch giữa các chương);
   - đại từ người kể dùng cho nhân vật không nhất quán;
   - thuật ngữ hoặc tên lệch với glossary/characters, hay lệch nhau giữa 3 chương;
   - câu văn dịch máy, cứng, khó đọc, phạm các lỗi trong `natural-vietnamese.md`; câu đùa mất duyên;
   - vi phạm định dạng trong `rules.md`.
3. Chạy `qa_check.py <slug> <range>` và đưa các cảnh báo đáng chú ý vào báo cáo.
4. Báo cáo theo đúng mẫu sau, mỗi lỗi một dòng, trích nguyên văn đủ để tìm được chỗ cần sửa. Phần `hiện tại` phải **chép y nguyên** từ file bản dịch, không tóm tắt, không bỏ vế. Phần `đề xuất` chỉ thay đúng đoạn được trích, để người sửa thay thế mà không làm mất chữ xung quanh (nhất là thuật ngữ trong glossary):

```
## Chương N
- [nặng|vừa|nhẹ] đoạn K — <loại lỗi>: <mô tả> | hiện tại: "<trích bản dịch>" | đề xuất: "<câu sửa>"

## Đề xuất cập nhật context
- <file>: <thêm/sửa gì> — lý do

## Câu hỏi
- <điều cần người quyết>
```

`nặng` là sai nghĩa, bỏ sót, sai xưng hô hay sai thuật ngữ. `vừa` là câu cứng hoặc khó hiểu. `nhẹ` là chuyện câu chữ nhỏ. Chương không có lỗi thì ghi `- Không có lỗi.`

## D. Sửa theo kết quả review

Dùng khi được giao file báo cáo review kèm file quyết định của orchestrator.

1. Đọc file quyết định trước. Chỉ sửa các mục được **chấp nhận**, và mục nào orchestrator ghi lại cách sửa thì sửa theo cách đó. Mục bị bác thì bỏ qua.
2. Sửa thẳng trong `vi/Chapter_NNN.md`, không đụng vào dòng ảnh và dòng điều hướng. Một lỗi có cùng kiểu (cùng thuật ngữ, cùng cặp xưng hô) thì sửa hết mọi chỗ trong các chương được giao, không chỉ chỗ được chỉ ra.
3. Cập nhật context theo các đề xuất đã được chấp nhận (đúng quy tắc ở bước B4: không sửa dòng xưng hô cũ mà thêm dòng mới; layout 2 dùng `ctx.py`).
4. Chạy `qa_check.py <slug> <range>` cho đến khi hết `[LỖI]`.
5. Đánh dấu: `progress.py <slug> set <range> reviewed`. Nếu brief bảo giữ nguyên trạng thái thì bỏ qua bước này.
6. Báo cáo: số lỗi đã sửa trong từng chương, những thay đổi context, các mục không sửa được và lý do.

## E. Ảnh trong chương

Chỉ thêm, thay hay xoá ảnh khi user yêu cầu. Chi tiết và lý do: `chapter-image-guide.md` ở repo root.

1. **File ảnh** đặt trong `translations/<slug>/vi/images/`:
   - tên chữ thường, chỉ gồm `a-z`, `0-9`, `-`, có tiền tố số chương: `ch012-ban-do-tang-1.webp`;
   - định dạng `.webp` (nên dùng), `.png`, `.jpg`/`.jpeg`;
   - rộng tối đa 1600px, nên dưới 500KB.
2. **Dòng ảnh** trong chương: nằm riêng một dòng, có dòng trống trước và sau, cả dòng đúng dạng
   ```
   ![Bản đồ tầng 1 của Tháp](images/ch012-ban-do-tang-1.webp)
   ```
   - Đường dẫn tương đối tính từ file chương: không `/` ở đầu, không URL `http(s)://`, không chứa `)`, không có tiêu đề kiểu `"title"`.
   - Chú thích được để trống, không chứa `]`.
   - Không đặt ảnh lẫn trong đoạn văn, không dùng thẻ `<img>`.
   - Dòng ảnh không tính là đoạn dịch, nên `qa_check.py` không đếm nó.
3. **Không ghi đè ảnh đã push.** Muốn thay ảnh thì tạo file tên mới (vd thêm `-v2`) rồi sửa dòng `![..](..)` trong chương. Lý do: app chỉ tải lại chương khi sha của file `.md` đổi, ghi đè ảnh cùng tên thì app vẫn hiện ảnh cũ đã cache. GitHub Action chặn push có ảnh bị sửa. Chỉ xoá file ảnh khi không còn chương nào dùng.
4. Kiểm tra bằng `python scripts/build_index.py`: script báo `[LỖI] <file>:<dòng>` khi ảnh không tồn tại (kể cả sai chữ hoa/thường), sai đuôi file, đường dẫn tuyệt đối hoặc trỏ ra ngoài repo, hay khi một dòng có `![` mà không đúng dạng ở bước 2. Commit ảnh **cùng lúc** với chương dùng nó.

## F. Tóm tắt arc và story-so-far (chỉ layout 2)

Truyện dài không thể đưa tóm tắt mọi chương vào mỗi lần dịch. Layout 2 nén theo ba tầng: tóm tắt chương (bước B4), tóm tắt arc, và `story-so-far.md`. `prepare.py` chỉ in `story-so-far`, tóm tắt 2 arc trước và tóm tắt chương của arc hiện tại.

Arc chia theo `arc_rule` trong `novel.json` (mục A1), mỗi arc tối đa khoảng 20 chương. Arc gốc dài hơn bị chia thành nhiều phần, mỗi phần tính là một arc riêng. Xem arc của một chương bằng `ctx.py <slug> arc N`.

Khi mọi chương của một arc đã dịch xong (`orchestrate.py next` báo `action=arc-summary`, hoặc `ctx.py <slug> arc` liệt kê arc thiếu):

1. `ctx.py <slug> show-summaries <range của arc>`: đọc tóm tắt các chương. Chỉ đọc lại bản dịch khi tóm tắt không đủ để hiểu một diễn biến quan trọng.
2. Viết **tóm tắt arc** 5–10 dòng (tối đa 2000 ký tự): mục tiêu và diễn biến chính, kết quả, nhân vật mới quan trọng, thay đổi về quan hệ, sức mạnh, vật phẩm, địa điểm, và mạch còn dở chuyển sang arc sau. Ghi bằng `ctx.py <slug> set-arc-summary <arc> --file <file>`.
3. Đọc `story-so-far.md` hiện tại (file nhỏ, đọc trực tiếp được). Viết lại toàn bộ, tối đa 6000 ký tự, gồm ba phần:
   - `Bối cảnh`: thế giới, nhân vật chính, các mối quan hệ cốt lõi. Chỉ đổi khi có thay đổi lớn.
   - `Diễn biến`: các arc đã qua theo thứ tự thời gian. Arc càng cũ càng nén ngắn, nhiều arc cũ có thể gộp chung một câu. Giữ những chi tiết mà chương sau còn nhắc lại: lời hứa, kẻ thù còn sống, vật phẩm quan trọng, bí mật đã lộ.
   - `Đang dở`: các mạch chưa khép, mục tiêu hiện tại của nhân vật chính.

   Ghi bằng `ctx.py <slug> set-story <arc> --file <file>`. Lệnh từ chối khi file quá 6000 ký tự: nén các arc cũ lại rồi ghi lại.
4. Kiểm tra bằng `python .agents/skills/novel-orchestrator/scripts/orchestrate.py <slug> verify-arc <arc>`.

## Chạy dưới orchestrator

Brief có ghi "chế độ orchestrator" thì:

- Chỉ làm đúng việc và đúng chương được giao, rồi dừng. Không tự sang chương khác.
- Không chờ user. Chỗ nào skill bảo "báo user, chờ duyệt" (bước A3, mục "Cần user xác nhận") thì ghi đề xuất và câu hỏi vào báo cáo, chọn phương án hợp lý nhất để làm tiếp, rồi kết thúc lượt. Orchestrator sẽ quyết và sửa lại nếu cần.
- Không tạo file tạm hay file nháp trong repo, kể cả ở gốc repo. Cần file tạm (dump đoạn để đối chiếu, script tạm...) thì đặt trong `.herdr/` và xoá khi xong.
- Câu hỏi ghi trên **một dòng** `- [#N] ...`, không xuống dòng thành ý con (layout 2: `progress.py ask` tự gộp thành một dòng).
- Không chạy `git` (add, commit, push) và không chạy `scripts/build_index.py`. Orchestrator lo việc này; panel sửa file ngoài `translations/<slug>/` (kể cả `index.json`) sẽ bị orchestrator dừng vòng lặp.
- Câu hỏi vẫn được ghi lại (layout 2: `progress.py ask`; layout 1: mục "Cần user xác nhận" trong `progress.md`), đồng thời ghi vào mục "Câu hỏi" của báo cáo.

## Lệnh khác

```
python .agents/skills/novel-translate/scripts/progress.py <slug> next -n 5     # 5 chương todo kế tiếp
python .agents/skills/novel-translate/scripts/progress.py <slug> stats         # tổng tiến độ
python .agents/skills/novel-translate/scripts/progress.py <slug> set 290-292 skip --note "trùng #287-289"
python .agents/skills/novel-translate/scripts/extract_terms.py <slug> 40-60 --all   # soát thuật ngữ một đoạn truyện
python .agents/skills/novel-translate/scripts/qa_check.py <slug> 1-20          # QA lại một loạt chương
python .agents/skills/novel-translate/scripts/progress.py <slug> ask 42 "..."  # layout 2: ghi câu hỏi vào questions.md
python .agents/skills/novel-translate/scripts/ctx.py <slug> find <từ>          # layout 2: tra glossary + characters
```

## Báo cáo cuối lượt

Sau khi dịch xong một hoặc nhiều chương, báo ngắn gọn:
- những chương đã xong và kết quả QA;
- kết quả `build_index.py` (số truyện, số chương trong `index.json`), trừ khi chạy dưới orchestrator;
- thuật ngữ, nhân vật, xưng hô mới đã thêm, mỗi mục một dòng `EN → VI`;
- các mục mới trong "Cần user xác nhận", nếu có.
