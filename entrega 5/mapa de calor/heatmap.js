/**
 * HeatMap - Biblioteca para crear mapas de calor sobre tablas usando valores numéricos.
 * 
 * Autor: Javier Hortigüela
 * Licencia: MIT
 *
 * Nuevas funcionalidades:
 * - Tooltip interactivo en cada celda que muestra el valor y su porcentaje relativo.
 */

// ======================
// Funciones auxiliares para manejo de colores
// ======================

/**
 * Convierte una cadena RGB (e.g. "rgb(255, 0, 0)") a formato HSL.
 * @param {string} rgbString - Cadena en formato RGB.
 * @returns {string} - Cadena en formato HSL.
 */
function rgbToHsl(rgbString) {
    const match = rgbString.match(/^rgb\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)$/);
    if (!match) {
        throw new Error("Formato RGB inválido. Usa 'rgb(x, y, z)'.");
    }

    let r = parseInt(match[1], 10);
    let g = parseInt(match[2], 10);
    let b = parseInt(match[3], 10);

    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0; // Gris, sin cromaticidad
    } else {
        const delta = max - min;
        s = l > 0.5 ? delta / (2 - max - min) : delta / (max + min);
        switch (max) {
            case r:
                h = (g - b) / delta + (g < b ? 6 : 0);
                break;
            case g:
                h = (b - r) / delta + 2;
                break;
            case b:
                h = (r - g) / delta + 4;
                break;
        }
        h /= 6;
    }

    // Convertir a grados y porcentajes
    h = Math.round(h * 360);
    s = Math.round(s * 100);
    l = Math.round(l * 100);

    return `hsl(${h}, ${s}%, ${l}%)`;
}

/**
 * Modifica el valor de la luminancia en una cadena HSL.
 * @param {string} hslString - Cadena HSL (e.g. "hsl(120, 50%, 50%)").
 * @param {number} newLightness - Nuevo valor de luminancia (0-100).
 * @returns {string} - Cadena HSL modificada.
 */
function modifyHslLightness(hslString, newLightness) {
    if (newLightness < 0 || newLightness > 100) {
        throw new Error("El valor de luminancia debe estar entre 0 y 100.");
    }
    const match = hslString.match(/^hsl\((\d{1,3}),\s*(\d{1,3})%,\s*(\d{1,3})%\)$/);
    if (!match) {
        throw new Error("Formato HSL inválido. Usa 'hsl(x, y%, z%)'.");
    }
    const h = parseInt(match[1], 10);
    const s = parseInt(match[2], 10);
    // Se reemplaza la luminancia por el nuevo valor
    return `hsl(${h}, ${s}%, ${newLightness}%)`;
}

/**
 * Interpola dos colores HSL.
 * @param {string} hsl1 - Primer color en HSL.
 * @param {string} hsl2 - Segundo color en HSL.
 * @param {number} percentage - Porcentaje de interpolación (0 a 1).
 * @returns {string} - Color resultante en formato HSL.
 */
function interpolateHsl(hsl1, hsl2, percentage) {
    const match1 = hsl1.match(/^hsl\((\d{1,3}),\s*(\d{1,3})%,\s*(\d{1,3})%\)$/);
    const match2 = hsl2.match(/^hsl\((\d{1,3}),\s*(\d{1,3})%,\s*(\d{1,3})%\)$/);
    
    if (!match1 || !match2) {
        throw new Error("Formato HSL inválido para interpolación.");
    }

    let h1 = parseInt(match1[1], 10),
        s1 = parseInt(match1[2], 10),
        l1 = parseInt(match1[3], 10),
        h2 = parseInt(match2[1], 10),
        s2 = parseInt(match2[2], 10),
        l2 = parseInt(match2[3], 10);

    // Interpolación circular para el matiz
    let deltaH = h2 - h1;
    if (deltaH > 180) deltaH -= 360;
    if (deltaH < -180) deltaH += 360;
    let h = (h1 + percentage * deltaH) % 360;
    if (h < 0) h += 360;

    // Interpolación lineal para saturación y luminancia
    let s = s1 + percentage * (s2 - s1);
    let l = l1 + percentage * (l2 - l1);

    return `hsl(${Math.round(h)}, ${Math.round(s)}%, ${Math.round(l)}%)`;
}

