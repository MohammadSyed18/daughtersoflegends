
const OpenAI = require("openai");
const chunks = require("./book_chunks.json");

function normalize(text){
  return (text || "").toLowerCase().replace(/[^a-z0-9\s]/g, " ");
}

function retrieve(message, limit = 5){
  const terms = new Set(normalize(message).split(/\s+/).filter(Boolean));
  const scored = chunks.map((chunk) => {
    const chunkText = normalize(chunk.text);
    let score = 0;
    for(const term of terms){
      if(term.length > 2 && chunkText.includes(term)) score += 1;
    }
    const lower = message.toLowerCase();
    for(const key of ["legendary mindset", "legacy blueprint", "execution", "faith", "god", "strategy", "delay", "fear", "purpose"]){
      if(lower.includes(key) && chunkText.includes(key)) score += 5;
    }
    return {score, chunk};
  }).filter(x => x.score > 0);

  scored.sort((a,b) => b.score - a.score);
  return (scored.length ? scored.slice(0, limit).map(x => x.chunk) : chunks.slice(0, limit));
}

function demoAnswer(message){
  const lower = message.toLowerCase();
  if(lower.includes("legendary mindset")){
    return "Based on the Daughters of Legends framework, the Legendary Mindset is more than motivation. It is a way of operating through vision, execution, strategy, faith, and legacy. Your next step is to turn the idea into one visible action today.";
  }
  if(lower.includes("execution") || lower.includes("delay")){
    return "Execution is the bridge between vision and legacy. If there is no movement, the blueprint stays only an idea. Choose the smallest aligned action and complete it today.";
  }
  if(lower.includes("fear") || lower.includes("scared")){
    return "Fearlessness does not mean fear disappears. It means fear does not get final authority over the decision. Move with faith, alignment, and one small act of obedience to the bigger vision.";
  }
  if(lower.includes("blueprint") || lower.includes("legacy")){
    return "The Legacy Blueprint is about clarity and alignment. Not every opportunity belongs in the structure. Ask whether it expands the mission, protects the legacy, and moves the vision forward.";
  }
  return "The Legacy AI Coach guides the user back to vision, execution, faith, and legacy. Name what you are building, remove one distraction, and complete one action that proves the vision is alive.";
}

exports.handler = async function(event){
  if(event.httpMethod !== "POST"){
    return { statusCode: 405, body: JSON.stringify({ error: "Method not allowed" }) };
  }

  try{
    const body = JSON.parse(event.body || "{}");
    const message = (body.message || "").trim();

    if(!message){
      return { statusCode: 400, body: JSON.stringify({ error: "Message required" }) };
    }

    const retrieved = retrieve(message, 5);
    const sources = retrieved.slice(0, 3).map(c => ({
      page: c.page || 0,
      text: (c.text || "").slice(0, 320)
    }));

    const apiKey = process.env.OPENAI_API_KEY;
    const demoMode = (process.env.DEMO_MODE || "false").toLowerCase() === "true";

    if(!apiKey || demoMode){
      return {
        statusCode: 200,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ answer: demoAnswer(message), sources, mode: "demo" })
      };
    }

    const openai = new OpenAI({ apiKey });
    const context = retrieved.map(c => `[Book page ${c.page}] ${c.text}`).join("\n\n");

    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_CHAT_MODEL || "gpt-4o-mini",
      temperature: 0.45,
      messages: [
        {
          role: "system",
          content: `You are the Daughters of Legends Legacy AI Coach.

Answer using the provided book context and Daughters of Legends themes.
Be motivational, faith-aware, clear, respectful, and action-oriented.
Do not pretend to be Kimberly B. Brown, Jim Brown, Robyn L. Charles, or any real person.
Do not invent direct quotes from the book.
If the context does not contain enough information, say the book context does not directly answer it, then offer general guidance.
Keep answers practical and concise. End with one next action step when helpful.`
        },
        {
          role: "user",
          content: `Book context:\n${context}\n\nUser question:\n${message}\n\nAnswer as the Legacy AI Coach.`
        }
      ]
    });

    const answer = completion.choices?.[0]?.message?.content || "I could not generate an answer.";

    return {
      statusCode: 200,
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ answer, sources, mode: "openai" })
    };
  } catch(error){
    return {
      statusCode: 500,
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ error: error.message || "Server error" })
    };
  }
};
