# معماری

SAMA Next یک modular monolith با Django و SQLite است. جریان اجباری: Authority → `RawCell` lossless evidence → registry/validation → typed domain models → services/queries → UI/reporting. `domains/` مالک مدل‌های رابطه‌ای، `services/` مالک قواعد یکتا، `queries/` مالک query schema، `reporting/` مالک خروجی رسمی و `ui/` شامل controllerهای نازک است. هیچ runtime یا application code قدیمی استفاده نشده است.
