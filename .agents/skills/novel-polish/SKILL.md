---
name: novel-polish
description: Trau chuốt văn phong các chương đã dịch cho tự nhiên, bớt văn dịch máy, qua Herdr. Mở một orchestrator agy (Gemini 4 Argon Medium). Orchestrator cho mỗi chương một panel Gemini 3.8 Flash High viết lại, cứ 3 chương thì một panel Gemini 4 Argon Medium review và sửa lại; 3 vòng như vậy là một phase 9 chương. Dùng khi user bảo "trau chuốt văn phong", "sửa lại văn cho tự nhiên", "bản dịch máy móc quá", "polish chương N–M".
---

# Trau chuốt văn phong

Dùng cho các chương **đã dịch và review** nhưng văn còn cứng, đọc ra là truyện dịch. Skill này không dịch mới.

## Cấu trúc một phase

```
manager (bạn) ──► orchestrator agy (gemini-4-argon-medium)
                    vòng 1: pl-a, pl-a+1, pl-a+2 (gemini-3.8-flash-high, mỗi panel 1 chương)
                            ──► plr-a-(a+2) (gemini-4-argon-medium, review + sửa 3 chương)
                    vòng 2, vòng 3: như trên
                  ──► báo cáo ──► manager review, sửa, commit
```

- Mỗi panel con xong thì orchestrator kiểm tra phạm vi và QA, rồi commit và push (`style(translate): ...`).
- Panel trau chuốt **không đổi thuật ngữ hay cặp xưng hô đã chốt**, chỉ đề xuất. Panel được thêm quy luật văn phong vào mục "Lỗi văn dịch máy cần tránh" của `style.md` và sửa lỗi nhỏ trong `characters.md`.
- Panel review nhận "nhận xét chung về lỗi lặp lại". Orchestrator chép nhận xét đó vào brief của các panel trau chuốt ở vòng sau.

## Chạy một phase

Trong Herdr, từ repo root:

```
bash .agents/skills/novel-polish/scripts/phase.sh <slug> <chương bắt đầu> [--name orch-pl] [--count 9] [--cycle 3] [--polish-model M] [--review-model M]
bash .agents/skills/herdr-spawn/scripts/wait-report.sh <name> --idle-grace 3600 --interval 60 --timeout 21600000
```

- Lệnh chờ chạy ở chế độ nền. Một phase thường mất vài giờ.
- `phase.sh` gọi `gen_briefs.py` để sinh brief vào `.herdr/tasks/`:
  - `pl-NNN.md` cho từng chương;
  - `plr-AAA-BBB.md` cho từng vòng, còn chừa `__BASE__` để orchestrator điền;
  - `orch-pl-AAA-BBB.md` cho orchestrator, kèm file `.base` ghi commit gốc.

  Sau đó nó đóng pane cũ cùng tên và spawn orchestrator. Chương chưa dịch trong khoảng sẽ tự bị bỏ qua.
- Tên mặc định là `orch-pl`. Chạy song song nhiều truyện thì đặt `--name` riêng cho từng truyện.
- Truyện chưa có mục "Lỗi văn dịch máy cần tránh" trong `context/style.md` thì nên thêm trước. Xem bản mẫu trong `translations/the-unwanted-undead-adventurer/context/style.md`. Nếu chưa có, brief trau chuốt dùng danh sách rút gọn ở cuối brief.

## Sau mỗi phase (manager)

1. Đọc báo cáo `.herdr/reports/<name>.md`: đánh giá chất lượng từng chương, lỗi lặp lại, đề xuất đổi thuật ngữ hay xưng hô.
2. Kiểm tra phạm vi: `git diff --name-only $(cat .herdr/tasks/orch-pl-AAA-BBB.base)..origin/main` chỉ được có `translations/<slug>/` và `index.json`, không có file trong `vi/images/`.
3. `python .agents/skills/novel-orchestrator/scripts/orchestrate.py <slug> verify A-B --status reviewed`.
4. Đọc mẫu vài đoạn đã sửa và so với raw. Lỗi văn phong lặp lại thì tự sửa, và bổ sung vào `style.md` nếu là quy luật chung.
5. Đề xuất đổi thuật ngữ hay xưng hô thì quyết theo mục "Quyết định" của `novel-orchestrator`. Áp dụng cho mọi chương bị ảnh hưởng, hoặc đưa user quyết nếu đụng vào quyết định của user.
6. Commit và push phần đã sửa. Đóng pane orchestrator.

## Dừng giữa chừng

`herdr agent prompt <name> "Manager: dừng ngay..."`. Orchestrator agy có thể bỏ qua lời nhắn trong lúc đang chờ panel con. Nếu nó vẫn mở panel mới thì đóng thẳng cả pane con lẫn pane orchestrator bằng `herdr pane close`, rồi kiểm tra `git status` xem có thay đổi dở dang không.
