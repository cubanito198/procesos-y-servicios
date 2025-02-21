/**
 * SankeyFlow - Biblioteca para crear diagramas Sankey interactivos con SVG
 * 
 * Autor: luis sanchez 
 * Licencia: MIT
 *
 * Nuevas funcionalidades:
 * - Configuración de altura mínima de nodos (minNodeHeight).
 * - Exportación del diagrama como imagen PNG.
 * - Tooltip global interactivo para mostrar información de nodos y enlaces.
 */

(function (global) {
  // Objeto principal de la biblioteca
  const SankeyFlow = {};

  // ======================
  // Configuración Global del Tooltip
  // ======================
  // Se crea un tooltip global que se añadirá al contenedor para mostrar información interactiva
  const tooltip = document.createElement('div');
  tooltip.style.position = 'absolute';
  tooltip.style.background = 'rgba(0, 0, 0, 0.8)';
  tooltip.style.color = 'white';
  tooltip.style.padding = '8px';
  tooltip.style.borderRadius = '4px';
  tooltip.style.pointerEvents = 'none';
  tooltip.style.display = 'none';

  // ======================
  // Función Principal: createSankeyChart
  // ======================
  SankeyFlow.createSankeyChart = function (config) {
    // Desestructuramos la configuración y asignamos valores por defecto
    const {
      element,      // Contenedor (selector o elemento DOM)
      data,         // Datos del diagrama { nodes: [...], links: [...] }
      width,        // Ancho total del SVG
      height,       // Alto total del SVG
      nodeWidth = 20,       // Ancho de cada nodo
      nodePadding = 10,     // Espaciado vertical entre nodos
      minNodeHeight = 20,   // NUEVA FUNCIONALIDAD: Altura mínima de cada nodo
      exportButton = false  // NUEVA FUNCIONALIDAD: Agregar botón de exportación a PNG
    } = config;

    // Resolver el contenedor a partir del selector o del elemento
    const container = typeof element === 'string' 
      ? document.querySelector(element) 
      : element;
    if (!container) throw new Error("Contenedor no encontrado");

    // Limpiar el contenedor y añadir el tooltip global
    container.innerHTML = '';
    container.appendChild(tooltip);

    // Crear el elemento SVG y añadirlo al contenedor
      const svg = createSVGElement('svg', { width, height, class: 'sankey-flow-svg' });
      container.appendChild(svg);

      // Crear <defs> de forma directa usando createElementNS
      const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
      console.log("Elemento <defs> creado:", defs);
      // Agregar <defs> al inicio del SVG
      svg.insertBefore(defs, svg.firstChild);

// Para depurar, mostramos el contenido de defs en la consola


    // ======================
    // Preparación de Nodos y Enlaces
    // ======================
    // Se preparan los nodos asignando índices, nombre y color (aleatorio si no se especifica)
    const nodes = data.nodes.map((d, i) => ({
      index: i,
      name: d.name || `Nodo ${i}`,
      color: d.color || getRandomColor(),
      sourceLinks: [],
      targetLinks: [],
      valueIn: 0,
      valueOut: 0,
      layer: 0  // Se asignará posteriormente
    }));

    // Se crea un mapa para acceder a los nodos por su nombre
    const nameToIndex = Object.fromEntries(nodes.map((n, i) => [n.name, i]));

    // Preparar enlaces, convirtiendo nombres a índices cuando sea necesario
    const links = data.links.map(link => {
      const sourceIndex = typeof link.source === 'string'
        ? nameToIndex[link.source]
        : link.source;
      const targetIndex = typeof link.target === 'string'
        ? nameToIndex[link.target]
        : link.target;
      return {
        source: sourceIndex,
        target: targetIndex,
        value: +link.value // Asegurarse de que el valor sea numérico
      };
    });

    // Asignar enlaces a cada nodo y acumular flujos de entrada/salida
    links.forEach(link => {
      const sourceNode = nodes[link.source];
      const targetNode = nodes[link.target];
      sourceNode.sourceLinks.push(link);
      targetNode.targetLinks.push(link);
      sourceNode.valueOut += link.value;
      targetNode.valueIn += link.value;
    });

    // ======================
    // Cálculo de Capas y Posiciones de los Nodos
    // ======================
    // 1. Asignar cada nodo a una capa (valor "layer") de forma simple
    assignNodeLayers(nodes);
    // Determinar la cantidad máxima de capas y calcular escala en X
    const maxLayer = Math.max(...nodes.map(n => n.layer));
    const xScale = (width - nodeWidth) / maxLayer;
    nodes.forEach(n => {
      n.x0 = n.layer * xScale;
      n.x1 = n.x0 + nodeWidth;
    });

    // 2. Distribuir los nodos verticalmente en cada capa
    // Se agrupan nodos por capa y se distribuyen con la función 'distributeLayerNodes'
    const layers = {};
    nodes.forEach(n => {
      if (!layers[n.layer]) layers[n.layer] = [];
      layers[n.layer].push(n);
    });
    Object.values(layers).forEach(layerNodes => {
      distributeLayerNodes(layerNodes, height, nodePadding, minNodeHeight);
    });

    // ======================
    // Creación de Enlaces (Paths SVG)
    // ======================
    // Dibujar cada enlace entre nodos y configurar interacciones con tooltip
    links.forEach((link, idx) => {
      const source = nodes[link.source];
      const target = nodes[link.target];

      // Se calcula el ancho del enlace proporcional al valor
      const linkWidth = link.value;
      // Se define la posición central de los nodos para el enlace
      const sy = source.y0 + (source.y1 - source.y0) / 2;
      const ty = target.y0 + (target.y1 - target.y0) / 2;
      
      // Definir el trazo del enlace con un degradado si los colores difieren
      let stroke;
      if (source.color === target.color) {
        stroke = source.color;
      } else {
        // Crear un degradado lineal en <defs>
        const gradientId = `gradient-${source.index}-${target.index}-${idx}`;
        const linearGradient = createSVGElement('linearGradient', {
          id: gradientId,
          x1: '0%',
          y1: '0%',
          x2: '100%',
          y2: '0%'
        });
        const stop1 = createSVGElement('stop', { offset: '0%', 'stop-color': source.color });
        const stop2 = createSVGElement('stop', { offset: '100%', 'stop-color': target.color });
        linearGradient.appendChild(stop1);
        linearGradient.appendChild(stop2);
        // ****************** VERIFICACIÓN DE <defs> ******************
        // Se verifica si existe un elemento <defs> en el SVG; si no, se crea se inserta.
        defs.appendChild(linearGradient);
       stroke = `url(#${gradientId})`;
}

      // Calcular la ruta del enlace con una curva suave
      const pathD = sankeyLinkPath(source.x1, sy, target.x0, ty);
      const path = createSVGElement('path', {
        d: pathD,
        stroke: stroke,
        'stroke-width': linkWidth,
        fill: 'none',
        opacity: 0.2,
        class: 'sankey-flow-link'
      });

      // ======================
      // Configuración del Tooltip para Enlaces
      // ======================
      const linkTooltip = `
        <strong>${source.name} → ${target.name}</strong><br>
        Valor: ${link.value}
      `;
      setupTooltip(path, linkTooltip);

      // Interacción para resaltar el enlace al pasar el mouse
      path.addEventListener('mouseover', () => {
        path.style.strokeWidth = linkWidth * 1.5;
      });
      path.addEventListener('mouseout', () => {
        path.style.strokeWidth = linkWidth;
      });

      svg.appendChild(path);
      // Almacenamos la referencia al elemento SVG en el enlace para posibles actualizaciones futuras
      link.pathElement = path;
    });

    // ======================
    // Creación de Nodos (Grupos SVG)
    // ======================
    nodes.forEach(node => {
      // Crear un grupo <g> para agrupar el rectángulo y el texto
      const g = createSVGElement('g', { class: 'sankey-flow-node' });
      
      // Crear el rectángulo del nodo
      const rect = createSVGElement('rect', {
        x: node.x0,
        y: node.y0,
        width: nodeWidth,
        height: node.y1 - node.y0,
        fill: node.color,
        stroke: '#ffffff',
        rx: 5,
        ry: 5,
        'stroke-width': 2
      });
      g.appendChild(rect);
      
      // Crear el texto centralizado del nodo
      const text = createSVGElement('text', {
        x: node.x0 + nodeWidth / 2,
        y: node.y0 + (node.y1 - node.y0) / 2,
        'text-anchor': 'middle',
        'dominant-baseline': 'middle',
        class: 'sankey-flow-text'
      }, node.name);
      g.appendChild(text);
      
      // ======================
      // Configuración del Tooltip para Nodos
      // ======================
      const nodeTooltip = `
        <strong>${node.name}</strong><br>
        Entrada: ${node.valueIn}<br>
        Salida: ${node.valueOut}
      `;
      setupTooltip(rect, nodeTooltip);
      
      // Interacción para resaltar el nodo al pasar el mouse
      rect.addEventListener('mouseover', () => {
        rect.style.filter = 'brightness(1.2)';
      });
      rect.addEventListener('mouseout', () => {
        rect.style.filter = 'none';
      });
      
      svg.appendChild(g);
      // Guardamos la referencia al grupo para posibles funcionalidades futuras
      node.gElement = g;
    });

    // ======================
    // NUEVA FUNCIONALIDAD: Botón de Exportación a PNG
    // ======================
    if (exportButton) {
      const btnExport = document.createElement('button');
      btnExport.textContent = 'Exportar a PNG';
      btnExport.className = 'sankey-flow-export-btn';
      btnExport.addEventListener('click', () => {
        exportChartAsPNG(svg, width, height);
      });
      container.appendChild(btnExport);
    }
  };

  // ======================
  // Función para asignar capas (layers) a los nodos
  // ======================
  function assignNodeLayers(nodes) {
    nodes.forEach(n => { n.layer = 0; });
    let changed = true;
    while (changed) {
      changed = false;
      nodes.forEach(n => {
        n.sourceLinks.forEach(link => {
          const target = nodes[link.target];
          if (target.layer <= n.layer) {
            target.layer = n.layer + 1;
            changed = true;
          }
        });
      });
    }
  }

  // ======================
  // Función para distribuir los nodos verticalmente en cada capa
  // ======================
  function distributeLayerNodes(layerNodes, totalHeight, nodePadding, minNodeHeight) {
    if (!layerNodes.length) return;
    const totalValue = layerNodes.reduce((sum, n) => sum + Math.max(n.valueIn, n.valueOut), 0);
    const minHeightTotal = minNodeHeight * layerNodes.length + nodePadding * (layerNodes.length - 1);
    const availableHeight = Math.max(totalHeight, minHeightTotal);
    let yStart = 0;
    layerNodes.forEach(n => {
      const nodeValue = Math.max(n.valueIn, n.valueOut);
      const rawHeight = (nodeValue / totalValue) * availableHeight;
      const nodeHeight = Math.max(rawHeight, minNodeHeight);
      n.y0 = yStart;
      n.y1 = yStart + nodeHeight;
      yStart += nodeHeight + nodePadding;
    });
  }

  // ======================
  // Función para calcular la ruta (path) de un enlace Sankey con curva suave
  // ======================
  function sankeyLinkPath(x0, y0, x1, y1) {
    const curvature = 0.5;
    const xi = interpolateNumber(x0, x1);
    const x2 = xi(curvature);
    const x3 = xi(1 - curvature);
    return `M${x0},${y0} C${x2},${y0} ${x3},${y1} ${x1},${y1}`;
  }

  // ======================
  // Función de interpolación numérica
  // ======================
  function interpolateNumber(a, b) {
    return function (t) {
      return a + (b - a) * t;
    };
  }

  // ======================
  // Función auxiliar para crear elementos SVG
  // ======================
  function createSVGElement(name, attributes = {}, textContent = '') {
    const el = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.entries(attributes).forEach(([key, value]) => {
      el.setAttribute(key, value);
    });
    if (textContent) el.textContent = textContent;
    return el;
  }

  // ======================
  // Función auxiliar para generar un color aleatorio
  // ======================
  function getRandomColor() {
    const color = Math.floor(Math.random() * 16777215).toString(16);
    return `#${color.padStart(6, '0')}`;
  }

  // ======================
  // Función para configurar el tooltip en un elemento
  // ======================
  function setupTooltip(element, content) {
    element.addEventListener('mouseover', (e) => {
      tooltip.innerHTML = content;
      tooltip.style.display = 'block';
      updateTooltipPosition(e);
    });
    element.addEventListener('mousemove', updateTooltipPosition);
    element.addEventListener('mouseout', () => {
      tooltip.style.display = 'none';
    });
  }

  // ======================
  // Función para actualizar la posición del tooltip
  // ======================
  function updateTooltipPosition(e) {
    const offset = 15;
    tooltip.style.left = `${e.clientX + offset}px`;
    tooltip.style.top = `${e.clientY + offset}px`;
  }

  // ======================
  // NUEVA FUNCIONALIDAD: Exportar el diagrama SVG a PNG
  // ======================
  function exportChartAsPNG(svgElement, width, height) {
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgElement);
    const img = new Image();
    const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    img.onload = function () {
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const pngUrl = canvas.toDataURL('image/png');
      const downloadLink = document.createElement('a');
      downloadLink.href = pngUrl;
      downloadLink.download = 'sankey_diagram.png';
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      URL.revokeObjectURL(url);
    };
    img.src = url;
  }

  // ======================
  // Exportar el objeto SankeyFlow (compatible con módulos o en el ámbito global)
  // ======================
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = SankeyFlow;
  } else {
    global.SankeyFlow = SankeyFlow;
  }

})(this);
