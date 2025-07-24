document.getElementById('ideaForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const niche = document.getElementById('niche').value.trim();
  const audience = document.getElementById('audience').value.trim();
  const topics = document.getElementById('topics').value.trim();
  const lang = document.getElementById('lang').value;
  const platform = document.getElementById('platform').value;

  const payload = {
    niche,
    audience,
    topics,
    language: lang,
    platform
  };

  const resultsSection = document.getElementById('results');
  resultsSection.innerHTML = '<p class="loading">⏳ Generating ideas...</p>';
  resultsSection.scrollIntoView({ behavior: 'smooth' });

  try {
    const response = await fetch('http://0.0.0.0:10000/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (data.ideas && typeof data.ideas === 'string') {
      const ideaBlocks = data.ideas
        .split(/\n?\d+\.\s+/) // Split by numbered list (e.g. "1. ", "2. ")
        .filter(Boolean)
        .map((idea, index) => {
          const [titleLine, ...descLines] = idea.trim().split('\n');
          const title = titleLine || `Topic ${index + 1}`;
          const desc = descLines.join('\n') || '';
          const fullText = `Topic ${index + 1}: ${title}\n${desc}`;

          return `
            <div class="idea-card">
              <p><strong>Topic ${index + 1}: ${title}</strong></p>
              <div class="idea-box yellow-box" id="idea-${index}">
                ${desc.replace(/\n/g, '<br>')}
              </div>
              <button class="copy-btn" onclick="copied(\`${fullText.replace(/`/g, '\\`')}\`)"> 📋 Copy</button>
            </div>
          `;
        });

      resultsSection.innerHTML = ideaBlocks.join('');
    } else {
      resultsSection.innerHTML = '<p>No ideas returned. Try different input.</p>';
    }
  } catch (err) {
    resultsSection.innerHTML = '<p>Error generating ideas. Please try again later.</p>';
    console.error('Error:', err);
    
  }
});

// ✅ Properly copies full text: title + description + hashtags
function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
    .then(() => alert("✅ Copied"))
    .catch(() => alert("Copy failed. Please try manually."));
}
