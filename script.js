
const platformButton = document.querySelector('.platform-button');
const platformDrawer = document.querySelector('.platform-drawer');
if(platformButton && platformDrawer){
  platformButton.addEventListener('click', () => platformDrawer.classList.toggle('open'));
}
const form = document.querySelector('#aiForm');
const input = document.querySelector('#aiInput');
const log = document.querySelector('#chatLog');
function reply(msg){
  const t = msg.toLowerCase();
  if(t.includes('motivat') || t.includes('tired')) return "Start with one promise you can keep today. Legacy is built by repeated action, not one perfect moment.";
  if(t.includes('journal')) return "Journal prompt: What lesson from your family, father, mentor, or life experience still deserves to live through your actions?";
  if(t.includes('goal') || t.includes('discipline')) return "Make the goal smaller. Choose the next visible action, schedule it, and protect that time.";
  if(t.includes('creative') || t.includes('music')) return "Creativity carries memory. Choose one sound, story, or image and turn it into something someone else can feel.";
  return "Name what you are carrying today, then choose one faithful next step. What is the smallest action that moves the legacy forward?";
}
function add(text,type='ai'){
  if(!log) return;
  const d=document.createElement('div'); d.className='bubble '+type; d.textContent=text; log.appendChild(d); log.scrollTop=log.scrollHeight;
}
if(form && input){
  form.addEventListener('submit', e => {e.preventDefault(); const m=input.value.trim(); if(!m) return; add(m,'user'); input.value=''; setTimeout(()=>add(reply(m),'ai'),250);});
}
document.querySelectorAll('[data-prompt]').forEach(b=>b.addEventListener('click',()=>{const m=b.dataset.prompt; add(m,'user'); setTimeout(()=>add(reply(m),'ai'),250);}));
