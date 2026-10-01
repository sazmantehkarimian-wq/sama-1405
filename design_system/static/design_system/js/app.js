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

const dossierTabs = [...document.querySelectorAll('.tabs a[href^="#"]')];
if (dossierTabs.length) {
  const selectTab = (id) => dossierTabs.forEach((tab) => {
    const selected = tab.hash === `#${id}`;
    tab.classList.toggle('active', selected);
    if (selected) tab.setAttribute('aria-current', 'location');
    else tab.removeAttribute('aria-current');
  });
  selectTab((location.hash || dossierTabs[0].hash).slice(1));
  dossierTabs.forEach((tab) => tab.addEventListener('click', () => selectTab(tab.hash.slice(1))));
  const sections = dossierTabs.map((tab) => document.querySelector(tab.hash)).filter(Boolean);
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) selectTab(visible.target.id);
    }, { rootMargin: '-20% 0px -65% 0px', threshold: [0, .25, .5] });
    sections.forEach((section) => observer.observe(section));
  }
}
