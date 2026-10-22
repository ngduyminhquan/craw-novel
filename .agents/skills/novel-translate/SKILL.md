---
name: novel-translate
description: Dịch truyện (webnovel) từ raw tiếng Anh sang tiếng Việt theo từng chương, giữ nhất quán tên nhân vật, xưng hô, thuật ngữ, tên kỹ năng và văn phong qua các file context. Dùng khi user bảo "dịch chương N", "dịch tiếp", "dịch 5 chương", "khởi tạo truyện mới để dịch", "cập nhật glossary/nhân vật", hoặc nhắc tới thư mục translations/.
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
  novel.json            # tên truyện, đường dẫn raw, raw_ignore_lines (dòng raw không phải truyện, script bỏ qua khi đếm đoạn)
  progress.md           # bảng tiến độ (todo/done/reviewed/skip) + "Cần user xác nhận" + "Đã quyết"
  context/
    rules.md            # quy tắc cứng: tên riêng, thuật ngữ, định dạng, T/N. Ưu tiên cao nhất
    style.md            # góc nhìn, giọng kể, nguyên tắc văn phong, bảng cảm thán
    characters.md       # bảng nhân vật (EN | Alias | VI) + tính cách, cách nói chuyện
    pronouns.md         # người kể gọi nhân vật + xưng hô từng cặp, có mốc chương
    glossary.md         # thuật ngữ, kỹ năng, danh hiệu, vật phẩm, địa danh
    summaries.md        # tóm tắt 3–5 dòng mỗi chương
  vi/Chapter_001.md     # bản dịch, đánh số theo cột # của progress.md
```

Các bảng trong context được script đọc. Giữ đúng tên cột, mỗi dòng một mục, không thêm `|` trong ô.

## A. Khởi tạo truyện mới (một lần)

1. Chạy:
   ```
   python .agents/skills/novel-translate/scripts/init_novel.py --raw "<thư mục raw>" --slug <slug> --title "<tên truyện>"
   ```
   Raw phải có dạng `Chapter_XXX - <tiêu đề>.txt`. Script đánh dấu `skip` các chương nghi trùng (cùng tiêu đề). Mở raw các cặp đó, đối chiếu vài đoạn để xác nhận trùng thật; không trùng thì sửa lại `todo`.
2. Dựng context ban đầu:
   ```
   python .agents/skills/novel-translate/scripts/extract_terms.py <slug> 1-15 --min 2
   ```
   Đọc lướt 3–5 chương đầu, rồi điền: `style.md` (thể loại, góc nhìn, giọng kể), `characters.md` (nhân vật chính và tính cách), `pronouns.md` (người kể gọi nhân vật chính là gì, xưng hô các cặp chính), `glossary.md` (thuật ngữ xuất hiện nhiều).
3. Báo user các quyết định quan trọng (đại từ người kể dùng cho nhân vật chính, xưng hô các cặp chính, 10–20 thuật ngữ chính) và chờ duyệt trước khi dịch chương đầu tiên.

## B. Dịch một chương

Làm đủ 5 bước cho từng chương. Dịch nhiều chương thì làm **tuần tự** từng chương một, xong bước 5 của chương này mới sang chương sau. Không dịch song song nhiều chương, vì chương sau dùng context do chương trước cập nhật.

### Bước 1 — Chuẩn bị

```
python .agents/skills/novel-translate/scripts/prepare.py <slug> [N]
```

Bỏ `N` thì script lấy chương `todo` kế tiếp. Output gồm: đường dẫn raw và file bản dịch, góc nhìn ước lượng, nhân vật đã biết xuất hiện kèm xưng hô liên quan, thuật ngữ **chưa có** trong context, tóm tắt 3 chương trước.

Sau đó:

1. Đọc `rules.md` và `style.md`. Đọc mục chi tiết trong `characters.md` của các nhân vật script liệt kê.
2. Đọc toàn bộ raw của chương.
3. **Thuật ngữ mới**: với mỗi mục script liệt kê là tên riêng/kỹ năng thật (bỏ qua từ thường bị bắt nhầm), chốt bản dịch theo `rules.md` và thêm vào `glossary.md` hoặc `characters.md` **trước khi dịch**. Tên chưa chắc là ai, hoặc là cách viết khác của tên đã có, thì thêm vào cột Alias của mục cũ.
4. **Góc nhìn và xưng hô**: xác nhận góc nhìn của chương (có chương đổi sang góc nhìn nhân vật khác). Với mỗi cặp nhân vật có hội thoại mà `pronouns.md` chưa có, quyết định xưng hô dựa trên tuổi, địa vị, quan hệ, tính cách và ghi vào `pronouns.md`.
5. **Mạch truyện**: đọc tóm tắt script in ra. Chương mở đầu nối tiếp cảnh của chương trước (cùng arc, cảnh chưa kết thúc) thì đọc phần cuối bản dịch liền trước để giữ giọng và chi tiết. Chương nhắc lại chi tiết cũ mà tóm tắt không đủ thì đọc thêm bản dịch của 2–3 chương trước đó. Chưa có chương nào đã dịch thì bỏ qua.

### Bước 2 — Dịch

Ghi vào file bản dịch script đã in ra (`translations/<slug>/vi/Chapter_NNN.md`).

- Dòng đầu: `# Chương N: <tiêu đề dịch>`, rồi một dòng trống.
- Dịch **đủ từng đoạn**, theo đúng thứ tự. Mỗi đoạn raw thành một đoạn dịch, cách nhau dòng trống. Không tóm tắt, không bỏ câu, không thêm nội dung.
- Bỏ ghi chú translator (T/N) của raw. T/N kẹp trong câu thì chỉ bỏ phần ghi chú, vẫn dịch phần truyện của câu đó.
- Quyết định bỏ hẳn một dòng raw không phải truyện (vd bảng chú giải ký hiệu của bản EN) thì ghi lý do vào `rules.md` và thêm nguyên văn dòng đó vào `raw_ignore_lines` trong `novel.json`, để QA không báo thiếu đoạn.
- Theo `rules.md` (tên, thuật ngữ, định dạng) và `style.md` (giọng văn). Mỗi lời thoại phải đúng xưng hô trong `pronouns.md` cho cặp người nói/người nghe ở thời điểm của chương.
- Chương dài thì ghi file theo nhiều phần nối tiếp, nhưng mỗi phần vẫn dịch đủ.

