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
   - panel chạy với `--dangerously-skip-permissions`, nên không có hộp thoại xin quyền. Bù lại, sau mỗi panel phải kiểm tra phạm vi (mục "Mở panel và chờ").
3. Xác định với user:
   - `slug` của truyện;
   - nếu chưa khởi tạo thì cần thêm thư mục raw và tên truyện;
   - giới hạn: dịch tới chương nào (`--until N`) hoặc bao nhiêu chương.

   User không nói giới hạn thì mặc định dịch 9 chương (3 vòng review), rồi dừng và báo cáo.

## Vòng lặp

```
next ──► init ──► [panel] khởi tạo ──► duyệt context ──► commit + push
     ├─► repair R ──► [panel] sửa lỗi QA ──► verify ──► commit + push
     ├─► fix-context ──► lint ──► tự sửa context / [panel] viết tóm tắt thiếu ──► commit + push
     ├─► translate N ──► [panel] dịch ──► verify ──► quyết câu hỏi ──► commit + push
     ├─► review a-b ──► [panel] review ──► phân loại lỗi ──► [panel] sửa ──► verify ──► commit + push
     └─► finished ──► báo cáo cuối
```

Mỗi vòng:

1. `orchestrate.py <slug> next --until <N>`. Script in ra một dòng: `action=init`, `action=repair range=<R>`, `action=fix-context`, `action=translate n=<N>`, `action=review range=<R>` hoặc `action=finished`, kèm `open_questions=<k>`.
2. Nếu `open_questions` > 0: chạy `orchestrate.py <slug> questions` rồi quyết từng câu (mục "Quyết định") **trước khi** mở panel mới.
3. Làm theo action ở các mục dưới, rồi quay lại bước 1.

Làm **tuần tự**: mỗi lúc chỉ một panel làm việc, và commit xong mới mở panel tiếp theo. Panel sau đọc context do panel trước cập nhật. Nếu commit trong lúc panel khác đang sửa file thì sẽ commit dính phần làm dở.

### Mở panel và chờ

```
python .agents/skills/novel-orchestrator/scripts/orchestrate.py <slug> brief <kind> [...]
# in ra: name=<name> task=<file brief> report=<file báo cáo>
bash .agents/skills/herdr-spawn/scripts/spawn.sh <name> agy --task-file <task> -- --model gemini-3.8-flash-medium --dangerously-skip-permissions
bash .agents/skills/herdr-spawn/scripts/wait-report.sh <name> --timeout 3600 --idle-grace 120
```

- Lệnh chờ chạy ở chế độ nền của harness, giống herdr-spawn bước 3.
- Mỗi lần mở panel là một session mới, nên context luôn sạch.
- **Kiểm tra phạm vi**, vì panel chạy không xin quyền. Trước khi mở panel, ghi lại `git log -1 --format=%h` và `git status --short`. Sau khi panel xong:
  - hash commit phải giữ nguyên, tức là panel không tự commit;
  - so với `git status --short` lúc trước, dòng mới hoặc dòng thay đổi chỉ được nằm trong `translations/<slug>/`. Thay đổi đã có từ trước không tính;
  - không có file nào trong `translations/<slug>/vi/images/` bị sửa (` M`) hay xoá (` D`). Panel không được đụng vào ảnh; ghi đè ảnh đã push còn làm GitHub Action báo lỗi (`chapter-image-guide.md` mục 3).

  Sai một trong hai thì **dừng vòng lặp**, báo user kèm danh sách thay đổi. Không tự revert.
- Đường dẫn báo cáo luôn lấy đúng giá trị `report=` mà lệnh `brief` in ra (tên có đệm 3 chữ số, vd `rv-001-003`). Không tự ghép tên.
- Xử lý xong báo cáo thì đóng pane bằng `herdr pane close <pane>`.
- Tên panel trùng tên một panel đang sống (vì chạy lại) thì đóng panel cũ trước.

### action=init

1. `brief init --raw "<thư mục raw>" --title "<tên truyện>"`, rồi mở panel và chờ.
2. Đọc báo cáo, rồi đọc lướt các file context trong `translations/<slug>/context/` (`style.md`, `characters.md`, `pronouns.md`, `glossary.md`). Kiểm tra:
   - các chương `skip` có trùng thật không;
   - đại từ người kể dùng cho nhân vật chính có hợp giọng truyện không;
   - xưng hô các cặp chính có hợp tuổi và quan hệ không;
   - thuật ngữ có theo `rules.md` không.

   Sai thì tự sửa file context. Câu hỏi trong báo cáo thì quyết theo mục "Quyết định".
3. Đóng pane. Commit và push với message `chore(translate): khởi tạo <slug>`.

### action=repair range=R

Các chương đã dịch nhưng giờ QA báo `[LỖI]`, thường vì script QA vừa được sửa và bắt được lỗi cũ.

