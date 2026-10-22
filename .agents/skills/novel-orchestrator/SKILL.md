---
name: novel-orchestrator
description: Điều phối dịch truyện tự động qua Herdr. Mở panel agy (Gemini 3.8 Flash Medium) chạy skill novel-translate để khởi tạo truyện hoặc dịch từng chương. Cứ 3 chương thì mở panel review, rồi mở panel sửa. Commit và push sau mỗi chương, và tự quyết các câu hỏi agent phụ đặt ra. Dùng khi user bảo "chạy orchestrator", "tự động dịch", "dịch liên tục N chương", "dịch tới chương N", "điều phối dịch truyện <slug>".
---

# Điều phối dịch truyện

Bạn là orchestrator. Bạn **không tự dịch, không tự review, không tự sửa bản dịch**. Mọi việc đó giao cho panel agy chạy skill `novel-translate`. Việc của bạn:
- chọn bước tiếp theo;
- mở panel và giao brief;
- kiểm tra kết quả panel trả về;
- quyết các câu hỏi;
- commit và push.

Toàn bộ trạng thái nằm trong `translations/<slug>/progress.md`. Gọi lại `next` lúc nào cũng tiếp tục được, kể cả khi mất context.

Script: `python .agents/skills/novel-orchestrator/scripts/orchestrate.py <slug> ...`, đường dẫn tính từ repo root. Script đã được kiểm thử: gọi thẳng, không đọc mã.

## Bước 0 — Chuẩn bị

1. Kiểm tra đang chạy trong Herdr (`HERDR_ENV=1`). Không phải thì báo user và dừng.
2. Đọc `.agents/skills/herdr-spawn/SKILL.md` để biết cú pháp `spawn.sh` và `wait-report.sh`, cách gọi từ PowerShell, cách xử lý từng `status`. Skill này **ghi đè** herdr-spawn ở ba điểm:
   - đóng pane ngay sau khi xử lý xong báo cáo, không hỏi user;
   - câu hỏi về nội dung dịch do bạn quyết, theo mục "Quyết định";
   - hộp thoại xin quyền được tự duyệt trong phạm vi ở mục "Panel bị chặn".
3. Xác định với user:
   - `slug` của truyện;
   - nếu chưa khởi tạo thì cần thêm thư mục raw và tên truyện;
   - giới hạn: dịch tới chương nào (`--until N`) hoặc bao nhiêu chương.

   User không nói giới hạn thì mặc định dịch 9 chương (3 vòng review), rồi dừng và báo cáo.

## Vòng lặp

```
next ──► init ──► [panel] khởi tạo ──► duyệt context ──► commit
     ├─► translate N ──► [panel] dịch ──► verify ──► quyết câu hỏi ──► commit + push
     ├─► review a-b ──► [panel] review ──► phân loại lỗi ──► [panel] sửa ──► verify ──► commit + push
     └─► finished ──► báo cáo cuối
```

Mỗi vòng:

1. `orchestrate.py <slug> next --until <N>`. Script in ra một dòng: `action=init`, `action=translate n=<N>`, `action=review range=<R>` hoặc `action=finished`, kèm `open_questions=<k>`.
2. Nếu `open_questions` > 0: chạy `orchestrate.py <slug> questions` rồi quyết từng câu (mục "Quyết định") **trước khi** mở panel mới.
3. Làm theo action ở các mục dưới, rồi quay lại bước 1.

Làm **tuần tự**: mỗi lúc chỉ một panel làm việc, và commit xong mới mở panel tiếp theo. Panel sau đọc context do panel trước cập nhật. Nếu commit trong lúc panel khác đang sửa file thì sẽ commit dính phần làm dở.

### Mở panel và chờ

```
python .agents/skills/novel-orchestrator/scripts/orchestrate.py <slug> brief <kind> [...]
# in ra: name=<name> task=<file brief> report=<file báo cáo>
bash .agents/skills/herdr-spawn/scripts/spawn.sh <name> agy --task-file <task> -- --model gemini-3.8-flash-medium --mode auto
bash .agents/skills/herdr-spawn/scripts/wait-report.sh <name> --timeout 3600 --idle-grace 120
```

- Lệnh chờ chạy ở chế độ nền của harness, giống herdr-spawn bước 3.
- Mỗi lần mở panel là một session mới, nên context luôn sạch.
- Xử lý xong báo cáo thì đóng pane bằng `herdr pane close <pane>`.
- Tên panel trùng tên một panel đang sống (vì chạy lại) thì đóng panel cũ trước.

### action=init

