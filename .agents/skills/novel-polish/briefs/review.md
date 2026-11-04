Chế độ orchestrator. Dùng skill `novel-translate`: đọc `.agents/skills/novel-translate/SKILL.md` trước, gồm cả mục "Chạy dưới orchestrator".

Repo: __ROOT__
Truyện: `__SLUG__`

Việc: **review và sửa văn phong chương __A__–__B__**. Các chương này vừa được những panel khác trau chuốt văn phong, mỗi panel một chương, dựa trên bản dịch đã review từ trước. Bạn là người biên tập cuối: đọc lại, sửa thẳng vào file và đảm bảo chất lượng đồng đều.

Raw: `__RAW__/Chapter_NNN - *.txt`. Bản dịch: `translations/__SLUG__/vi/Chapter_NNN.md`.
Xem panel trước đã đổi gì: `git diff __BASE__ -- translations/__SLUG__/` (chỉ đọc, không chạy lệnh git nào khác).

Cách làm:
1. Đọc kỹ `context/style.md`, nhất là mục "Lỗi văn dịch máy cần tránh". Đọc `context/rules.md`. Với mỗi chương, chạy `python .agents/skills/novel-translate/scripts/prepare.py __SLUG__ N`.
2. Với từng chương, đối chiếu **từng đoạn** với raw và kiểm tra:
   - **trung thành**: lần trau chuốt có làm sai nghĩa, thêm ý hay bỏ sót ý không. Đây là lỗi nặng nhất, sửa theo raw;
   - **tự nhiên**: còn câu nào đọc ra là văn dịch không. Viết lại;
   - **giọng nhân vật**: lời thoại có đúng tính cách và đúng cặp xưng hô trong `pronouns.md` không;
   - **nhất quán**: thuật ngữ, tên riêng và cách hành văn có đồng đều giữa các chương không;
   - **sửa quá tay**: câu bị viết hoa mỹ, thêm thắt cảm xúc không có trong raw, hoặc dùng từ Hán Việt nặng thì kéo lại cho mộc.
3. Kiểm tra các thay đổi context mà panel trước đã làm, trong `style.md` và `characters.md`. Bỏ hoặc sửa mục sai hay trùng ý. Gộp mục "Lỗi văn dịch máy cần tránh" cho gọn nếu bị phình.
4. Giữ nguyên số đoạn, dòng tiêu đề, dòng ảnh, dấu phân cách. Không đổi thuật ngữ hay cặp xưng hô đã chốt, nếu cần đổi thì ghi vào mục "Đề xuất" của báo cáo.
5. Chạy `python .agents/skills/novel-translate/scripts/qa_check.py __SLUG__ __A__-__B__` cho tới khi hết `[LỖI]`.
6. Không đổi trạng thái trong `progress.md`. Không sửa chương ngoài __A__–__B__. Không chạy git, ngoài lệnh `git diff` đã nói ở trên.

Báo cáo gồm:
- với từng chương: chất lượng sau lượt trau chuốt (tốt / khá / còn yếu), số chỗ bạn sửa, các lỗi sai nghĩa đã sửa;
- 2–3 ví dụ sửa tiêu biểu;
- nhận xét chung về lỗi lặp lại của các panel trau chuốt, để orchestrator nhắc ở các lượt sau;
- thay đổi trong context;
- đề xuất về thuật ngữ hay xưng hô (nếu có).
