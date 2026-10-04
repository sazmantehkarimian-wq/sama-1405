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

document.querySelectorAll('[data-report-layout]').forEach(form=>{
 const list=form.querySelector('[data-layout-list]');
 form.addEventListener('click',event=>{const button=event.target.closest('[data-move]');if(button){const row=button.closest('.report-column-item');if(button.dataset.move==='up'&&row.previousElementSibling)list.insertBefore(row,row.previousElementSibling);if(button.dataset.move==='down'&&row.nextElementSibling)list.insertBefore(row.nextElementSibling,row);}
 if(event.target.closest('[data-add-blank]')){const input=form.querySelector('[data-blank-title]'),title=input.value.trim();if(!title)return;const row=document.createElement('div');row.className='report-column-item';row.innerHTML='<span>'+title+'</span><input type="hidden" name="blank"><input type="hidden" name="layout"><button type="button" class="compact secondary" data-move="up">↑</button><button type="button" class="compact secondary" data-move="down">↓</button>';row.querySelector('[name=blank]').value=title;row.querySelector('[name=layout]').value='blank:'+title;list.append(row);input.value='';}});
 form.addEventListener('submit',()=>form.querySelectorAll('.report-column-item').forEach(row=>{const box=row.querySelector('[name=field]'),layout=row.querySelector('[name=layout]');if(box)layout.disabled=!box.checked;}));
});

document.querySelectorAll('[data-search-picker]').forEach(picker=>{
 const query=picker.querySelector('[data-picker-query]'),value=picker.querySelector('[data-picker-value]'),list=picker.querySelector('.picker-options'),options=[...picker.querySelectorAll('[data-picker-option]')];let active=-1;
 const normalize=text=>String(text||'').replace(/[۰-۹٠-٩]/g,char=>String('۰۱۲۳۴۵۶۷۸۹'.includes(char)?'۰۱۲۳۴۵۶۷۸۹'.indexOf(char):'٠١٢٣٤٥٦٧٨٩'.indexOf(char)));
 const normalized=text=>normalize(text).toLocaleLowerCase('fa').trim();
 const visible=()=>[...list.querySelectorAll('[data-picker-option]:not([hidden])')];
 const highlight=index=>{const items=visible();active=Math.max(0,Math.min(index,items.length-1));options.forEach(x=>x.classList.remove('active'));if(items[active]){items[active].classList.add('active');items[active].scrollIntoView({block:'nearest'})}};
 const search=()=>{const term=normalized(query.value);value.value='';const ranked=options.map((item,index)=>{const code=normalized(item.dataset.value),haystack=normalized(item.dataset.search||item.textContent);let rank=term===''?0:code===term?0:code.startsWith(term)?1:code.includes(term)?2:haystack.includes(term)?3:99;return{item,index,rank}});ranked.sort((a,b)=>a.rank-b.rank||a.index-b.index).forEach(({item,rank})=>{item.hidden=rank===99;list.append(item)});picker.classList.add('open');query.setAttribute('aria-expanded','true');active=-1;if(term&&visible().length)highlight(0)};
 query.addEventListener('input',search);query.addEventListener('focus',()=>{picker.classList.add('open');query.setAttribute('aria-expanded','true')});query.addEventListener('keydown',event=>{if(event.key==='ArrowDown'){event.preventDefault();highlight(active+1)}else if(event.key==='ArrowUp'){event.preventDefault();highlight(active-1)}else if(event.key==='Enter'&&visible()[active]){event.preventDefault();visible()[active].click()}else if(event.key==='Escape'){picker.classList.remove('open');query.setAttribute('aria-expanded','false')}});
 options.forEach(item=>item.addEventListener('click',()=>{value.value=item.dataset.value;query.value=item.dataset.label||item.textContent.trim();options.forEach(x=>x.setAttribute('aria-selected',x===item?'true':'false'));query.focus();picker.classList.remove('open');query.setAttribute('aria-expanded','false')}));
});
document.addEventListener('click',event=>{if(event.target.closest('[data-print]'))window.print();document.querySelectorAll('[data-search-picker].open').forEach(picker=>{if(!picker.contains(event.target)){picker.classList.remove('open');picker.querySelector('[data-picker-query]').setAttribute('aria-expanded','false')}})});