1. Chạy `qa_check.py <slug> R` để xem lỗi. Lỗi thiếu đoạn hay gộp đoạn thì mở raw và bản dịch, tìm đúng đoạn bị thiếu hoặc bị gộp.
2. Ghi file quyết định: với mỗi chương, nêu lỗi QA và cách sửa (vd "đoạn raw K chưa được dịch: dịch bổ sung thành một đoạn riêng"; "đoạn K gộp hai đoạn raw: tách lại").
3. `brief fix --range R --decisions <file> --keep-status`, rồi mở panel và chờ.
4. `verify R --status translated`. Chưa đạt thì xử lý giống bước 3 của translate.
5. Đóng pane. Commit và push với message `fix(translate): sửa lỗi QA chương <R>`.

### action=fix-context

`lint_context.py` báo `[LỖI]` trong các file context.

1. Chạy `python .agents/skills/novel-translate/scripts/lint_context.py <slug>` để xem lỗi.
2. Lỗi trùng dòng và lỗi tên trong `pronouns.md`: tự sửa file context. Gộp dòng trùng, giữ bản dịch đang được dùng trong các chương. Sửa tên cho khớp `characters.md`.
3. Thiếu tóm tắt chương: ghi file quyết định "viết mục `## N` trong `summaries.md` theo mẫu bước B4", rồi chạy `brief fix --range <các chương thiếu> --decisions <file> --keep-status`, mở panel và chờ.
4. Chạy lại lint cho tới khi hết `[LỖI]`. Commit và push với message `fix(translate): sửa context`.

### action=translate n=N

1. `brief translate --n N`, rồi mở panel và chờ.
2. `orchestrate.py <slug> verify N`. Lệnh này kiểm tra:
   - có file bản dịch;
   - QA không còn `[LỖI]`;
   - trạng thái là `done`;
   - có tóm tắt trong `summaries.md`.
3. Verify chưa đạt:
   - Lần đầu: nhắc chính panel đó bằng `herdr agent prompt <name> "<các vấn đề verify in ra, sửa rồi ghi lại báo cáo>"`, rồi chờ lại. **Xoá file báo cáo cũ của panel trước khi nhắc** (`rm .herdr/reports/<name>.md`), nếu không `wait-report.sh` thấy dòng `STATUS: done` cũ và thoát ngay. Áp dụng cho mọi lần nhắc lại một panel đã báo xong.
   - Vẫn chưa đạt: đóng pane, đặt lại chương về todo bằng `progress.py <slug> set N todo`, mở panel mới làm lại từ đầu một lần.
   - Lần thứ ba vẫn hỏng: **dừng vòng lặp**, báo user.
4. Đọc mục câu hỏi trong báo cáo và quyết. Panel thường chỉ ghi câu hỏi vào báo cáo mà không ghi vào `progress.md`. Câu như vậy thì ghi thẳng vào "Đã quyết" bằng `orchestrate.py <slug> resolve "[#N] <câu hỏi>" "<quyết định>" --new`. Quyết định làm đổi nội dung chương N thì nhắc panel sửa trước khi đóng.
5. Đóng pane. Commit và push với message `feat(translate): dịch chương N - <tiêu đề raw>`.
6. Báo user một dòng: `#N xong — QA ok, +k thuật ngữ, q câu hỏi đã quyết`.

### action=review range=R

1. `brief review --range R`, rồi mở panel và chờ. Báo cáo review nằm ở đường dẫn `report=` mà lệnh `brief` in ra.
2. Phân loại từng lỗi trong báo cáo, rồi ghi file quyết định `.herdr/tasks/decisions-<a>-<b>.md` theo mẫu dưới.
   - `nặng`: mở đúng đoạn trong raw ra đối chiếu. Reviewer đúng thì chấp nhận, sai thì bác.
   - `vừa` và `nhẹ`: chấp nhận khi rõ ràng làm câu tốt hơn mà không trái `rules.md`, `style.md` hay context. Chỉ khác về khẩu vị thì bác.
   - Đề xuất sửa context: chấp nhận khi có bằng chứng trong raw, và theo đúng mục "Quyết định".
3. Đóng pane review.
4. Có mục được chấp nhận:
   - `brief fix --range R --review-report <report của panel review> --decisions .herdr/tasks/decisions-<a>-<b>.md`, rồi mở panel và chờ.
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
     Chuỗi có dấu `"` mà gọi từ PowerShell 5.1 thì ghi câu hỏi vào dòng 1, quyết định vào các dòng sau của một file UTF-8 trong `.herdr/tasks/`, rồi gọi `resolve --args-file <file>` (thêm `--new` nếu cần).
