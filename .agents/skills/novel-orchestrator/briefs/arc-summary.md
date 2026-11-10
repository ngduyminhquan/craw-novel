Chế độ orchestrator. Dùng skill `novel-translate`: đọc `.agents/skills/novel-translate/SKILL.md` trước, gồm cả mục "Chạy dưới orchestrator".

Repo: $root

Việc: tóm tắt arc $arc ($label) của truyện `$slug` rồi viết lại story-so-far, theo mục F của skill.
- File arc: `$arc_file`
- Các chương của arc: $range

Không dịch, không sửa bản dịch hay file context nào khác. Không chạy git.

Tiêu chí xong:
- `python .agents/skills/novel-orchestrator/scripts/orchestrate.py $slug verify-arc $arc` báo OK.
- `story-so-far.md` không quá $story_limit ký tự (lệnh `set-story` tự chặn).

Báo cáo gồm:
- tóm tắt arc đã ghi (chép nguyên văn);
- phần nào của story-so-far đã được nén lại hay bỏ đi, và vì sao;
- các mạch truyện còn dở mà arc sau cần nhớ.
