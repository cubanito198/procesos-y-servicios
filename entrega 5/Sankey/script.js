 class SankeyFlowPro {
      constructor(container, options = {}) {
        this.container = container;
        this.options = {
          width: 1000,
          height: 600,
          nodeWidth: 25,
          nodePadding: 15,
          minNodeHeight: 20,
          animationEnabled: false,
          theme: 'default',
          ...options
        };
        
        this.data = null;
        this.svg = null;
        this.tooltip = document.getElementById('tooltip');
        this.scale = 1;
        this.translateX = 0;
        this.translateY = 0;
        this.isDragging = false;
        this.lastMousePos = { x: 0, y: 0 };
        
        this.init();
      }

      init() {
        this.setupEventListeners();
        this.loadSampleData();
      }

      setupEventListeners() {
        // Control de ancho de nodo
        document.getElementById('nodeWidth').addEventListener('input', (e) => {
          this.options.nodeWidth = parseInt(e.target.value);
          this.render(false); // Sin loading para cambios rápidos
        });

        // Control de espaciado
        document.getElementById('nodePadding').addEventListener('input', (e) => {
          this.options.nodePadding = parseInt(e.target.value);
          this.render(false); // Sin loading para cambios rápidos
        });

        // Toggle de animación
        document.getElementById('toggleAnimation').addEventListener('click', (e) => {
          this.options.animationEnabled = !this.options.animationEnabled;
          e.target.textContent = this.options.animationEnabled ? 'Desactivar' : 'Activar';
          this.toggleAnimation();
        });

        // Botones de exportación
        document.getElementById('exportPNG').addEventListener('click', () => this.exportPNG());
        document.getElementById('exportSVG').addEventListener('click', () => this.exportSVG());

        // Datos aleatorios
        document.getElementById('randomizeData').addEventListener('click', () => this.generateRandomData());

        // Crear gráfica personalizada
        document.getElementById('createCustom').addEventListener('click', () => this.showCustomModal());

        // Modal events
        document.getElementById('modalClose').addEventListener('click', () => this.hideCustomModal());
        document.getElementById('cancelCustom').addEventListener('click', () => this.hideCustomModal());
        document.getElementById('createFromData').addEventListener('click', () => this.createFromCustomData());
        document.getElementById('modalOverlay').addEventListener('click', (e) => {
          if (e.target === document.getElementById('modalOverlay')) {
            this.hideCustomModal();
          }
        });

        // Controles de zoom
        document.getElementById('zoomIn').addEventListener('click', () => this.zoom(1.2));
        document.getElementById('zoomOut').addEventListener('click', () => this.zoom(0.8));
        document.getElementById('resetZoom').addEventListener('click', () => this.resetZoom());

        // Pan y zoom con mouse
        this.container.addEventListener('wheel', (e) => this.handleWheel(e));
        this.container.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.container.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.container.addEventListener('mouseup', () => this.handleMouseUp());

        // Tecla Escape para cerrar modal
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape') {
            this.hideCustomModal();
          }
        });
      }

      loadSampleData() {
        this.data = {
          nodes: [
            { name: "Fuente A", color: "#3b82f6" },
            { name: "Fuente B", color: "#10b981" },
            { name: "Fuente C", color: "#f59e0b" },
            { name: "Proceso", color: "#6b7280" },
            { name: "Destino X", color: "#ef4444" },
            { name: "Destino Y", color: "#8b5cf6" },
            { name: "Destino Z", color: "#ec4899" }
          ],
          links: [
            { source: 0, target: 3, value: 150 },
            { source: 1, target: 3, value: 100 },
            { source: 2, target: 3, value: 80 },
            { source: 3, target: 4, value: 120 },
            { source: 3, target: 5, value: 110 },
            { source: 3, target: 6, value: 100 }
          ]
        };
        this.render();
      }

      showCustomModal() {
        const modal = document.getElementById('modalOverlay');
        if (!modal) return;
        
        modal.classList.add('show');
        // Pre-llenar con datos de ejemplo mejorados
        const nodesInput = document.getElementById('nodesInput');
        const linksInput = document.getElementById('linksInput');
        
        if (nodesInput) {
          nodesInput.value = `Energía Solar
Energía Eólica
Energía Hidráulica
Red Nacional
Industria
Hogares
Comercios
Pérdidas`;
        }
        
        if (linksInput) {
          linksInput.value = `Energía Solar,Red Nacional,200
Energía Eólica,Red Nacional,150
Energía Hidráulica,Red Nacional,100
Red Nacional,Industria,180
Red Nacional,Hogares,150
Red Nacional,Comercios,100
Red Nacional,Pérdidas,20`;
        }
      }

      hideCustomModal() {
        const modal = document.getElementById('modalOverlay');
        if (modal) {
          modal.classList.remove('show');
        }
      }

      createFromCustomData() {
        const nodesText = document.getElementById('nodesInput').value.trim();
        const linksText = document.getElementById('linksInput').value.trim();

        if (!nodesText || !linksText) {
          alert('Por favor, completa ambos campos');
          return;
        }

        try {
          // Procesar nodos
          const nodeNames = nodesText.split('\n').map(line => line.trim()).filter(line => line);
          const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'];
          
          const nodes = nodeNames.map((name, index) => ({
            name: name,
            color: colors[index % colors.length]
          }));

          // Procesar enlaces
          const linkLines = linksText.split('\n').map(line => line.trim()).filter(line => line);
          const links = [];

          for (const line of linkLines) {
            const parts = line.split(',').map(part => part.trim());
            if (parts.length !== 3) {
              throw new Error(`Formato incorrecto en línea: "${line}". Use: origen,destino,valor`);
            }

            const [sourceName, targetName, valueStr] = parts;
            const value = parseFloat(valueStr);

            if (isNaN(value)) {
              throw new Error(`Valor numérico inválido: "${valueStr}"`);
            }

            const sourceIndex = nodeNames.indexOf(sourceName);
            const targetIndex = nodeNames.indexOf(targetName);

            if (sourceIndex === -1) {
              throw new Error(`Nodo no encontrado: "${sourceName}"`);
            }
            if (targetIndex === -1) {
              throw new Error(`Nodo no encontrado: "${targetName}"`);
            }

            links.push({
              source: sourceIndex,
              target: targetIndex,
              value: value
            });
          }

          // Actualizar datos y renderizar
          this.data = { nodes, links };
          this.hideCustomModal();
          this.render();

        } catch (error) {
          alert(`Error al procesar los datos: ${error.message}`);
        }
      }

      generateRandomData() {
        const categories = [
          { prefix: "Fuente", colors: ["#ff9500", "#00bcd4", "#2196f3", "#4caf50"] },
          { prefix: "Proceso", colors: ["#9c27b0", "#ff5722", "#795548", "#607d8b"] },
          { prefix: "Destino", colors: ["#f44336", "#e91e63", "#673ab7", "#3f51b5"] }
        ];

        const nodes = [];
        const links = [];
        let nodeIndex = 0;

        categories.forEach((category, categoryIndex) => {
          const nodeCount = Math.floor(Math.random() * 3) + 2; // 2-4 nodos por categoría
          for (let i = 0; i < nodeCount; i++) {
            nodes.push({
              name: `${category.prefix} ${i + 1}`,
              color: category.colors[i % category.colors.length],
              category: categoryIndex
            });
            nodeIndex++;
          }
        });

        // Generar enlaces aleatorios entre categorías
        for (let source = 0; source < categories.length - 1; source++) {
          const sourceNodes = nodes.filter(n => n.category === source);
          const targetNodes = nodes.filter(n => n.category === source + 1);

          sourceNodes.forEach(sourceNode => {
            const targetCount = Math.floor(Math.random() * targetNodes.length) + 1;
            const shuffled = [...targetNodes].sort(() => 0.5 - Math.random());
            
            for (let i = 0; i < Math.min(targetCount, 3); i++) {
              const sourceIndex = nodes.indexOf(sourceNode);
              const targetIndex = nodes.indexOf(shuffled[i]);
              const value = Math.floor(Math.random() * 100) + 10;
              
              links.push({ source: sourceIndex, target: targetIndex, value });
            }
          });
        }

        this.data = { nodes, links };
        this.render();
      }

      render(showLoading = true) {
        if (showLoading) {
          const loading = document.getElementById('loading');
          const zoomControls = document.querySelector('.zoom-controls');
          loading.classList.add('show');

          setTimeout(() => {
            // Preservar elementos importantes antes de limpiar
            const elementsToPreserve = [];
            if (loading) elementsToPreserve.push(loading);
            if (zoomControls) elementsToPreserve.push(zoomControls);
            
            this.container.innerHTML = '';
            
            // Restaurar elementos preservados
            elementsToPreserve.forEach(el => {
              if (el && el.parentNode !== this.container) {
                this.container.appendChild(el);
              }
            });
            
            this.createSVG();
            this.processData();
            this.drawChart();
            this.updateStats();
            
            loading.classList.remove('show');
          }, 100);
        } else {
          // Renderizado rápido sin loading para cambios menores
          this.processData();
          this.drawChart();
          this.updateStats();
        }
      }

      createSVG() {
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('width', this.options.width);
        this.svg.setAttribute('height', this.options.height);
        this.svg.setAttribute('class', 'sankey-svg');
        
        // Crear grupo para transformaciones
        this.g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        this.svg.appendChild(this.g);
        
        // Definiciones para gradientes
        this.defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        this.svg.appendChild(this.defs);
        
        this.container.appendChild(this.svg);
      }

      processData() {
        // Preparar nodos
        this.nodes = this.data.nodes.map((d, i) => ({
          ...d,
          index: i,
          sourceLinks: [],
          targetLinks: [],
          valueIn: 0,
          valueOut: 0,
          layer: 0
        }));

        // Preparar enlaces
        this.links = this.data.links.map(link => ({
          source: link.source,
          target: link.target,
          value: link.value
        }));

        // Asignar enlaces a nodos
        this.links.forEach(link => {
          this.nodes[link.source].sourceLinks.push(link);
          this.nodes[link.target].targetLinks.push(link);
          this.nodes[link.source].valueOut += link.value;
          this.nodes[link.target].valueIn += link.value;
        });

        // Calcular capas
        this.calculateLayers();
        this.calculatePositions();
      }

      calculateLayers() {
        // Algoritmo mejorado para asignar capas
        const visited = new Set();
        const layers = new Map();
        
        // Encontrar nodos fuente (sin enlaces de entrada)
        const sources = this.nodes.filter(n => n.targetLinks.length === 0);
        
        const assignLayer = (node, layer) => {
          if (visited.has(node.index)) return;
          visited.add(node.index);
          
          node.layer = Math.max(node.layer || 0, layer);
          layers.set(layer, (layers.get(layer) || []).concat(node));
          
          // Procesar nodos hijos
          node.sourceLinks.forEach(link => {
            const target = this.nodes[link.target];
            assignLayer(target, layer + 1);
          });
        };

        // Asignar capas comenzando desde los nodos fuente
        sources.forEach(source => assignLayer(source, 0));
        
        // Asegurar que todos los nodos tengan una capa
        this.nodes.forEach(node => {
          if (!visited.has(node.index)) {
            assignLayer(node, 0);
          }
        });
      }

      calculatePositions() {
        const maxLayer = Math.max(...this.nodes.map(n => n.layer));
        const layerWidth = (this.options.width - this.options.nodeWidth) / Math.max(maxLayer, 1);
        
        // Posiciones horizontales
        this.nodes.forEach(node => {
          node.x0 = node.layer * layerWidth;
          node.x1 = node.x0 + this.options.nodeWidth;
        });

        // Agrupar por capas y calcular posiciones verticales
        const layers = {};
        this.nodes.forEach(node => {
          if (!layers[node.layer]) layers[node.layer] = [];
          layers[node.layer].push(node);
        });

        Object.values(layers).forEach(layerNodes => {
          this.calculateVerticalPositions(layerNodes);
        });
      }

      calculateVerticalPositions(layerNodes) {
        const totalValue = layerNodes.reduce((sum, n) => sum + Math.max(n.valueIn, n.valueOut, 1), 0);
        const availableHeight = this.options.height - (layerNodes.length - 1) * this.options.nodePadding;
        
        let y = 0;
        layerNodes.forEach(node => {
          const nodeValue = Math.max(node.valueIn, node.valueOut, 1);
          const nodeHeight = Math.max(
            (nodeValue / totalValue) * availableHeight,
            this.options.minNodeHeight
          );
          
          node.y0 = y;
          node.y1 = y + nodeHeight;
          y += nodeHeight + this.options.nodePadding;
        });
      }

      drawChart() {
        // Limpiar grupo principal
        this.g.innerHTML = '';
        
        // Dibujar enlaces primero (para que aparezcan detrás)
        this.drawLinks();
        
        // Dibujar nodos
        this.drawNodes();
        
        // Aplicar transformación actual
        this.updateTransform();
      }

      drawLinks() {
        this.links.forEach((link, index) => {
          const source = this.nodes[link.source];
          const target = this.nodes[link.target];
          
          // Crear gradiente para el enlace
          const gradientId = `gradient-${index}`;
          const gradient = this.createGradient(gradientId, source.color, target.color);
          this.defs.appendChild(gradient);
          
          // Calcular posiciones
          const sourceY = source.y0 + (source.y1 - source.y0) / 2;
          const targetY = target.y0 + (target.y1 - target.y0) / 2;
          
          // Crear path
          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          const pathData = this.createLinkPath(source.x1, sourceY, target.x0, targetY);
          
          path.setAttribute('d', pathData);
          path.setAttribute('stroke', `url(#${gradientId})`);
          path.setAttribute('stroke-width', Math.max(link.value / 5, 2));
          path.setAttribute('fill', 'none');
          path.setAttribute('opacity', '0.6');
          path.setAttribute('class', 'sankey-link');
          path.setAttribute('data-link', `${link.source}-${link.target}`);
          
          // Eventos del enlace
          this.setupLinkEvents(path, link, source, target);
          
          this.g.appendChild(path);
        });
      }

      drawNodes() {
        this.nodes.forEach(node => {
          // Crear grupo para el nodo
          const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
          nodeGroup.setAttribute('class', 'sankey-node');
          
          // SOLO clase, TODOS los estilos se aplican en setupNodeEvents
          if (this.options.animationEnabled) {
            nodeGroup.classList.add('animated');
          }
          
          // Rectángulo del nodo
          const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
          rect.setAttribute('x', node.x0);
          rect.setAttribute('y', node.y0);
          rect.setAttribute('width', this.options.nodeWidth);
          rect.setAttribute('height', node.y1 - node.y0);
          rect.setAttribute('fill', node.color);
          rect.setAttribute('rx', '6');
          rect.setAttribute('ry', '6');
          rect.setAttribute('stroke', 'rgba(255,255,255,0.3)');
          rect.setAttribute('stroke-width', '1.5');
          
          // Efecto de brillo interno para nodos animados
          if (this.options.animationEnabled) {
            // Crear gradiente con brillo
            const gradientId = `nodeGradient-${Math.random().toString(36).substr(2, 9)}`;
            const defs = this.svg.querySelector('defs') || document.createElementNS('http://www.w3.org/2000/svg', 'defs');
            if (!this.svg.querySelector('defs')) {
              this.svg.appendChild(defs);
            }
            
            const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
            gradient.setAttribute('id', gradientId);
            gradient.setAttribute('x1', '0%');
            gradient.setAttribute('y1', '0%');
            gradient.setAttribute('x2', '100%');
            gradient.setAttribute('y2', '100%');
            
            const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop1.setAttribute('offset', '0%');
            stop1.setAttribute('stop-color', node.color);
            
            const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop2.setAttribute('offset', '50%');
            stop2.setAttribute('stop-color', this.lightenColor(node.color, 20));
            
            const stop3 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
            stop3.setAttribute('offset', '100%');
            stop3.setAttribute('stop-color', node.color);
            
            gradient.appendChild(stop1);
            gradient.appendChild(stop2);
            gradient.appendChild(stop3);
            defs.appendChild(gradient);
            
            rect.setAttribute('fill', `url(#${gradientId})`);
          }
          
          // Texto del nodo
          const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          text.setAttribute('x', node.x0 + this.options.nodeWidth / 2);
          text.setAttribute('y', node.y0 + (node.y1 - node.y0) / 2);
          text.setAttribute('text-anchor', 'middle');
          text.setAttribute('dominant-baseline', 'middle');
          text.setAttribute('class', 'sankey-text');
          text.setAttribute('font-size', '11');
          text.setAttribute('fill', 'white');
          text.setAttribute('font-weight', '600');
          text.setAttribute('text-shadow', '0 1px 3px rgba(0,0,0,0.5)');
          text.textContent = node.name;
          
          nodeGroup.appendChild(rect);
          nodeGroup.appendChild(text);
          
          // EVENTOS que aplican TODOS los estilos directamente
          this.setupNodeEvents(nodeGroup, node, rect);
          
          this.g.appendChild(nodeGroup);
        });
      }

      createGradient(id, color1, color2) {
        const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
        gradient.setAttribute('id', id);
        gradient.setAttribute('x1', '0%');
        gradient.setAttribute('y1', '0%');
        gradient.setAttribute('x2', '100%');
        gradient.setAttribute('y2', '0%');
        
        const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop1.setAttribute('offset', '0%');
        stop1.setAttribute('stop-color', color1);
        
        const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        stop2.setAttribute('offset', '100%');
        stop2.setAttribute('stop-color', color2);
        
        gradient.appendChild(stop1);
        gradient.appendChild(stop2);
        
        return gradient;
      }

      createLinkPath(x0, y0, x1, y1) {
        const curvature = 0.5;
        const xi = (x0 + x1) / 2;
        return `M${x0},${y0} C${xi},${y0} ${xi},${y1} ${x1},${y1}`;
      }

      setupNodeEvents(nodeGroup, node, rect) {
        nodeGroup.addEventListener('mouseenter', (e) => {
          this.showTooltip(e, `
            <strong>${node.name}</strong><br>
            Entrada: ${node.valueIn}<br>
            Salida: ${node.valueOut}<br>
            Balance: ${node.valueIn - node.valueOut}
          `);
        });

        nodeGroup.addEventListener('mouseleave', () => {
          this.hideTooltip();
        });

        // Drag and drop mejorado
        let isDragging = false;
        let startY = 0;
        let startNodeY = 0;

        nodeGroup.addEventListener('mousedown', (e) => {
          e.preventDefault();
          isDragging = true;
          startY = e.clientY;
          startNodeY = node.y0;
          nodeGroup.classList.add('dragging');
          document.body.style.cursor = 'grabbing';
        });

        const handleMouseMove = (e) => {
          if (!isDragging || !rect) return;
          
          const deltaY = e.clientY - startY;
          const newY = Math.max(0, Math.min(
            this.options.height - (node.y1 - node.y0),
            startNodeY + deltaY / this.scale
          ));
          
          node.y0 = newY;
          node.y1 = newY + (node.y1 - startNodeY);
          
          rect.setAttribute('y', node.y0);
          
          // Actualizar enlaces conectados
          this.updateConnectedLinks(node);
        };

        const handleMouseUp = () => {
          if (isDragging) {
            isDragging = false;
            nodeGroup.classList.remove('dragging');
            document.body.style.cursor = 'default';
            this.render(); // Re-renderizar para optimizar posiciones
          }
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
      }

      setupLinkEvents(path, link, source, target) {
        path.addEventListener('mouseenter', (e) => {
          this.showTooltip(e, `
            <strong>${source.name} → ${target.name}</strong><br>
            Flujo: ${link.value}<br>
            Porcentaje: ${((link.value / this.getTotalFlow()) * 100).toFixed(1)}%
          `);
        });

        path.addEventListener('mousemove', (e) => {
          this.updateTooltipPosition(e);
        });

        path.addEventListener('mouseleave', () => {
          this.hideTooltip();
        });
      }

      updateConnectedLinks(node) {
        if (!this.g) return;
        
        // Actualizar enlaces donde este nodo es origen
        node.sourceLinks.forEach(link => {
          const target = this.nodes[link.target];
          const sourceY = node.y0 + (node.y1 - node.y0) / 2;
          const targetY = target.y0 + (target.y1 - target.y0) / 2;
          const pathData = this.createLinkPath(node.x1, sourceY, target.x0, targetY);
          
          const pathElement = this.g.querySelector(`path[data-link="${link.source}-${link.target}"]`);
          if (pathElement) {
            pathElement.setAttribute('d', pathData);
          }
        });

        // Actualizar enlaces donde este nodo es destino
        node.targetLinks.forEach(link => {
          const source = this.nodes[link.source];
          const sourceY = source.y0 + (source.y1 - source.y0) / 2;
          const targetY = node.y0 + (node.y1 - node.y0) / 2;
          const pathData = this.createLinkPath(source.x1, sourceY, node.x0, targetY);
          
          const pathElement = this.g.querySelector(`path[data-link="${link.source}-${link.target}"]`);
          if (pathElement) {
            pathElement.setAttribute('d', pathData);
          }
        });
      }

      showTooltip(event, content) {
        this.tooltip.innerHTML = content;
        this.tooltip.classList.add('show');
        this.updateTooltipPosition(event);
      }

      hideTooltip() {
        this.tooltip.classList.remove('show');
      }

      updateTooltipPosition(event) {
        // Posición directa del cursor en la ventana
        let left = event.clientX + 12; // 12px a la derecha del cursor
        let top = event.clientY - 8;   // 8px arriba del cursor
        
        // Obtener dimensiones del tooltip y ventana
        const tooltipRect = this.tooltip.getBoundingClientRect();
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;
        
        // Si se sale por la derecha, mostrar a la izquierda del cursor
        if (left + tooltipRect.width > windowWidth - 10) {
          left = event.clientX - tooltipRect.width - 12;
        }
        
        // Si se sale por abajo, mostrar arriba del cursor
        if (top + tooltipRect.height > windowHeight - 10) {
          top = event.clientY - tooltipRect.height - 8;
        }
        
        // Si se sale por la izquierda, forzar a la derecha
        if (left < 10) {
          left = event.clientX + 12;
        }
        
        // Si se sale por arriba, forzar hacia abajo
        if (top < 10) {
          top = event.clientY + 12;
        }
        
        // Aplicar posición ABSOLUTA en la ventana
        this.tooltip.style.position = 'fixed';
        this.tooltip.style.left = `${left}px`;
        this.tooltip.style.top = `${top}px`;
        this.tooltip.style.zIndex = '99999';
      }

      toggleAnimation() {
        if (!this.g) return;
        
        // Animar enlaces
        const links = this.g.querySelectorAll('.sankey-link');
        links.forEach(link => {
          if (this.options.animationEnabled) {
            link.classList.add('animated');
          } else {
            link.classList.remove('animated');
          }
        });
        
        // Animar nodos
        const nodes = this.g.querySelectorAll('.sankey-node');
        nodes.forEach(node => {
          if (this.options.animationEnabled) {
            node.classList.add('animated');
          } else {
            node.classList.remove('animated');
          }
        });
      }

      // Función para aclarar colores
      lightenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
          (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
          (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
      }

      // Funciones de zoom y pan
      zoom(factor) {
        if (!this.g) return;
        
        this.scale *= factor;
        this.scale = Math.max(0.1, Math.min(3, this.scale));
        this.updateTransform();
      }

      resetZoom() {
        this.scale = 1;
        this.translateX = 0;
        this.translateY = 0;
        this.updateTransform();
      }

      updateTransform() {
        if (!this.g) return;
        
        this.g.setAttribute('transform', 
          `translate(${this.translateX}, ${this.translateY}) scale(${this.scale})`
        );
      }

      handleWheel(e) {
        e.preventDefault();
        const factor = e.deltaY > 0 ? 0.9 : 1.1;
        this.zoom(factor);
      }

      handleMouseDown(e) {
        if (!this.svg) return;
        
        if (e.target === this.svg || e.target === this.g) {
          this.isDragging = true;
          this.lastMousePos = { x: e.clientX, y: e.clientY };
          this.svg.style.cursor = 'grabbing';
        }
      }

      handleMouseMove(e) {
        if (!this.svg || !this.isDragging) return;
        
        if (this.isDragging) {
          const deltaX = e.clientX - this.lastMousePos.x;
          const deltaY = e.clientY - this.lastMousePos.y;
          
          this.translateX += deltaX;
          this.translateY += deltaY;
          
          this.updateTransform();
          
          this.lastMousePos = { x: e.clientX, y: e.clientY };
        }
      }

      handleMouseUp() {
        if (!this.svg) return;
        
        this.isDragging = false;
        this.svg.style.cursor = 'grab';
      }

      // Funciones de exportación mejoradas
      exportPNG() {
        if (!this.svg) {
          console.error('No hay diagrama para exportar');
          return;
        }
        
        const svgData = new XMLSerializer().serializeToString(this.svg);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        canvas.width = this.options.width;
        canvas.height = this.options.height;
        
        img.onload = () => {
          ctx.fillStyle = 'white';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0);
          
          const link = document.createElement('a');
          link.download = `sankey_diagram_${Date.now()}.png`;
          link.href = canvas.toDataURL();
          link.click();
        };
        
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
      }

      exportSVG() {
        if (!this.svg) {
          console.error('No hay diagrama para exportar');
          return;
        }
        
        const svgData = new XMLSerializer().serializeToString(this.svg);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.download = `sankey_diagram_${Date.now()}.svg`;
        link.href = url;
        link.click();
        
        URL.revokeObjectURL(url);
      }

      // Estadísticas
      updateStats() {
        const nodeCount = this.nodes.length;
        const linkCount = this.links.length;
        const totalFlow = this.getTotalFlow();
        const efficiency = this.calculateEfficiency();

        document.getElementById('nodeCount').textContent = nodeCount;
        document.getElementById('linkCount').textContent = linkCount;
        document.getElementById('totalFlow').textContent = totalFlow.toLocaleString();
        document.getElementById('efficiency').textContent = `${efficiency}%`;
      }

      getTotalFlow() {
        return this.links.reduce((sum, link) => sum + link.value, 0);
      }

      calculateEfficiency() {
        const totalInput = this.nodes
          .filter(n => n.targetLinks.length === 0)
          .reduce((sum, n) => sum + n.valueOut, 0);
        
        const totalOutput = this.nodes
          .filter(n => n.sourceLinks.length === 0)
          .reduce((sum, n) => sum + n.valueIn, 0);
        
        return totalInput > 0 ? Math.round((totalOutput / totalInput) * 100) : 0;
      }
    }

    // Inicializar la aplicación
    document.addEventListener('DOMContentLoaded', () => {
      const container = document.getElementById('chartContainer');
      const sankeyChart = new SankeyFlowPro(container, {
        width: 1000,
        height: 600
      });
    });