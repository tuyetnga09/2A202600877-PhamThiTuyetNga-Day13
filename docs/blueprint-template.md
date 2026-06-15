# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Cá nhân — Phạm Thị Tuyết Nga (MSSV: 2A202600877)
- [REPO_URL]: https://github.com/tuyetnga09/2A202600877-PhamThiTuyetNga-Day13
- [MEMBERS]:
  - Member A: Phạm Thị Tuyết Nga (MSSV: 2A202600877) | Role: Toàn bộ (làm cá nhân) — Logging, PII, Tracing, SLO/Alerts, Load test, Dashboard, Report & Demo
  - Member B: (không áp dụng — làm cá nhân)
  - Member C: (không áp dụng — làm cá nhân)
  - Member D: (không áp dụng — làm cá nhân)
  - Member E: (không áp dụng — làm cá nhân)

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 76
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/img/correlation-id.png (chụp 1 dòng trong data/logs.jsonl có field "correlation_id": "req-xxxxxxxx")
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/img/pii-redaction.png (chụp dòng log có "[REDACTED_EMAIL]" / "[REDACTED_CREDIT_CARD]")
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/img/trace-waterfall.png (chụp 1 trace trong Langfuse mở rộng span)
- [TRACE_WATERFALL_EXPLANATION]: Mỗi trace "run" gồm 2 span con: `rag_retrieve` (truy hồi tài liệu) và `llm_generate` (gọi mô hình). Ở trạng thái bình thường span `rag_retrieve` ~0.0s; khi bật sự cố rag_slow span này nhảy lên ~2.5s, chiếm gần như toàn bộ độ trễ của trace — đây chính là điểm định vị nguyên nhân.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/img/dashboard.png (6 panel; nguồn dữ liệu: endpoint /metrics hoặc CSV từ scripts/poll_metrics.py)
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 156ms |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | ~$0.0023/request |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/img/alert-rules.png (chụp config/alert_rules.yaml)
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Độ trễ p95 tăng vọt từ 156ms (baseline) lên 2666ms sau khi bật sự cố; error_rate và cost không đổi (loại trừ lỗi tool và cost). Dòng log `response_sent` ghi `latency_ms = 2657`.
- [ROOT_CAUSE_PROVED_BY]: (1) Log line correlation_id `req-d20a0fae` với `latency_ms=2657`; (2) Trace trên Langfuse có span `rag_retrieve` ~2.5s trong khi `llm_generate` chỉ ~0.15s → nghẽn nằm ở khâu truy hồi RAG (mock_rag.retrieve gọi time.sleep(2.5) khi STATE["rag_slow"]=True).
- [FIX_ACTION]: Tắt sự cố bằng `python scripts/inject_incident.py --scenario rag_slow --disable`; p95 trở lại ~156ms.
- [PREVENTIVE_MEASURE]: Đặt timeout cho lớp truy hồi + fallback nguồn RAG; thêm alert cảnh báo sớm `latency_p95_ms > 2000 for 10m` (dưới ngưỡng SLO 3000ms) để phát hiện trước khi vi phạm SLO.

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]
Phạm Thị Tuyết Nga (MSSV: 2A202600877) — làm cá nhân toàn bộ lab.
- [TASKS_COMPLETED]:
  - Correlation ID middleware (app/middleware.py)
  - Enrich log + PII scrubbing (app/main.py, app/logging_config.py, app/pii.py) — validate_logs đạt 100/100
  - Tracing Langfuse: cấu hình key/host (US region), thêm load_dotenv, thêm span rag_retrieve/llm_generate — xác minh 76 trace
  - SLO + alert rules đã test ngưỡng (config/slo.yaml, config/alert_rules.yaml, docs/alerts.md)
  - Load test + inject 3 kịch bản sự cố; xuất metrics ra CSV (scripts/poll_metrics.py) cho dashboard
  - Dashboard, thu thập bằng chứng, viết báo cáo & demo
- [EVIDENCE_LINK]: https://github.com/tuyetnga09/2A202600877-PhamThiTuyetNga-Day13/commits/main

### [MEMBER_B_NAME]
(không áp dụng — làm cá nhân)
- [TASKS_COMPLETED]: N/A
- [EVIDENCE_LINK]: N/A

### [MEMBER_C_NAME]
(không áp dụng — làm cá nhân)
- [TASKS_COMPLETED]: N/A
- [EVIDENCE_LINK]: N/A

### [MEMBER_D_NAME]
(không áp dụng — làm cá nhân)
- [TASKS_COMPLETED]: N/A
- [EVIDENCE_LINK]: N/A

### [MEMBER_E_NAME]
(không áp dụng — làm cá nhân)
- [TASKS_COMPLETED]: N/A
- [EVIDENCE_LINK]: N/A

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (tuỳ chọn) Định tuyến request đơn giản sang model rẻ hơn / cắt prompt; so sánh avg_cost trước-sau.
- [BONUS_AUDIT_LOGS]: (tuỳ chọn) Bật AUDIT_LOG_PATH (data/audit.jsonl) để tách log kiểm toán.
- [BONUS_CUSTOM_METRIC]: Thêm span tracing tuỳ biến (rag_retrieve, llm_generate) giúp phân tách độ trễ RAG vs LLM trong waterfall; script poll_metrics.py xuất chuỗi thời gian metrics ra CSV.
