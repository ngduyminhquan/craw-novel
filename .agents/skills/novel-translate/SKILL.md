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

File này đủ để **dịch một chương** (mục B). Việc khác thì đọc thêm đúng file tương ứng trong `.agents/skills/novel-translate/docs/`:

| Việc | Đọc thêm |
|---|---|
| Khởi tạo truyện mới | `docs/init.md` |
| Review một loạt chương | `docs/review.md` |
| Sửa theo kết quả review | `docs/fix.md` |
| Tóm tắt arc, viết lại story-so-far | `docs/arc-summary.md` |
| Thêm, thay, xoá ảnh trong chương | `docs/images.md` |
| Truyện layout 1 (`novel.json` không có `"layout": 2`) | `docs/layout1.md` |

## Cấu trúc thư mục

```
translations/<slug>/
  novel.json            # tên truyện, raw_dir, layout, raw_lang, arc_rule, raw_ignore_lines
  progress.md           # bảng tiến độ (todo/done/reviewed/skip)
  questions.md          # câu hỏi chờ quyết
  decisions/            # câu đã quyết, mỗi file một khoảng 100 chương
  context/
    rules.md            # quy tắc cứng: tên riêng, thuật ngữ, định dạng, T/N. Ưu tiên cao nhất
    style.md            # góc nhìn, giọng kể, nguyên tắc văn phong, bảng cảm thán
    characters.md       # bảng nhân vật (EN | Alias | VI) + mục chi tiết tính cách, cách nói chuyện
    pronouns.md         # người kể gọi nhân vật + xưng hô từng cặp, có mốc chương
    glossary.md         # thuật ngữ, kỹ năng, danh hiệu, vật phẩm, địa danh
    summaries/arc-NNN.md  # tóm tắt arc + tóm tắt từng chương của arc đó
    story-so-far.md     # toàn bộ câu chuyện tới giờ, tối đa 6000 ký tự
  vi/Chapter_001.md     # bản dịch, đánh số theo cột # của progress.md
```

## Layout của truyện

Truyện layout 2 (`novel.json` có `"layout": 2`, gồm Legend trở đi và mọi truyện khởi tạo mới) dài hàng nghìn chương, context rất lớn:

- **Không Read/Edit** `characters.md`, `glossary.md`, `pronouns.md`, `summaries/`, `story-so-far.md`, `questions.md`, `decisions/`. Tra và ghi bằng `ctx.py` (bảng dưới) và `progress.py ask`. Lệnh ghi tự kiểm tra trùng, ký tự `|`, tên xưng hô không có trong `characters.md`...; phạm lỗi thì không ghi gì và in lý do, sửa theo lý do đó. Chỉ khi cần một thay đổi mà không lệnh nào làm được (gộp hai dòng trùng, xoá một dòng sai) mới mở file, và chỉ sửa đúng chỗ đó.
- **Không đọc trọn `progress.md`** (hàng nghìn dòng). Xem tiến độ bằng `progress.py <slug> stats` / `next`, đổi trạng thái bằng `progress.py <slug> set`.
- `rules.md`, `style.md` vẫn đọc và sửa thẳng.

Truyện layout 1 thì đọc thêm `docs/layout1.md`.

```
python .agents/skills/novel-translate/scripts/ctx.py <slug> <lệnh> ...
```

