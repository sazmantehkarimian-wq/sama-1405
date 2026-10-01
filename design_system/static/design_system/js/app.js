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
