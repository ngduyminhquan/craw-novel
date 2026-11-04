Chế độ orchestrator. Dùng skill `novel-translate`: đọc `.agents/skills/novel-translate/SKILL.md` trước, gồm cả mục "Chạy dưới orchestrator".

Repo: __ROOT__
Truyện: `__SLUG__`

Việc: **trau chuốt văn phong chương __N__** (`translations/__SLUG__/vi/Chapter___NNN__.md`). Chương này đã dịch và review xong, nhưng user đọc thấy văn còn cứng, máy móc, đọc ra ngay là truyện dịch. Nhiệm vụ của bạn là viết lại cho tự nhiên như truyện viết bằng tiếng Việt, đồng thời vẫn trung thành với raw.

Raw: `__RAW__/Chapter___NNN__ - *.txt`

Cách làm:
1. Đọc `context/style.md` thật kỹ, nhất là mục **"Lỗi văn dịch máy cần tránh"** (chưa có thì dựa vào danh sách ở cuối brief). Đọc `context/rules.md`. Chạy `python .agents/skills/novel-translate/scripts/prepare.py __SLUG__ __N__` để lấy nhân vật, xưng hô và thuật ngữ liên quan tới chương.
2. Đi qua **từng đoạn**. Đoạn K của bản dịch ứng với đoạn K của raw. Đọc đoạn raw, đọc bản dịch, rồi viết lại câu nào còn cứng, sai nghĩa, thiếu ý hay lủng củng. Đây là biên tập lại, không phải soát lỗi chính tả: gần như đoạn nào cũng có chỗ cần sửa.
3. Giữ nguyên:
   - số đoạn và thứ tự đoạn, không gộp hay tách đoạn;
   - dòng tiêu đề, dòng ảnh `![..](..)`, dấu phân cách, ghi chú T/N;
   - tên riêng, thuật ngữ và tên kỹ năng theo `glossary.md`, `characters.md`, `rules.md`;
   - các cặp xưng hô đã chốt trong `pronouns.md`.
4. Không thêm hay bớt ý so với raw. Gặp chỗ bản dịch cũ dịch sai nghĩa thì sửa theo raw.
5. Context:
   - Rút ra được quy luật văn phong mới, áp dụng chung cho cả truyện, thì thêm một gạch đầu dòng ngắn vào mục "Lỗi văn dịch máy cần tránh" của `style.md`. Không lặp ý đã có.
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

Danh sách lỗi văn dịch máy thường gặp (dùng khi `style.md` chưa có mục riêng): bê nguyên cấu trúc câu tiếng Anh; mệnh đề phân từ treo đầu câu; danh từ hoá thừa ("việc", "sự", "điều"); bị động thừa; lạm dụng gạch ngang "—"; lặp đại từ và "của tôi"; mở câu liên tục bằng "Tuy nhiên", "Dẫu vậy", "Ngoài ra"; cụm sáo kiểu văn bản; hư từ thừa ("đã", "đang", "những", "một"); lời thoại như văn viết; dịch thành ngữ từng chữ; nhịp câu dài lê thê hoặc cụt liên tiếp; câu đùa mất duyên.