| Lệnh | Việc |
|---|---|
| `find <từ>` | tìm theo EN / Alias / VI (chuỗi con) trong glossary + characters, kể cả mục "Đã loại" |
| `show-char <tên>` | dòng bảng + mục chi tiết của một nhân vật. Mọi lệnh nhận tên đều nhận EN, Alias, VI, hoặc một phần tên nếu chỉ khớp một mục |
| `pronouns <tên> [<tên 2>]` | mọi dòng xưng hô liên quan tới nhân vật, hoặc của một cặp |
| `show-summaries <range>` | tóm tắt các chương |
| `grep <chuỗi/regex> [--raw] [--range A-B] [--max 40]` | tìm trong các bản dịch đã có của truyện này (thêm `--raw` để tìm trong raw), để giữ cách dịch nhất quán (tiêu đề arc: `grep "^# Chương"`, tiếng kêu, cách gọi một vật...). Dùng lệnh này thay cho `git grep` hay tự viết code |
| `arc [N]` | arc chứa chương N; bỏ N thì in các arc đã xong mà thiếu tóm tắt |
| `add-term --en X [--alias "a; b"] --vi Y --kind <loại> --ch N [--note ...]` | thêm thuật ngữ vào glossary (`--force` khi trùng VI với mục khác mà thật sự là hai thứ khác nhau). `<loại>`: `kỹ năng`, `danh hiệu`, `chức nghiệp`, `cấp bậc`, `vật phẩm`, `địa danh`, `tổ chức`, `chủng tộc`, `quái vật`, `hệ thống`, `khác` |
| `add-char --en X [--alias ...] --vi Y --role ... --ch N [--detail "..."]...` | thêm nhân vật; mỗi `--detail` là một dòng của mục chi tiết |
| `char-note <tên> "..." [--replace <nhãn>]` | thêm một dòng vào mục chi tiết của nhân vật. `--replace "Kỹ năng"` thay dòng đang bắt đầu bằng `Kỹ năng:` thay vì thêm dòng mới |
| `add-alias <tên/thuật ngữ> "<alias>"` | thêm alias cho một mục đã có |
| `set <glossary\|characters> <tên> <cột> "<giá trị>"` | đổi một ô (vd `vai trò`, `ghi chú`, `loại`); không đổi được EN/Alias |
| `add-narrator <tên> "<người kể gọi>" N ["ghi chú"]` | thêm dòng "người kể gọi nhân vật" |
| `add-pronoun <A> <B\|*> "<A xưng>" "<A gọi B>" N ["ghi chú"]` | thêm dòng xưng hô một chiều A → B |
| `add-summary N "..."` | ghi tóm tắt chương N vào đúng file arc (`--replace` để ghi đè) |

Nội dung dài hay có dấu `"` thì ghi vào một file UTF-8 trong `.herdr/` rồi truyền `--file <file>` (có ở `char-note`, `add-summary`, `set-arc-summary`, `set-story`, `progress.py ask`). Ghi file đó bằng công cụ ghi file của agent, không dùng `python -c` hay `echo` (PowerShell làm hỏng dấu nháy và xuống dòng). Xong thì xoá file tạm. Chuỗi ngắn truyền thẳng (`--vi`, `--note`, `--role`...) thì không đặt dấu `"` bên trong chuỗi, cần trích thì dùng `'...'`: PowerShell 5.1 tách chuỗi có `"` lồng thành nhiều tham số.

### Raw tiếng Nhật

`novel.json` có `"raw_lang": "ja"`. Khác với raw tiếng Anh:
- `characters.md`: cột `EN` là **tên khoá viết Latin** (romaji hoặc tên chính thức, thường trùng `VI`), `pronouns.md` tham chiếu tới giá trị này. **Mọi** cách viết tiếng Nhật của nhân vật (`レイ; 佐伯玲二; 玲二`) ghi ở `Alias`, vì script dò tên trong raw theo các chữ này.
- `glossary.md`: cột `EN` là dạng chuẩn trong raw (tiếng Nhật, vd `魔獣術`), cách viết khác (`死神の大鎌` cho `デスサイズ`) ghi ở `Alias`.
- Tên katakana không khớp khi dính liền katakana khác (`レイ` không khớp trong `スレイプニル`).
- Thuật ngữ mới script liệt kê là cụm katakana, nội dung `【】『』《》` và kanji đứng trước kính ngữ; danh sách lẫn từ thường (đồ vật, từ mượn), chỉ thêm tên riêng và thuật ngữ cố định.
- Raw hay gọi nhân vật bằng tên ngắn (`タクム` cho `タクム・スズノセ`): bản dịch dùng một chữ trong tên VI (`Takumu`) là được.
- QA báo đoạn dịch còn sót chữ Nhật, ký tự lạ (Kirin, Thái...), và thuật ngữ viết hoa khác glossary.

