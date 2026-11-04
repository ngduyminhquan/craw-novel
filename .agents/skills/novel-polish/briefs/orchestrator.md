Bạn là orchestrator cho việc **trau chuốt văn phong** truyện `__SLUG__`, chương __A__–__B__. Bạn không tự sửa bản dịch. Việc của bạn là mở panel con, chờ, kiểm tra kết quả, rồi commit và push.

- Repo root: __ROOT__. Môi trường đã ở trong Herdr (`HERDR_ENV=1`). Folder đã được trust cho agy.
- Trước khi làm, đọc `.agents/skills/herdr-spawn/SKILL.md` để biết cú pháp `spawn.sh` và `wait-report.sh`, cùng cách xử lý từng `status`. Đọc mục "Mở panel và chờ", "Panel bị chặn" và "Commit và push" trong `.agents/skills/novel-orchestrator/SKILL.md`. Các mục đó áp dụng ở đây, trừ những điểm brief này ghi đè.
- Brief cho panel con đã được sinh sẵn trong `.herdr/tasks/` từ template của skill `novel-polish`.

## Quy trình

Các vòng: __CYCLES__. Mỗi vòng gồm:

1. Ghi lại `BASE=$(git log -1 --format=%h)`.
2. Với từng chương N trong vòng, **tuần tự**:
   - Brief đã sinh sẵn: `.herdr/tasks/pl-<NNN>.md` (N đệm 3 chữ số).
   - Mở panel bằng `bash .agents/skills/herdr-spawn/scripts/spawn.sh pl-<NNN> agy --task-file .herdr/tasks/pl-<NNN>.md --max 8 -- --model __POLISH_MODEL__ --dangerously-skip-permissions`, rồi chờ bằng `wait-report.sh pl-<NNN> --timeout 5400 --idle-grace 300` ở chế độ nền.
   - Kiểm tra:
     - **phạm vi**: chỉ `translations/__SLUG__/` thay đổi, không có file trong `vi/images/` bị sửa hay xoá;
     - `git diff --stat` có `vi/Chapter_<NNN>.md` thay đổi đáng kể. Nếu gần như không đổi thì nhắc panel làm lại đúng yêu cầu;
     - `python .agents/skills/novel-translate/scripts/qa_check.py __SLUG__ N` không có `[LỖI]`.
   - Đọc báo cáo. Panel đề xuất đổi thuật ngữ hay xưng hô thì **không áp dụng**, chỉ gom lại để đưa vào báo cáo cuối.
   - Đóng pane. Commit và push với message `style(translate): trau chuốt văn phong chương N`.
3. Review vòng, chương a–b:
   - Brief đã sinh sẵn: `.herdr/tasks/plr-<aaa>-<bbb>.md`, còn chừa chỗ `__BASE__`. Điền vào bằng `sed -i "s/__BASE__/$BASE/g" .herdr/tasks/plr-<aaa>-<bbb>.md`.
   - Mở panel `plr-<aaa>-<bbb>` với `--model __REVIEW_MODEL__ --dangerously-skip-permissions` (thêm `--max 8`), rồi chờ với `--timeout 7200 --idle-grace 300`.
   - Kiểm tra phạm vi. Chạy `python .agents/skills/novel-orchestrator/scripts/orchestrate.py __SLUG__ verify a-b --status reviewed`, kết quả phải OK cả.
   - Đóng pane. Commit và push với message `style(translate): review văn phong chương a-b`.
   - Báo cáo review có "nhận xét chung về lỗi lặp lại" thì thêm các nhận xét đó vào cuối brief `pl-*.md` của vòng sau, dưới tiêu đề `Lưu ý từ lượt review trước:`. Sửa bản sinh ra trong `.herdr/tasks/`, không sửa template trong skill.

Mỗi lúc chỉ một panel làm việc. Commit xong mới mở panel tiếp theo.

## Quy tắc commit và push (ghi đè skill)

- Chỉ stage `translations/__SLUG__/` và `index.json`, sinh bằng `python scripts/build_index.py` sau khi add thư mục truyện. Tuyệt đối không stage thư mục raw (`__RAW__/`), `.herdr/` hay thư mục của truyện khác trong `translations/`. Trước `git commit`, xem `git diff --cached --stat`.
- Push bị từ chối thì chạy `git pull --rebase --autostash origin main`, rồi push lại. Nếu rebase chỉ conflict ở `index.json`:
    git checkout origin/main -- index.json
    python scripts/build_index.py
    git add -- index.json
    GIT_EDITOR=true git rebase --continue
  rồi push lại. Conflict ở file khác thì `git rebase --abort` rồi dừng. Không bao giờ dùng `git reset`, `git stash` hay force push.
- Commit thì tự chạy, không cần subagent.

## Dừng

- Xong mọi vòng thì dừng.
- Dừng sớm khi: panel hỏng hai lần liền ở cùng một chương; vi phạm phạm vi; push lỗi; panel kẹt mà bạn không tự xử lý được.
- **Manager nhắn bảo dừng thì dừng ngay**: không mở panel mới, kể cả khi vòng đang dở. Panel đang chạy thì đóng nó và bỏ thay đổi chưa commit của chương đó bằng `git checkout -- translations/__SLUG__/` (đây là ngoại lệ duy nhất được phép).
- Trước khi dừng, đóng các pane con còn mở.

## Báo cáo cuối

Ghi vào file báo cáo của bạn, gồm:
- các chương đã trau chuốt và đã review, kèm commit;
- đánh giá chất lượng từng chương, lấy từ báo cáo review;
- lỗi lặp lại phổ biến và thay đổi đã thêm vào `style.md`; lỗi nào mang tính chung cho mọi truyện thì ghi riêng, để manager cân nhắc bổ sung vào `natural-vietnamese.md`;
- các đề xuất đổi thuật ngữ hay xưng hô chưa áp dụng, mỗi mục một dòng, kèm bằng chứng;
- lý do dừng.
Dòng cuối: `STATUS: done`.
