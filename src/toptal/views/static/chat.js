// Client-side chat: keeps history in the browser, streams replies over SSE (fetch + POST).
const history = [];
const log = document.getElementById("log");

function add(cls, text) {
  const d = document.createElement("div");
  d.className = cls;
  d.textContent = text;
  log.appendChild(d);
  return d;
}

document.getElementById("f").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = document.getElementById("q");
  const text = q.value.trim();
  if (!text) return;
  q.value = "";
  add("user", "You: " + text);
  history.push({ role: "user", content: text });
  const out = add("assistant", "");
  let answer = "";
  const provider = document.getElementById("provider").value || null;

  const res = await fetch("/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages: history, provider }),
  });
  if (!res.ok) {
    out.textContent = "Error: " + (await res.text());
    history.pop();
    return;
  }

  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop();
    for (const p of parts) {
      const data = p.replace(/^data: /, "");
      if (data === "[DONE]") continue;
      const msg = JSON.parse(data);
      if (msg.error) { out.textContent += "\n[error: " + msg.error + "]"; continue; }
      answer += msg.delta;
      out.textContent = answer;
    }
  }
  history.push({ role: "assistant", content: answer });
});
