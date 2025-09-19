const API_BASE = "http://127.0.0.1:8000";

async function fetchSchedule() {
  const res = await fetch(`${API_BASE}/schedule`);
  const data = await res.json();
  const list = document.getElementById("scheduleList");
  list.innerHTML = "";
  data.schedule.forEach(item => {
    const li = document.createElement("li");
    li.innerHTML = `${item.title} - ${item.datetime} ${item.note ? "(" + item.note + ")" : ""} 
      <button onclick="deleteItem(${item.id})">❌</button>`;
    list.appendChild(li);
  });
}

async function addSchedule(e) {
  e.preventDefault();
  const title = document.getElementById("title").value;
  const datetime = document.getElementById("datetime").value;
  const note = document.getElementById("note").value;

  const newItem = {
    id: Date.now(), // simple unique id
    title,
    datetime,
    note
  };

  await fetch(`${API_BASE}/schedule`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(newItem)
  });

  document.getElementById("scheduleForm").reset();
  fetchSchedule();
}

async function deleteItem(id) {
  await fetch(`${API_BASE}/schedule/${id}`, {method: "DELETE"});
  fetchSchedule();
}

document.getElementById("scheduleForm").addEventListener("submit", addSchedule);

fetchSchedule();
