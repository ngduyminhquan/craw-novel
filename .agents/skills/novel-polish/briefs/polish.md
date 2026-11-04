Chế độ orchestrator. Dùng skill `novel-translate`: đọc `.agents/skills/novel-translate/SKILL.md` trước, gồm cả mục "Chạy dưới orchestrator".

Repo: __ROOT__
Truyện: `__SLUG__`

Việc: **trau chuốt văn phong chương __N__** (`translations/__SLUG__/vi/Chapter___NNN__.md`). Chương này đã dịch và review xong, nhưng user đọc thấy văn còn cứng, máy móc, đọc ra ngay là truyện dịch. Nhiệm vụ của bạn là viết lại cho tự nhiên như truyện viết bằng tiếng Việt, đồng thời vẫn trung thành với raw.

Raw: `__RAW__/Chapter___NNN__ - *.txt`

Cách làm:
1. Đọc thật kỹ `.agents/skills/novel-translate/natural-vietnamese.md`: đây là danh sách lỗi văn dịch máy dùng chung, cũng là tiêu chí chính của lượt này. Đọc `context/style.md` để nắm giọng riêng của truyện và nhân vật, cùng các quy luật riêng nếu có. Quy luật riêng trong `style.md` (ví dụ yêu cầu về độ hiện đại, độ trẻ của giọng văn) thắng file chung: soát cả chương theo đúng các quy luật đó. Đọc `context/rules.md`. Chạy `python .agents/skills/novel-translate/scripts/prepare.py __SLUG__ __N__` để lấy nhân vật, xưng hô và thuật ngữ liên quan tới chương.
2. Đi qua **từng đoạn**. Đoạn K của bản dịch ứng với đoạn K của raw. Đọc đoạn raw, đọc bản dịch, rồi viết lại câu nào còn cứng, sai nghĩa, thiếu ý hay lủng củng. Đây là biên tập lại, không phải soát lỗi chính tả: gần như đoạn nào cũng có chỗ cần sửa. Giữ độ kỹ đều tay tới đoạn cuối: chương dài hay bị sửa kỹ nửa đầu rồi lướt nửa sau. Chia chương thành từng khúc 20–30 đoạn, xong khúc nào thì soát lại khúc đó.
3. Giữ nguyên:
   - số đoạn và thứ tự đoạn, không gộp hay tách đoạn;
   - dòng tiêu đề, dòng ảnh `![..](..)`, dấu phân cách, ghi chú T/N;
   - tên riêng, thuật ngữ và tên kỹ năng theo `glossary.md`, `characters.md`, `rules.md`;
   - các cặp xưng hô đã chốt trong `pronouns.md`.
   - ranh giới lời thoại và độc thoại như raw: câu raw không có ngoặc kép (độc thoại nội tâm) thì bản dịch cũng không có, và ngược lại.
4. Không thêm hay bớt ý so với raw. Gặp chỗ bản dịch cũ dịch sai nghĩa thì sửa theo raw.
5. Context:
   - Rút ra được quy luật văn phong riêng của truyện này (giọng nhân vật, cách nói lặp lại của raw...) thì thêm một gạch đầu dòng ngắn vào `style.md`. Không lặp ý đã có trong `style.md` hay `.agents/skills/novel-translate/natural-vietnamese.md`. Không sửa `.agents/skills/novel-translate/natural-vietnamese.md`.
   - Thấy một thuật ngữ hay cặp xưng hô đã chốt mà đọc gượng hoặc sai: **không đổi** trong context hay trong chương. Ghi vào mục "Đề xuất" của báo cáo, nêu bằng chứng từ raw. Lý do: thuật ngữ và xưng hô đã dùng trong nhiều chương, đổi ở một chỗ sẽ gây lệch.
   - Lỗi nhỏ trong `characters.md` (sai sự thật so với raw chương này) thì được sửa thẳng.
6. Chạy `python .agents/skills/novel-translate/scripts/qa_check.py __SLUG__ __N__` cho tới khi hết `[LỖI]`.
7. Không đổi trạng thái trong `progress.md`. Không sửa chương khác. Không chạy git.

Báo cáo gồm:
- tỉ lệ đoạn đã sửa, ước chừng;
- 3–5 ví dụ tiêu biểu theo dạng `đoạn K: "<cũ>" → "<mới>"`;
- các chỗ sai nghĩa đã sửa theo raw;
- thay đổi trong context;
- đề xuất về thuật ngữ hay xưng hô (nếu có).