## B. Dịch một chương

Làm đủ 5 bước cho từng chương. Dịch nhiều chương thì làm **tuần tự** từng chương một, xong bước 5 của chương này mới sang chương sau, vì chương sau dùng context do chương trước cập nhật.

### Bước 1 — Chuẩn bị

```
python .agents/skills/novel-translate/scripts/prepare.py <slug> [N]
```

Bỏ `N` thì script lấy chương `todo` kế tiếp. Output gồm: đường dẫn raw và file bản dịch, góc nhìn ước lượng, nhân vật đã biết xuất hiện kèm xưng hô liên quan, thuật ngữ đã có và **chưa có** trong context, mạch truyện (`story-so-far`, tóm tắt 2 arc trước, tóm tắt các chương đã dịch của arc hiện tại).

Sau đó:

1. Đọc `rules.md`, `style.md` và `.agents/skills/novel-translate/natural-vietnamese.md`. Với mỗi nhân vật script liệt kê, `ctx.py <slug> show-char <tên>` để đọc mục chi tiết (tính cách, cách nói chuyện).
2. Đọc toàn bộ raw của chương. Cần raw theo từng đoạn đánh số (để dịch đủ, đối chiếu số đoạn) thì dùng `qa_check.py <slug> N --side --full` (nguyên văn từng đoạn; thêm `--paras 40-80` để chỉ in một khoảng): chưa có bản dịch thì cột VI để trống, dịch xong chạy lại `--side` (bản rút gọn) để so từng cặp. Không tự viết code Python đọc raw hay đếm đoạn.
3. **Thuật ngữ mới**: với mỗi mục script liệt kê là tên riêng/kỹ năng thật (bỏ qua từ thường bị bắt nhầm), chốt bản dịch theo `rules.md` và thêm vào context **trước khi dịch**: `ctx.py find` để kiểm tra đã có mục cùng nghĩa chưa, rồi `add-term` / `add-char` / `add-alias`. Cách viết khác của tên đã có thì thêm vào Alias của mục cũ, nhưng Alias chỉ ghi cách viết trong raw **dịch ra đúng chữ ở cột VI**; biệt danh, tên gọi tắt hay tước vị dịch thành chữ khác thì thêm **dòng riêng**, và không đưa từ đơn chung vào Alias vì QA sẽ báo sai ở mọi chương có từ đó. Mục nằm trong `## Đã loại` của glossary (lệnh sẽ báo) thì **không thêm lại**, cứ dịch tự nhiên theo ngữ cảnh.
4. **Góc nhìn và xưng hô**: xác nhận góc nhìn của chương (có chương đổi sang góc nhìn nhân vật khác). Với mỗi cặp nhân vật có hội thoại mà chưa có xưng hô, quyết định dựa trên tuổi, địa vị, quan hệ, tính cách và ghi bằng `ctx.py add-pronoun` / `add-narrator`. Cần xem lịch sử xưng hô của một nhân vật thì `ctx.py pronouns <tên>`.
5. **Mạch truyện**: đọc phần mạch truyện script in ra. Chương mở đầu nối tiếp cảnh của chương trước (cùng arc, cảnh chưa kết thúc) thì đọc **phần cuối** bản dịch liền trước để giữ giọng và chi tiết. Chương nhắc lại chi tiết cũ mà tóm tắt không đủ thì đọc thêm bản dịch của 2–3 chương trước đó. Cần biết chương trước đã dịch một chữ, một tiếng kêu, một tiêu đề thế nào thì `ctx.py <slug> grep "<chuỗi>"`.

### Bước 2 — Dịch

Ghi vào file bản dịch script đã in ra (`translations/<slug>/vi/Chapter_NNN.md`). File được app Novel Reader đọc **theo từng dòng, không render Markdown**:

