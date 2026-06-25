
const messages = document.querySelector("#messages");
const form = document.querySelector("#chatForm");
const input = document.querySelector("#messageInput");
const sourcesBox = document.querySelector("#sources");
const modeBadge = document.querySelector("#modeBadge");

function addMessage(text, type = "ai"){
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function demoAnswer(message){
  const lower = message.toLowerCase();
  if(lower.includes("legendary mindset")){
    return {answer:"Based on the Daughters of Legends framework, the Legendary Mindset is more than motivation. It is a way of operating through vision, execution, strategy, faith, and legacy. Your next step is to turn the idea into one visible action today.",sources:[{page:11,text:"The Legendary Mindset is a system of thinking and operating built on vision, blueprint, execution, strategy, faith, legacy, scale, and identity."},{page:22,text:"The Legendary Mindset principles include fearlessness, consistency, discipline, patience, awareness, and adaptability."}],mode:"demo"};
  }
  if(lower.includes("execution") || lower.includes("delay")){
    return {answer:"The book-based coaching idea treats execution as the bridge between vision and legacy. If there is no movement, the blueprint stays only an idea. Your next step is to choose the smallest aligned action and complete it today.",sources:[{page:43,text:"If there is no movement, there is no blueprint. No movement, no legacy. No execution, no purpose."},{page:34,text:"The Legacy Blueprint becomes real through clarity, filtering, and execution."}],mode:"demo"};
  }
  if(lower.includes("fear") || lower.includes("scared")){
    return {answer:"Fearlessness does not mean fear disappears. It means fear does not get final authority over the decision. Move with faith, alignment, and one small act of obedience to the bigger vision.",sources:[{page:22,text:"The Legendary Mindset is built on fearlessness, determination, consistency, discipline, focus, patience, awareness, and adaptability."}],mode:"demo"};
  }
  if(lower.includes("blueprint") || lower.includes("legacy")){
    return {answer:"The Legacy Blueprint is about clarity and alignment. Not every opportunity belongs in the structure. Ask: does this expand the mission, protect the legacy, and move the vision forward?",sources:[{page:34,text:"The Legacy Blueprint becomes real through clarity, filtering, and execution."},{page:43,text:"Execution separates vision from imagination."}],mode:"demo"};
  }
  return {answer:"The Legacy AI Coach would guide the user back to vision, execution, faith, and legacy. A strong next step is to name what you are building, remove one distraction, and complete one action that proves the vision is alive.",sources:[{page:11,text:"The Legendary Mindset is a system of thinking and operating built on vision, execution, strategy, faith, and legacy."}],mode:"demo"};
}

function showSources(sources){
  if(!sources || sources.length === 0){ sourcesBox.innerHTML = ""; return; }
  const visibleSources = sources.slice(0, 2);
  const hiddenSources = sources.slice(2);
  sourcesBox.innerHTML = `
    <div class="sources-header"><strong>Book context used</strong><span>${sources.length} source${sources.length === 1 ? "" : "s"}</span></div>
    <div class="sources-visible">${visibleSources.map(src => `<div class="source">Page ${src.page}: ${src.text}</div>`).join("")}</div>
    ${hiddenSources.length > 0 ? `<button id="showMoreSources" class="show-more-sources" type="button">Show ${hiddenSources.length} more source${hiddenSources.length === 1 ? "" : "s"}</button><div id="hiddenSources" class="sources-hidden">${hiddenSources.map(src => `<div class="source">Page ${src.page}: ${src.text}</div>`).join("")}</div>` : ""}
  `;
  const btn = document.querySelector("#showMoreSources");
  const hidden = document.querySelector("#hiddenSources");
  if(btn && hidden){
    btn.addEventListener("click", () => {
      const open = hidden.classList.toggle("open");
      btn.textContent = open ? "Show fewer sources" : `Show ${hiddenSources.length} more source${hiddenSources.length === 1 ? "" : "s"}`;
    });
  }
}

async function sendMessage(message){
  addMessage(message, "user");
  addMessage("Thinking...", "ai");
  const thinking = messages.lastElementChild;
  try{
    const response = await fetch(`/.netlify/functions/chat`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({message})});
    if(!response.ok) throw new Error("Backend unavailable");
    const data = await response.json();
    thinking.textContent = data.answer;
    modeBadge.textContent = data.mode === "openai" ? "Live AI" : "Demo Mode";
    showSources(data.sources);
  }catch(error){
    const data = demoAnswer(message);
    thinking.textContent = data.answer;
    modeBadge.textContent = "Demo Mode";
    showSources(data.sources);
  }
}

if(form && input){
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if(!message) return;
    input.value = "";
    sendMessage(message);
  });
}
document.querySelectorAll("[data-prompt]").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});