5. **Quyết định làm sai các chương đã commit** (đổi thuật ngữ, đổi xưng hô từ một chương cũ):
   - ghi file quyết định chỉ có các mục context và câu hỏi;
   - mở panel fix cho các chương bị ảnh hưởng bằng `brief fix --range R --decisions <file> --keep-status`, không cần báo cáo review. Tìm các chương đó bằng cách tìm từ cũ trong `translations/<slug>/vi/`. Cờ `--keep-status` giữ nguyên trạng thái `done`, để không làm vỡ lô review 3 chương sắp tới;
   - `verify R --status translated`, rồi commit và push với message `fix(translate): áp dụng quyết định <tóm tắt> cho chương <R>`.

## Panel bị chặn

`wait-report.sh` trả về `blocked` hoặc `idle-no-report` thì đọc màn hình bằng `herdr pane read <pane> --source visible`.

- **Vẫn hiện hộp thoại xin quyền** (cờ skip không có tác dụng) thì đọc kỹ yêu cầu. Việc nằm trong phạm vi thì duyệt một lần: chọn đúng phím của lựa chọn duyệt một lần trên màn hình, gửi bằng `herdr agent send-keys`. Trong phạm vi gồm:
  - chạy `python .agents/skills/novel-translate/scripts/...`;
  - đọc raw;
  - đọc hoặc ghi file trong `translations/<slug>/` và `.herdr/`.

  Việc khác (git, xóa file ngoài các thư mục trên, cài đặt, truy cập mạng...) thì từ chối, rồi báo user.
- **Hỏi về nội dung dịch**: quyết theo mục "Quyết định", trả lời bằng `herdr agent prompt <name> "<quyết định>"`, rồi chạy lại lệnh chờ. Gọi từ PowerShell 5.1 thì nội dung không được chứa dấu `"`: ghi câu trả lời vào một file trong `.herdr/tasks/` rồi gọi qua Git Bash, `bash -c 'herdr agent prompt <name> "$(cat <file>)"'`, hoặc diễn đạt lại để không cần dấu `"`.
- **Quên ghi báo cáo**: nhắc như herdr-spawn hướng dẫn.
- **`spawn.sh` thất bại** (exit khác 0, hoặc in `status=failed`): pane vẫn bị giữ lại để xem lỗi. Đọc màn hình, đóng pane đó, rồi mới spawn lại. Không chạy `wait-report.sh` cho lần spawn hỏng. Khi gộp hai lệnh: trong bash nối bằng `&&`; PowerShell 5.1 không có `&&`, dùng `A; if ($?) { B }`. Không nối bằng `;` trần.
- **Lỗi khởi tạo model ngay khi mở** (vd `failed to construct executor`, `plan model not specified`): đóng pane, mở lại một lần với cùng brief. Vẫn lỗi thì dừng vòng lặp, báo user.
- **Kẹt ở hộp thoại trust hay login**: dừng vòng lặp, báo user.
- **User nhắn thẳng vào pane của bạn** một yêu cầu mới (vd thêm quy tắc định dạng): coi như quyết định của user. Ghi vào `rules.md`, áp dụng cho các chương đã dịch theo nguyên tắc 5 của mục "Quyết định", và ghi rõ trong báo cáo cuối là do user yêu cầu.

## Commit và push

Giao cho **subagent sẵn có của harness**: Claude Code dùng Agent tool, agy dùng tính năng subagent nếu có. Không có subagent thì tự chạy. Chờ subagent xong mới sang vòng tiếp.

Việc này chỉ là chạy vài lệnh git cố định, nên luôn đặt subagent ở **mức effort thấp nhất** mà harness cho phép (vd tham số `effort: "low"` của Agent tool). Harness không cho chọn effort thì dùng mặc định.

Brief cho subagent:

```
Repo: <repo root>. Chạy đúng các lệnh sau theo thứ tự, không làm gì thêm, không hỏi lại:
  git add -- translations/<slug>/
  python scripts/build_index.py
  git add -- index.json
  git diff --cached --stat
  git commit -m "<message>"
  git push origin HEAD
build_index.py thoát với mã khác 0 thì không commit, báo lại nguyên văn lỗi và dừng.
Không có gì để commit thì báo lại và dừng.
Push bị từ chối vì remote có commit mới: chạy git pull --rebase origin <nhánh hiện tại> rồi push lại một lần.
Rebase bị conflict hoặc gặp lỗi khác: chạy git rebase --abort nếu đang rebase. Không force push. Báo lại nguyên văn lỗi.
Báo lại: hash commit, danh sách file, kết quả push.
```

- Chỉ stage `translations/<slug>/` và `index.json`, không bao giờ stage `.herdr/`.
- `index.json` (spec: `index-json-spec.md`) liệt kê truyện và chương cho app đọc. Chạy `build_index.py` **sau** `git add translations/<slug>/` để `sha` lấy đúng nội dung sắp commit. Nội dung không đổi thì script giữ nguyên file, không sinh thay đổi. GitHub Action `build-index.yml` cũng tự sinh lại khi push, nên commit thiếu `index.json` vẫn được sửa trên `main`.
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