- Dòng đầu: `# Chương N: <tiêu đề dịch>`, rồi một dòng trống. Dịch tiêu đề cùng cách với các chương cùng arc trước đó.
- Dịch **đủ từng đoạn**, theo đúng thứ tự. Mỗi đoạn raw thành một đoạn dịch **trên một dòng**, cách nhau dòng trống. Không ngắt một đoạn ra nhiều dòng. Không tóm tắt, không bỏ câu, không thêm nội dung.
- `*`, `_` hiện nguyên ký tự (không thành in đậm/in nghiêng), `[...]` không phải link. Không tự thêm ảnh; raw hay file chương có dòng ảnh `![...](images/...)` thì giữ nguyên dòng đó ở vị trí tương ứng.
- Bỏ ghi chú translator (T/N) của raw. T/N kẹp trong câu thì chỉ bỏ phần ghi chú, vẫn dịch phần truyện của câu đó. Quyết định bỏ hẳn một dòng raw không phải truyện thì ghi lý do vào `rules.md` và thêm nguyên văn dòng đó vào `raw_ignore_lines` trong `novel.json`, để QA không báo thiếu đoạn.
- Theo `rules.md` (tên, thuật ngữ, định dạng) và `style.md` (giọng văn). Viết tiếng Việt tự nhiên ngay từ bản đầu theo `natural-vietnamese.md`, không dịch bám chữ rồi để sửa sau. Mỗi lời thoại phải đúng xưng hô cho cặp người nói/người nghe ở thời điểm của chương.
- Chương dài thì ghi file theo nhiều phần nối tiếp, nhưng mỗi phần vẫn dịch đủ.

### Bước 3 — QA

```
python .agents/skills/novel-translate/scripts/qa_check.py <slug> N
```

- `[LỖI]` thì bắt buộc sửa rồi chạy lại. Thiếu đoạn gần như chắc chắn là bỏ sót hoặc gộp đoạn: `qa_check.py <slug> N --side` in từng cặp đoạn raw / bản dịch theo đúng cách QA đếm, chỗ hai bên bắt đầu lệch là chỗ sót hoặc gộp.
- `[cảnh báo]` thì xem từng cái. Sửa những cái là lỗi thật; cái nào là báo nhầm (ví dụ thuật ngữ được diễn đạt lại hợp lý, hoặc từ trong raw dùng theo nghĩa thường) thì bỏ qua.

Sau khi script sạch, tự đọc lại bản dịch một lượt và kiểm tra: đại từ người kể dùng cho từng nhân vật có nhất quán không; xưng hô trong mọi lời thoại có đúng cặp và đúng thời điểm không; còn câu văn dịch máy, cứng, sai nghĩa không (soát theo `natural-vietnamese.md`); câu đùa có còn buồn cười không.

### Bước 4 — Cập nhật context

Xem lại chương vừa dịch và cập nhật bằng `ctx.py`, không mở file:

- **Tóm tắt chương: bắt buộc.** 3–5 dòng: diễn biến chính, nhân vật/kỹ năng mới, cảnh kết thúc. `ctx.py <slug> add-summary N --file <file>`, script tự ghi vào đúng file arc.
- **Nhân vật**: nhân vật mới (`add-char`); tính cách, cách nói chuyện mới lộ ra; thay đổi lớn về trạng thái hay quan hệ (`char-note`, `set characters <tên> "vai trò" ...`). Mục chi tiết chỉ ghi điều **lâu dài**, không ghi diễn biến từng chương (diễn biến thuộc tóm tắt chương): mục chi tiết được nạp mỗi khi nhân vật xuất hiện, nên nhật ký kiểu `- Chương 7: ...` làm nó phình theo số chương. Kỹ năng và trạng thái giữ **một dòng** cho mỗi nhãn: `char-note <tên> "Kỹ năng: ..." --replace "Kỹ năng"`, `char-note <tên> "Trạng thái tính đến chương N: ..." --replace "Trạng thái"`. Nhân vật lộ tên thật sau một thời gian chỉ được gọi bằng biệt danh thì **thêm dòng riêng** cho tên thật, giữ dòng biệt danh, ghi chú liên kết hai dòng; không nhét tên thật vào Alias của dòng biệt danh.
- **Xưng hô**: cặp mới dùng trong chương. Quan hệ thay đổi (thân hơn, trở mặt, lộ thân phận) thì **thêm dòng mới** với `Từ chương` = N, không sửa dòng cũ. Không thêm đám đông hay vật phẩm.
- **Thuật ngữ**: chỉ tên riêng và thuật ngữ cố định, không thêm cụm miêu tả chung. Cột `VI` chỉ ghi **một** bản dịch, không ghi hai dạng ngăn bằng `/`: tên gọi tắt là một dòng riêng. Đã có mục cùng nghĩa (`find`) thì thêm vào Alias của mục đó.
- `style.md`: đặc điểm giọng kể mới đáng giữ; cảm thán mới vào bảng cảm thán. `rules.md`, mục "Riêng truyện này": trường hợp mới cần xử lý thống nhất về sau.