1. `brief init --raw "<thư mục raw>" --title "<tên truyện>"`, rồi mở panel và chờ.
2. Đọc báo cáo, rồi đọc lướt các file context (`style.md`, `characters.md`, `pronouns.md`, `glossary.md`). Kiểm tra:
   - các chương `skip` có trùng thật không;
   - đại từ người kể dùng cho nhân vật chính có hợp giọng truyện không;
   - xưng hô các cặp chính có hợp tuổi và quan hệ không;
   - thuật ngữ có theo `rules.md` không.

   Sai thì tự sửa file context. Câu hỏi trong báo cáo thì quyết theo mục "Quyết định".
3. Đóng pane, rồi commit với message `chore(translate): khởi tạo <slug>`.

### action=translate n=N

1. `brief translate --n N`, rồi mở panel và chờ.
2. `orchestrate.py <slug> verify N`. Lệnh này kiểm tra:
   - có file bản dịch;
   - QA không còn `[LỖI]`;
   - trạng thái là `done`;
   - có tóm tắt trong `summaries.md`.
3. Verify chưa đạt:
   - Lần đầu: nhắc chính panel đó bằng `herdr agent prompt <name> "<các vấn đề verify in ra, sửa rồi ghi lại báo cáo>"`, rồi chờ lại.
   - Vẫn chưa đạt: đóng pane, đặt lại chương về todo bằng `progress.py <slug> set N todo`, mở panel mới làm lại từ đầu một lần.
   - Lần thứ ba vẫn hỏng: **dừng vòng lặp**, báo user.
4. Đọc mục câu hỏi trong báo cáo và quyết. Quyết định làm đổi nội dung chương N thì nhắc panel sửa trước khi đóng.
5. Đóng pane. Commit và push với message `feat(translate): dịch chương N - <tiêu đề raw>`.
6. Báo user một dòng: `#N xong — QA ok, +k thuật ngữ, q câu hỏi đã quyết`.

### action=review range=R

1. `brief review --range R`, rồi mở panel và chờ. Báo cáo review nằm ở `.herdr/reports/rv-<a>-<b>.md`.
2. Phân loại từng lỗi trong báo cáo, rồi ghi file quyết định `.herdr/tasks/decisions-<a>-<b>.md` theo mẫu dưới.
   - `nặng`: mở đúng đoạn trong raw ra đối chiếu. Reviewer đúng thì chấp nhận, sai thì bác.
   - `vừa` và `nhẹ`: chấp nhận khi rõ ràng làm câu tốt hơn mà không trái `rules.md`, `style.md` hay context. Chỉ khác về khẩu vị thì bác.
   - Đề xuất sửa context: chấp nhận khi có bằng chứng trong raw, và theo đúng mục "Quyết định".
3. Đóng pane review.
4. Có mục được chấp nhận:
   - `brief fix --range R --review-report .herdr/reports/rv-<a>-<b>.md --decisions .herdr/tasks/decisions-<a>-<b>.md`, rồi mở panel và chờ.
   - `verify R --status reviewed`. Chưa đạt thì xử lý giống bước 3 của translate.
   - Đóng pane. Commit và push với message `fix(translate): sửa chương <R> theo review`.
5. Không có mục nào được chấp nhận:
   - `progress.py <slug> set R reviewed`;
   - commit và push với message `chore(translate): review chương <R>`.

Mẫu file quyết định:

```
## Chương N
- đoạn K: chấp nhận
- đoạn K: chấp nhận, sửa thành "<câu>"
- đoạn K: bác — <lý do>

## Context
- <file>: chấp nhận/bác <đề xuất> — <lý do>

## Câu hỏi
- <câu hỏi> → <quyết định>
```

### action=finished

Chạy `progress.py <slug> stats`, rồi báo cáo cuối như mục "Báo cáo cho user".

## Quyết định

Bạn quyết thay user các câu hỏi panel đặt ra: câu hỏi trong báo cáo, mục "Cần user xác nhận" của `progress.md`, và câu hỏi panel hỏi thẳng trên màn hình. Nguyên tắc:

1. **Không đổi quyết định của user.** Đó là các mục "Tên riêng", "Thuật ngữ...", "Định dạng", "Ghi chú translator" trong `rules.md`, và "Nguyên tắc chung" trong `style.md`. Câu hỏi đòi đổi những mục này thì **dừng vòng lặp, hỏi user**.
2. **Ưu tiên nhất quán.** Giữ cái đã chốt, trừ khi raw chứng minh rõ là sai, ví dụ nhân vật hóa ra là nữ, hoặc là người lớn tuổi hơn.
3. **Dựa vào raw, không đoán.** Mở đoạn raw liên quan, và nếu cần thì cả `characters.md` và `summaries.md`, rồi mới quyết.
4. **Ghi lại mọi quyết định:**
   - sửa file context tương ứng (`glossary.md`, `pronouns.md`, `characters.md`, mục "Riêng truyện này" của `rules.md`);
   - chuyển câu hỏi sang mục "Đã quyết" bằng `orchestrate.py <slug> resolve "<đoạn chữ trong câu hỏi>" "<quyết định>"`.