### Bước 3 — QA

```
python .agents/skills/novel-translate/scripts/qa_check.py <slug> N
```

- `[LỖI]` thì bắt buộc sửa rồi chạy lại. Lệch số đoạn theo hướng thiếu nghĩa là gần như chắc chắn đã bỏ sót: đối chiếu từng đoạn với raw để tìm chỗ thiếu.
- `[cảnh báo]` thì xem từng cái. Sửa những cái là lỗi thật; cái nào là báo nhầm (ví dụ thuật ngữ được diễn đạt lại hợp lý) thì bỏ qua.

Sau khi script sạch, tự đọc lại bản dịch một lượt và kiểm tra:
- đại từ người kể dùng cho từng nhân vật có nhất quán không;
- xưng hô trong mọi lời thoại có đúng cặp và đúng thời điểm không;
- có câu nào còn văn dịch máy, cứng, sai nghĩa không;
- câu đùa có còn buồn cười không.

### Bước 4 — Cập nhật context

Xem lại chương vừa dịch và cập nhật:

- `summaries.md`: **bắt buộc**, thêm mục `## N` gồm 3–5 dòng: diễn biến chính, nhân vật/kỹ năng mới, cảnh kết thúc.
- `characters.md`: nhân vật mới; tính cách hoặc cách nói chuyện mới lộ ra; thay đổi lớn về trạng thái hay quan hệ (ghi "tính đến chương N"). Nhân vật lộ tên thật sau một thời gian chỉ được gọi bằng biệt danh thì **thêm dòng riêng** cho tên thật, giữ dòng biệt danh, và ghi chú liên kết hai dòng. Không nhét tên thật vào Alias của dòng biệt danh.
- `pronouns.md`: cặp xưng hô mới dùng trong chương. Quan hệ thay đổi (thân hơn, trở mặt, lộ thân phận) thì **thêm dòng mới** với `Từ chương` = N, không sửa dòng cũ. Tên trong cột `A`, `B`, `Nhân vật` phải đúng giá trị cột `EN` của một dòng trong `characters.md`. Không thêm đám đông hay vật phẩm.
- `glossary.md`: thuật ngữ đã thêm ở bước 1 mà còn thiếu loại hoặc ghi chú. Chỉ thêm tên riêng và thuật ngữ cố định, không thêm cụm miêu tả chung (vd "black leopard" chỉ để tả một con báo đen). Cột `VI` chỉ ghi **một** bản dịch. Nếu thật sự cần hai dạng theo ngữ cảnh, ghi cả hai ngăn bằng `/` và nói rõ trong Ghi chú khi nào dùng dạng nào.
- `style.md`: đặc điểm giọng kể mới đáng giữ; cảm thán mới vào bảng cảm thán.
- `rules.md`, mục "Riêng truyện này": trường hợp mới cần xử lý thống nhất về sau.

