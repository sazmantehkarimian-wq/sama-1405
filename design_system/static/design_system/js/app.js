document.addEventListener("input", (event) => {
  if (!event.target.matches("[data-option-filter]")) return;
  const query = event.target.value.trim().toLocaleLowerCase("fa");
  event.target.closest(".multi-select-options").querySelectorAll("[data-option]").forEach((option) => {
    option.hidden = query && !option.textContent.toLocaleLowerCase("fa").includes(query);
  });
});

document.addEventListener("change", (event) => {
  if (event.target.type !== "file") return;
  const name = event.target.files.length ? event.target.files[0].name : "فایلی انتخاب نشده است";
  const output = event.target.closest(".file-control")?.querySelector(".file-name");
  if (output) output.textContent = name;
});

document.querySelectorAll(".bar-fill[data-percent]").forEach((bar) => {
  const percent = Math.max(0, Math.min(100, Number(bar.dataset.percent) || 0));
  bar.style.inlineSize = `${percent}%`;
});

/* Administrative dropdowns: one open menu at a time, close on outside click/Escape. */
document.addEventListener("toggle", (event) => {
  const current = event.target;
  if (!(current instanceof HTMLDetailsElement) || !current.open) return;
  document.querySelectorAll(".topnav details[open], .account[open]").forEach((item) => {
    if (item !== current) item.removeAttribute("open");
  });
}, true);

document.addEventListener("click", (event) => {
  document.querySelectorAll(".topnav details[open], .account[open]").forEach((item) => {
    if (!item.contains(event.target)) item.removeAttribute("open");
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  document.querySelectorAll("details[open]").forEach((item) => item.removeAttribute("open"));
});

/* Prevent accidental double POSTs while keeping validation and normal GET forms intact. */
document.addEventListener("submit", (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement) || form.method.toLowerCase() !== "post") return;
  if (!form.checkValidity() || form.dataset.submitting === "1") {
    if (form.dataset.submitting === "1") event.preventDefault();
    return;
  }
  form.dataset.submitting = "1";
  form.setAttribute("aria-busy", "true");
  form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach((button) => {
    button.disabled = true;
    if (button.tagName === "BUTTON" && !button.dataset.originalText) {
      button.dataset.originalText = button.textContent;
      button.textContent = "در حال ثبت…";
    }
  });
});