5. **Quyết định làm sai các chương đã commit** (đổi thuật ngữ, đổi xưng hô từ một chương cũ):
   - ghi file quyết định chỉ có các mục context và câu hỏi;
   - mở panel fix cho các chương bị ảnh hưởng, không cần báo cáo review. Tìm các chương đó bằng cách tìm từ cũ trong `translations/<slug>/vi/`;
   - verify, rồi commit với message `fix(translate): áp dụng quyết định <tóm tắt> cho chương <R>`.

## Panel bị chặn

`wait-report.sh` trả về `blocked` hoặc `idle-no-report` thì đọc màn hình bằng `herdr pane read <pane> --source visible`.

- **Xin quyền** cho việc nằm trong phạm vi thì tự duyệt **một lần**: chọn đúng phím tương ứng với lựa chọn duyệt một lần trên màn hình rồi gửi bằng `herdr agent send-keys`. Trong phạm vi gồm:
  - chạy `python .agents/skills/novel-translate/scripts/...`;
  - đọc raw;
  - đọc hoặc ghi file trong `translations/<slug>/` và `.herdr/`.

  Việc khác (git, xóa file ngoài các thư mục trên, cài đặt, truy cập mạng...) thì từ chối, rồi báo user.
- **Hỏi về nội dung dịch**: quyết theo mục "Quyết định", trả lời bằng `herdr agent prompt <name> "<quyết định>"`, rồi chạy lại lệnh chờ.
- **Quên ghi báo cáo**: nhắc như herdr-spawn hướng dẫn.
- **Kẹt ở hộp thoại trust, login hay lỗi model**: dừng vòng lặp, báo user.

## Commit và push

Giao cho **subagent sẵn có của harness**: Claude Code dùng Agent tool, agy dùng tính năng subagent nếu có. Không có subagent thì tự chạy. Chờ subagent xong mới sang vòng tiếp. Brief cho subagent:

```
Repo: <repo root>. Chạy đúng các lệnh sau theo thứ tự, không làm gì thêm, không hỏi lại:
  git add -- translations/<slug>/
  git diff --cached --stat
  git commit -m "<message>"
  git push origin HEAD
Không có gì để commit thì báo lại và dừng.
Push bị từ chối vì remote có commit mới: chạy git pull --rebase origin <nhánh hiện tại> rồi push lại một lần.
Rebase bị conflict hoặc gặp lỗi khác: chạy git rebase --abort nếu đang rebase. Không force push. Báo lại nguyên văn lỗi.
Báo lại: hash commit, danh sách file, kết quả push.
```

- Chỉ stage `translations/<slug>/`, không bao giờ stage `.herdr/`.
- Push lỗi (sai quyền, mất mạng, conflict) thì **dừng vòng lặp**, báo user. Commit local vẫn giữ.

## Dừng

Dừng vòng lặp khi gặp một trong các trường hợp:
- `next` trả về `finished`, hoặc đã tới giới hạn user đặt;
- một chương hỏng 3 lần;
- có câu hỏi cần user quyết (nguyên tắc 1);
- push lỗi;
- panel kẹt mà bạn không tự xử lý được;
- user bảo dừng.

Trước khi dừng, đóng các pane còn mở. Đang có panel làm dở thì chờ nó xong trước, hoặc hỏi user.

## Giữ context gọn

Bạn có thể chạy hàng trăm vòng:
- Không đọc trọn bản dịch. Chỉ đọc báo cáo, output của `verify`, và đúng các đoạn raw hay đoạn dịch cần để quyết.
- Giữ một bảng theo dõi ngắn trong cuộc trò chuyện, cập nhật sau mỗi vòng:

| Vòng | Việc | Panel | Kết quả | Commit |
|---|---|---|---|---|

## Báo cáo cho user

Khi dừng, báo cáo ngắn gọn:
- tiến độ, lấy từ `progress.py stats`;
- các chương đã dịch hoặc đã review trong lần chạy này, kèm commit;
- các quyết định bạn đã đưa ra thay user, mỗi mục một dòng, để user soát lại;
- lý do dừng, và việc user cần làm (nếu có).
