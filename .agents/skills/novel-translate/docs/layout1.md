# Truyện layout 1 (truyện cũ)

Phần của skill `novel-translate`. `novel.json` **không** có `"layout": 2` (vd `the-unwanted-undead-adventurer`) thì làm theo `SKILL.md`, chỉ khác ở các điểm sau:

- **Context sửa thẳng file.** Các lệnh ghi của `ctx.py` (`add-*`, `set`, `char-note`, `add-summary`...) và `progress.py ask` từ chối truyện layout 1. Ở bước B1, B4 và khi sửa theo review, đọc và sửa thẳng `characters.md`, `glossary.md`, `pronouns.md`, theo đúng các quy tắc nội dung của bước đó (Alias, một bản dịch ở cột VI, thêm dòng xưng hô mới thay vì sửa dòng cũ...). Các lệnh tra (`find`, `show-char`, `pronouns`, `show-summaries`) vẫn dùng được.
- **Tóm tắt** nằm trong một file `context/summaries.md`: thêm mục `## N` gồm 3–5 dòng cho mỗi chương. Không có tóm tắt arc hay `story-so-far.md`; `prepare.py` in tóm tắt 3 chương trước.
- **Câu hỏi** ghi vào mục `## Cần user xác nhận` **đã có** trong `progress.md` (nằm ngay trên mục `## Đã quyết`, không phải cuối file; không tạo mục mới), mỗi câu một dòng `- [#N] ...`. Không có `questions.md`, `decisions/`.
- **Review** đọc trọn `pronouns.md` và các mục liên quan trong `characters.md`, `glossary.md`.
