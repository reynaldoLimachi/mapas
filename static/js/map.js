// map.js - búsqueda, filtros, markers, OSRM ruta
let map = L.map('map').setView([-16.5, -68.15], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

const icons = {
  hospital: L.icon({ iconUrl: '/static/img/hospital.png', iconSize: [32,32] }),
  centro:   L.icon({ iconUrl: '/static/img/centro.png', iconSize: [32,32] }),
  posta:    L.icon({ iconUrl: '/static/img/posta.png', iconSize: [32,32] })
};

let markersLayer = L.layerGroup().addTo(map);
let rutaLayer = null;

const searchInput = document.getElementById('searchInput');
const tipoCheckboxes = document.querySelectorAll('.tipo-filter');
const resultsPanel = document.getElementById('results');
const btnClear = document.getElementById('btnClear');

function debounce(fn, delay) {
  let t;
  return function(...args) {
    clearTimeout(t);
    t = setTimeout(() => fn.apply(this, args), delay);
  }
}

function getSelectedTipos() {
  const arr = [];
  tipoCheckboxes.forEach(cb => { if (cb.checked) arr.push(cb.value); });
  return arr;
}

function renderResults(data) {
  markersLayer.clearLayers();
  resultsPanel.innerHTML = '';

  if (!data || data.length === 0) {
    resultsPanel.innerHTML = '<div style="padding:8px;">No se encontraron centros.</div>';
    return;
  }

  data.forEach(c => {
    const icon = icons[c.tipo] || icons['centro'];
    const marker = L.marker([c.lat, c.lon], { icon }).addTo(markersLayer);
    marker.bindPopup(`<b>${c.nombre}</b><br>${c.direccion}<br><small>${c.tipo}</small>`);

    marker.on('click', async () => {
      map.setView([c.lat, c.lon], 15);
      // si geolocalizamos, calcular ruta
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (pos) => {
          const start = [pos.coords.latitude, pos.coords.longitude];
          const end = [c.lat, c.lon];
          await obtenerRuta(start, end, c.nombre, c.id);
        }, (err) => {
          // si no da permiso, solo abrir popup y registrar selección
          recordSearch({ center_id: c.id, query: searchInput.value.trim(), filtros: getSelectedTipos() });
        });
      } else {
        recordSearch({ center_id: c.id, query: searchInput.value.trim(), filtros: getSelectedTipos() });
      }
    });

    const div = document.createElement('div');
    div.className = 'result-item';
    div.innerHTML = `<strong>${c.nombre}</strong><br><small>${c.tipo} — ${c.direccion}</small>`;
    div.onclick = () => {
      map.setView([c.lat, c.lon], 15);
      marker.openPopup();
      // disparar click del marker (que calcula ruta)
      marker.fire('click');
    };
    resultsPanel.appendChild(div);
  });
}

async function buscar() {
  const name = searchInput.value.trim();
  const tipos = getSelectedTipos().join(',');
  const url = `/map/api/search?name=${encodeURIComponent(name)}&tipos=${encodeURIComponent(tipos)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    renderResults(data);
  } catch (err) {
    console.error("Error en búsqueda:", err);
  }
}

const debouncedBuscar = debounce(buscar, 350);

searchInput.addEventListener('input', debouncedBuscar);
tipoCheckboxes.forEach(cb => cb.addEventListener('change', debouncedBuscar));
btnClear.addEventListener('click', () => {
  searchInput.value = '';
  tipoCheckboxes.forEach(cb => cb.checked = true);
  debouncedBuscar();
});
window.addEventListener('load', () => buscar());

// graba búsquedas / selecciones
async function recordSearch(payload) {
  try {
    await fetch('/map/api/record_search', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
  } catch (err) {
    console.error("Error registrando búsqueda:", err);
  }
}

// obtiene ruta desde backend (que llama a OSRM) y dibuja en el mapa
async function obtenerRuta(start, end, hospitalNombre, center_id) {
  try {
    const res = await fetch('/map/api/ruta', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ start: start, end: end, hospital: hospitalNombre, center_id: center_id })
    });
    const data = await res.json();

    if (data && data.routes && data.routes.length > 0) {
      const geo = data.routes[0].geometry;

      if (rutaLayer) {
        map.removeLayer(rutaLayer);
      }
      rutaLayer = L.geoJSON(geo, { style: { color: 'blue', weight: 5 } }).addTo(map);
      map.fitBounds(rutaLayer.getBounds());

      // guardar info mínima adicional (distancia/duracion) en history frontend también
      const distancia_m = data.routes[0].distance;
      const duracion_s = data.routes[0].duration;
      // opcional: enviar un record_search con distancia/duracion
      recordSearch({
        center_id: center_id,
        query: searchInput.value.trim(),
        filtros: getSelectedTipos(),
        distancia: distancia_m ? (distancia_m/1000.0) : null,
        duracion: duracion_s ? (duracion_s/60.0) : null,
        ruta: data
      });
    } else {
      alert("No se encontró ruta.");
    }
  } catch (err) {
    console.error("Error obteniendo ruta:", err);
    alert("Error obteniendo ruta.");
  }
}
