# Review một loạt chương (chỉ đọc)

Phần của skill `novel-translate` (đọc `SKILL.md` trước). Dùng khi được giao review, thường là 3 chương vừa dịch. **Không sửa file bản dịch hay file context.** Kết quả duy nhất là báo cáo.

1. Đọc `rules.md`, `style.md` và `.agents/skills/novel-translate/natural-vietnamese.md` (bắt buộc: đây là tiêu chí bắt lỗi văn dịch máy). Chạy `prepare.py <slug> N` cho **từng** chương được giao: script in nhân vật, xưng hô, thuật ngữ liên quan và mạch truyện. Cần thêm thì `ctx.py pronouns`, `show-char`, `find`. Không đọc trọn `characters.md`, `glossary.md`, `pronouns.md`. (Truyện layout 1: đọc thẳng các file này, xem `docs/layout1.md`.)
2. Với từng chương, đối chiếu **từng đoạn** bản dịch với raw bằng `qa_check.py <slug> N --side` (đoạn K bản dịch ứng với đoạn K raw, đã bỏ tiêu đề và T/N; cột in bị cắt ngắn, chỗ cần đọc kỹ thì mở raw và bản dịch). Tìm:
   - sai nghĩa, bỏ sót hoặc thêm thắt nội dung;
   - sai xưng hô (sai cặp, sai thời điểm, lệch giữa các chương);
   - đại từ người kể dùng cho nhân vật không nhất quán;
   - thuật ngữ hoặc tên lệch với glossary/characters, hay lệch nhau giữa các chương;
   - câu văn dịch máy, cứng, khó đọc, phạm các lỗi trong `natural-vietnamese.md`; câu đùa mất duyên;
   - vi phạm định dạng hay quy tắc riêng trong `rules.md`, `style.md` (kể cả quy tắc mới thêm gần đây).
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
