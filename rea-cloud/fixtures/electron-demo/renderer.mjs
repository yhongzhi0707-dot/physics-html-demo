import { normalizeQuery } from './utils.mjs';

document.querySelector('#search').addEventListener('input', async (event) => {
  const results = await window.demo.search(normalizeQuery(event.target.value));
  document.querySelector('#results').textContent = JSON.stringify(results);
});