Cập nhật xong thì chạy `python .agents/skills/novel-translate/scripts/lint_context.py <slug>` và sửa hết `[LỖI]`.

**Không tự ghi đè quyết định cũ.** Thấy một thuật ngữ, tên hay xưng hô đã chốt có vẻ sai, hoặc mâu thuẫn với raw chương mới: giữ nguyên cách cũ trong bản dịch, ghi câu hỏi bằng `progress.py <slug> ask N "<vấn đề> — đề xuất <...>"`, và báo ở cuối lượt.

### Bước 5 — Đánh dấu xong

```
python .agents/skills/novel-translate/scripts/progress.py <slug> set N done
```

Dịch xong mọi chương của lượt thì chạy `python scripts/build_index.py` từ repo root để cập nhật `index.json` (danh sách chương cho app). Thoát với `[LỖI]` thì sửa đúng file được nêu rồi chạy lại. Commit `index.json` **cùng lúc** với các chương đó để `sha` khớp. Chạy dưới orchestrator thì **bỏ qua** bước này.

## Chạy dưới orchestrator

Brief có ghi "chế độ orchestrator" thì:

- Chỉ làm đúng việc và đúng chương được giao, rồi dừng. Không tự sang chương khác.
- Không chờ user. Chỗ nào skill bảo "báo user, chờ duyệt" thì ghi đề xuất và câu hỏi vào báo cáo, chọn phương án hợp lý nhất để làm tiếp, rồi kết thúc lượt. Orchestrator sẽ quyết và sửa lại nếu cần.
- Không tạo file tạm hay file nháp trong repo, kể cả ở gốc repo. Cần file tạm thì đặt trong `.herdr/` và xoá khi xong.
- Câu hỏi ghi bằng `progress.py ask` (layout 1: xem `docs/layout1.md`), đồng thời ghi vào mục "Câu hỏi" của báo cáo.
- Không chạy `git` (add, commit, push) và không chạy `scripts/build_index.py`. Orchestrator lo việc này; panel sửa file ngoài `translations/<slug>/` (kể cả `index.json`) sẽ bị orchestrator dừng vòng lặp.

## Lệnh khác

```
python .agents/skills/novel-translate/scripts/progress.py <slug> next -n 5     # 5 chương todo kế tiếp
python .agents/skills/novel-translate/scripts/progress.py <slug> stats         # tổng tiến độ
python .agents/skills/novel-translate/scripts/progress.py <slug> questions     # các câu hỏi đang mở
python .agents/skills/novel-translate/scripts/progress.py <slug> set 290-292 skip --note "trùng #287-289"
python .agents/skills/novel-translate/scripts/extract_terms.py <slug> 40-60 --all   # soát thuật ngữ một đoạn truyện
python .agents/skills/novel-translate/scripts/qa_check.py <slug> 1-20          # QA lại một loạt chương
```

## Báo cáo cuối lượt

Sau khi dịch xong một hoặc nhiều chương, báo ngắn gọn:
- những chương đã xong và kết quả QA;
- kết quả `build_index.py` (số truyện, số chương trong `index.json`), trừ khi chạy dưới orchestrator;
- thuật ngữ, nhân vật, xưng hô mới đã thêm, mỗi mục một dòng `EN → VI`;
- các câu hỏi mới đã ghi, nếu có.
