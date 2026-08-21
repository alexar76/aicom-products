from fastapi import APIRouter, Response

router = APIRouter()

@router.get("/api/embed.js")
async def get_embed_script():
    script = '''
    (function() {
      const container = document.currentScript.parentElement;
      const shadowHost = document.createElement('div');
      shadowHost.id = 'sentinel-widget-' + Math.random().toString(36).substr(2, 9);
      container.appendChild(shadowHost);
      const shadow = shadowHost.attachShadow({mode: 'open'});
      shadow.innerHTML = `
        <style>
          :host { display: block; font-family: 'Inter', sans-serif; background: #111820; color: #e8eef2; border-radius: 12px; padding: 1rem; border: 1px solid #263340; }
          .sld-widget { text-align: center; }
          .sld-status-ring { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #00d4aa; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-weight: bold; font-size: 1.2rem; }
          .sld-hazards { display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap; }
          .sld-hazard { background: #18222b; border: 1px solid #263340; border-radius: 8px; padding: 0.5rem 1rem; }
          .sld-btn { background: #00d4aa; color: #0a0f14; border: none; padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; font-weight: 600; }
        </style>
        <div class="sld-widget">
          <div class="sld-status-ring">?</div>
          <p>Check safety</p>
          <button class="sld-btn" id="sld-check">Check my location</button>
          <div class="sld-hazards"></div>
        </div>
      `;
      const button = shadow.querySelector('#sld-check');
      button.addEventListener('click', () => {
        const lat = prompt('Enter latitude:');
        const lon = prompt('Enter longitude:');
        if (lat && lon) {
          fetch(`/api/advisory?lat=${parseFloat(lat).toFixed(1)}&lon=${parseFloat(lon).toFixed(1)}`)
            .then(r => r.json())
            .then(data => {
              const hazardsDiv = shadow.querySelector('.sld-hazards');
              hazardsDiv.innerHTML = '';
              data.hazards.forEach(h => {
                const div = document.createElement('div');
                div.className = 'sld-hazard';
                div.textContent = `${h.type}: ${h.level}`;
                hazardsDiv.appendChild(div);
              });
              shadow.querySelector('.sld-status-ring').textContent = data.overall.level;
            });
        }
      });
    })();
    '''
    return Response(content=script, media_type="application/javascript")
