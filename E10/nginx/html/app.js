const form = document.getElementById('personForm');
const output = document.getElementById('output');
const loadBtn = document.getElementById('loadBtn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  const res = await fetch('/person/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  output.textContent = JSON.stringify(data, null, 2);
  if (res.ok) {
    form.reset();
  }
});

loadBtn.addEventListener('click', async () => {
  const res = await fetch('/persons/');
  const data = await res.json();
  output.textContent = JSON.stringify(data, null, 2);
});