// ======================
// Función principal: Aplicar mapa de calor a las tablas
// ======================

// Selecciona todas las tablas con la clase 'heatmap-table'
let tables = document.querySelectorAll(".heatmap-table");

tables.forEach(function(table) {
    // Obtener colores computados de la tabla
    let textColor = window.getComputedStyle(table).color;
    let bgColor = window.getComputedStyle(table).backgroundColor;

    // Valor por defecto en caso de no tener color definido
    if (!textColor || textColor === 'rgba(0, 0, 0, 0)' || textColor === 'transparent') {
        textColor = "rgb(255, 0, 0)"; // Rojo por defecto
    }

    // Convertir colores a HSL
    let textHsl = rgbToHsl(textColor);
    let bgHsl = (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') 
                  ? rgbToHsl(bgColor) : null;

    // Seleccionar todas las celdas numéricas del cuerpo de la tabla
    let cells = table.querySelectorAll("tbody td");
    let values = [];

    // Recoger los valores numéricos de las celdas
    cells.forEach(function(cell) {
        let value = parseFloat(cell.textContent);
        if (!isNaN(value)) {
            values.push(value);
        }
    });

    if (values.length === 0) {
        console.warn("No se encontraron valores numéricos en la tabla:", table);
        return;
    }

    let max = Math.max(...values);
    let min = Math.min(...values);
    let range = max - min;
    if (range === 0) range = 1; // Evitar división por cero

    // Crear un tooltip global para celdas (nueva funcionalidad)
    const cellTooltip = document.createElement('div');
    cellTooltip.style.position = 'fixed';
    cellTooltip.style.background = 'rgba(0, 0, 0, 0.75)';
    cellTooltip.style.color = 'white';
    cellTooltip.style.padding = '4px 8px';
    cellTooltip.style.borderRadius = '4px';
    cellTooltip.style.pointerEvents = 'none';
    cellTooltip.style.fontSize = '12px';
    cellTooltip.style.display = 'none';
    document.body.appendChild(cellTooltip);

    // Función para actualizar la posición del tooltip de celdas
    function updateCellTooltipPosition(e) {
        const offset = 10;
        cellTooltip.style.left = `${e.clientX + offset}px`;
        cellTooltip.style.top = `${e.clientY + offset}px`;
    }

    // Iterar nuevamente sobre las celdas para aplicar estilos
    cells.forEach(function(cell) {
        let value = parseFloat(cell.textContent);
        if (isNaN(value)) return;

        // Fijar color de texto
        cell.style.color = "black";

        // Calcular porcentaje normalizado (0 a 1)
        let percentage = (value - min) / range;
        let backgroundHsl;

        // Si hay color de fondo definido, se interpola entre el color de texto y el fondo
        if (bgHsl) {
            backgroundHsl = interpolateHsl(textHsl, bgHsl, percentage);
        } else {
            // Sino se ajusta la luminancia del color de texto
            backgroundHsl = modifyHslLightness(textHsl, 100 - Math.round(percentage * 50));
        }

        cell.style.backgroundColor = backgroundHsl;

        // NUEVA FUNCIONALIDAD: Tooltip en cada celda que muestra el valor y porcentaje
        cell.addEventListener('mouseover', (e) => {
            cellTooltip.innerHTML = `<strong>Valor:</strong> ${value}<br><strong>Porcentaje:</strong> ${Math.round(percentage * 100)}%`;
            cellTooltip.style.display = 'block';
            updateCellTooltipPosition(e);
        });
        cell.addEventListener('mousemove', updateCellTooltipPosition);
        cell.addEventListener('mouseout', () => {
            cellTooltip.style.display = 'none';
        });
    });

    // Opcional: Limpiar estilos de fondo y color de la tabla para que se vea solo el efecto en las celdas
    table.style.background = "none";
    table.style.color = "inherit";
});