Cập nhật xong thì chạy `python .agents/skills/novel-translate/scripts/lint_context.py <slug>` và sửa hết `[LỖI]`.

**Không tự ghi đè quyết định cũ.** Thấy một thuật ngữ, tên hay xưng hô đã chốt có vẻ sai, hoặc mâu thuẫn với raw chương mới:
1. giữ nguyên cách cũ trong bản dịch;
2. ghi vào mục "Cần user xác nhận" cuối `progress.md`, gồm số chương, vấn đề và đề xuất;
3. báo user ở cuối lượt.

### Bước 5 — Đánh dấu xong

```
python .agents/skills/novel-translate/scripts/progress.py <slug> set N done
```

## C. Review một loạt chương (chỉ đọc)

Dùng khi được giao review, thường là 3 chương vừa dịch. **Không sửa file bản dịch hay file context.** Kết quả duy nhất là báo cáo.

1. Đọc `rules.md`, `style.md`, `pronouns.md`, cùng các mục liên quan trong `characters.md` và `glossary.md`.
2. Với từng chương, đối chiếu **từng đoạn** bản dịch với raw (đoạn K của bản dịch ứng với đoạn K của raw sau khi bỏ tiêu đề và T/N). Tìm:
   - sai nghĩa, bỏ sót hoặc thêm thắt nội dung;
   - sai xưng hô (sai cặp, sai thời điểm, lệch giữa các chương);
   - đại từ người kể dùng cho nhân vật không nhất quán;
   - thuật ngữ hoặc tên lệch với glossary/characters, hay lệch nhau giữa 3 chương;
   - câu văn dịch máy, cứng, khó đọc; câu đùa mất duyên;
   - vi phạm định dạng trong `rules.md`.
3. Chạy `qa_check.py <slug> <range>` và đưa các cảnh báo đáng chú ý vào báo cáo.
4. Báo cáo theo đúng mẫu sau, mỗi lỗi một dòng, trích nguyên văn đủ để tìm được chỗ cần sửa:

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
2. Sửa thẳng trong `vi/Chapter_NNN.md`. Một lỗi có cùng kiểu (cùng thuật ngữ, cùng cặp xưng hô) thì sửa hết mọi chỗ trong các chương được giao, không chỉ chỗ được chỉ ra.
3. Cập nhật context theo các đề xuất đã được chấp nhận (đúng quy tắc ở bước B4: không sửa dòng xưng hô cũ mà thêm dòng mới).
4. Chạy `qa_check.py <slug> <range>` cho đến khi hết `[LỖI]`.
5. Đánh dấu: `progress.py <slug> set <range> reviewed`. Nếu brief bảo giữ nguyên trạng thái thì bỏ qua bước này.
6. Báo cáo: số lỗi đã sửa trong từng chương, những thay đổi context, các mục không sửa được và lý do.

## Chạy dưới orchestrator

Brief có ghi "chế độ orchestrator" thì:

- Chỉ làm đúng việc và đúng chương được giao, rồi dừng. Không tự sang chương khác.
- Không chờ user. Chỗ nào skill bảo "báo user, chờ duyệt" (bước A3, mục "Cần user xác nhận") thì ghi đề xuất và câu hỏi vào báo cáo, chọn phương án hợp lý nhất để làm tiếp, rồi kết thúc lượt. Orchestrator sẽ quyết và sửa lại nếu cần.
- Không chạy `git` (add, commit, push). Orchestrator lo việc này.
- Câu hỏi vẫn ghi vào mục "Cần user xác nhận" trong `progress.md`, đồng thời ghi vào mục "Câu hỏi" của báo cáo.

## Lệnh khác

```
python .agents/skills/novel-translate/scripts/progress.py <slug> next -n 5     # 5 chương todo kế tiếp
python .agents/skills/novel-translate/scripts/progress.py <slug> stats         # tổng tiến độ
python .agents/skills/novel-translate/scripts/progress.py <slug> set 290-292 skip --note "trùng #287-289"
python .agents/skills/novel-translate/scripts/extract_terms.py <slug> 40-60 --all   # soát thuật ngữ một đoạn truyện
python .agents/skills/novel-translate/scripts/qa_check.py <slug> 1-20          # QA lại một loạt chương
```

## Báo cáo cuối lượt

Sau khi dịch xong một hoặc nhiều chương, báo ngắn gọn:
- những chương đã xong và kết quả QA;
- thuật ngữ, nhân vật, xưng hô mới đã thêm, mỗi mục một dòng `EN → VI`;
- các mục mới trong "Cần user xác nhận", nếu có.
