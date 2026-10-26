Chế độ orchestrator. Dùng skill `novel-translate`: đọc `.agents/skills/novel-translate/SKILL.md` trước, gồm cả mục "Chạy dưới orchestrator".

Repo: $root

Việc: dịch chương #$n ($title) của truyện `$slug`, làm đủ 5 bước của mục B. Lệnh bước 1: `python .agents/skills/novel-translate/scripts/prepare.py $slug $n`

Chỉ dịch chương #$n. Xong bước 5 thì dừng. Không chạy git.

Tiêu chí xong:
- `$vi` tồn tại và dịch đủ mọi đoạn.
- `python .agents/skills/novel-translate/scripts/qa_check.py $slug $n` không còn `[LỖI]`.
- `progress.md` ghi #$n là `done`, và `summaries.md` có mục `## $n`.
- Tiêu đề chương ở dòng 1 đã dịch sang tiếng Việt, cùng cách dịch với các chương cùng arc trước đó.

Báo cáo gồm:
- kết quả QA, kèm các cảnh báo còn lại và lý do giữ nguyên;
- thuật ngữ, nhân vật, xưng hô mới đã thêm vào context, mỗi mục một dòng `EN → VI`;
- câu hỏi cần quyết, mỗi câu kèm phương án đã tạm dùng trong bản dịch. Mỗi câu cũng phải có trong `## Cần user xác nhận` của `progress.md` (một dòng, như mục "Chạy dưới orchestrator"); câu chỉ có trong báo cáo sẽ bị sót.
