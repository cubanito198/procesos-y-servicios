<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Rally Championship - Mapa de Calor Avanzado</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --racing-red: #ff0000;
            --bright-yellow: #ffff00;
            --rally-yellow: #ffd700;
            --pure-white: #ffffff;
            --racing-black: #000000;
            --dark-gray: #1a1a1a;
            --light-gray: #333333;
            --danger-red: #cc0000;
            --warning-yellow: #ffcc00;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Impact', 'Arial Black', sans-serif;
            background: 
                linear-gradient(45deg, rgba(0, 0, 0, 0.9), rgba(26, 26, 26, 0.95)),
                radial-gradient(circle at 20% 80%, var(--racing-red) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, var(--rally-yellow) 0%, transparent 50%),
                linear-gradient(135deg, var(--racing-black) 0%, var(--dark-gray) 100%);
            background-attachment: fixed;
            color: var(--pure-white);
            min-height: 100vh;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 2px,
                    rgba(255, 255, 0, 0.03) 2px,
                    rgba(255, 255, 0, 0.03) 4px
                );
            pointer-events: none;
            z-index: -1;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 25px;
            background: 
                linear-gradient(135deg, rgba(255, 0, 0, 0.15), rgba(255, 255, 0, 0.15)),
                rgba(0, 0, 0, 0.8);
            border-radius: 15px;
            backdrop-filter: blur(15px);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.4),
                inset 0 1px 0 rgba(255, 255, 0, 0.3),
                0 0 20px rgba(255, 0, 0, 0.2);
            border: 2px solid rgba(255, 255, 0, 0.4);
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: repeating-conic-gradient(
                from 0deg at 50% 50%,
                transparent 0deg,
                rgba(255, 255, 0, 0.05) 5deg,
                transparent 10deg
            );
            animation: rotate 20s linear infinite;
            pointer-events: none;
        }

        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .header h1 {
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(45deg, 
                var(--racing-red), 
                var(--bright-yellow), 
                var(--rally-yellow),
                var(--racing-red)
            );
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
            text-shadow: 
                2px 2px 4px rgba(0, 0, 0, 0.8),
                0 0 10px rgba(255, 0, 0, 0.4);
            animation: gradient-shift 3s ease-in-out infinite;
            position: relative;
            z-index: 1;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
            font-weight: 600;
            color: var(--rally-yellow);
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
            position: relative;
            z-index: 1;
        }

        .controls {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px;
            background: 
                linear-gradient(135deg, rgba(255, 0, 0, 0.1), rgba(255, 255, 0, 0.1)),
                rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 0, 0.4);
            box-shadow: 
                0 4px 20px rgba(0, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 0, 0.2);
        }

        .control-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .control-group label {
            font-weight: 700;
            font-size: 0.9rem;
            color: var(--bright-yellow);
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        select, input, button {
            padding: 10px 15px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            font-family: 'Impact', 'Arial Black', sans-serif;
        }

        select, input {
            background: 
                linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(26, 26, 26, 0.8));
            color: var(--pure-white);
            border: 2px solid rgba(255, 255, 0, 0.4);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        select option {
            background: var(--racing-black);
            color: var(--bright-yellow);
            font-weight: 600;
            padding: 8px;
        }

        select option:hover,
        select option:checked {
            background: var(--racing-red);
            color: var(--pure-white);
        }

        select:focus, input:focus {
            outline: none;
            border-color: var(--racing-red);
            box-shadow: 
                inset 0 2px 4px rgba(0, 0, 0, 0.3),
                0 0 0 3px rgba(255, 0, 0, 0.3),
                0 0 10px rgba(255, 255, 0, 0.5);
            transform: scale(1.05);
        }

        button {
            background: linear-gradient(45deg, var(--racing-red), var(--danger-red));
            color: var(--pure-white);
            font-weight: 700;
            cursor: pointer;
            border: 2px solid rgba(255, 255, 0, 0.4);
            display: flex;
            align-items: center;
            gap: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 
                0 4px 15px rgba(255, 0, 0, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }

        button:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 
                0 8px 25px rgba(255, 0, 0, 0.4),
                0 0 20px rgba(255, 255, 0, 0.6),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
            background: linear-gradient(45deg, var(--danger-red), var(--racing-red));
        }

        button:active {
            transform: translateY(-1px) scale(1.02);
        }

        .stats-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--bright-yellow);
            display: block;
        }

        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-top: 5px;
        }

        .table-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            overflow: auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }

        .heatmap-table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .heatmap-table th {
            background: linear-gradient(45deg, var(--racing-red), var(--bright-yellow), var(--rally-yellow));
            color: var(--racing-black);
            padding: 15px 8px;
            font-weight: 900;
            text-align: center;
            border: 2px solid rgba(255, 255, 0, 0.6);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Impact', 'Arial Black', sans-serif;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }

        .heatmap-table th::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.4), 
                transparent
            );
            transition: left 0.5s ease;
        }

        .heatmap-table th:hover::before {
            left: 100%;
        }

        .heatmap-table td {
            padding: 12px 8px;
            text-align: center;
            border: 1px solid rgba(255, 255, 0, 0.3);
            font-weight: 700;
            font-family: 'Impact', 'Arial Black', sans-serif;
            transition: all 0.4s ease;
            cursor: pointer;
            position: relative;
            font-size: 0.95rem;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
        }

        .heatmap-table td:hover {
            transform: scale(1.1) rotateZ(1deg);
            z-index: 10;
            box-shadow: 
                0 8px 25px rgba(0, 0, 0, 0.6),
                0 0 20px rgba(255, 255, 0, 0.8),
                inset 0 0 10px rgba(255, 255, 255, 0.1);
            border-color: var(--bright-yellow);
            border-width: 2px;
        }

        .legend {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            flex-wrap: wrap;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
        }

        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .tooltip {
            position: fixed;
            background: rgba(0, 0, 0, 0.95);
            color: var(--pure-white);
            padding: 10px 15px;
            border-radius: 8px;
            pointer-events: none;
            font-size: 12px;
            z-index: 1000;
            display: none;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 0, 0.4);
        }

        .tooltip::before {
            content: '';
            position: absolute;
            top: -5px;
            left: 50%;
            transform: translateX(-50%);
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 5px solid rgba(0, 0, 0, 0.95);
        }

        .export-section {
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }

        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-left: 4px solid var(--primary-color);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .controls {
                flex-direction: column;
            }
            
            .control-group {
                width: 100%;
                justify-content: space-between;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .table-container {
                padding: 10px;
            }
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header fade-in">
            <h1><i class="fas fa-mountain"></i> MONTE CARLO RALLY</h1>
            <p>🏔️ Análisis de Tiempos por Tramos Especiales de Montaña 🏁</p>
        </div>

        <div class="controls fade-in">
            <div class="control-group">
                <label for="colorScheme">Esquema:</label>
                <select id="colorScheme">
                    <option value="classicRacing" selected>🏁 Clásico Racing</option>
                    <option value="yellowToRed">⚡ Amarillo-Rojo</option>
                    <option value="blackToWhite">⚫ Negro-Blanco</option>
                    <option value="whiteToBlack">⚪ Blanco-Negro</option>
                    <option value="redToBlack">🔴 Rojo-Negro</option>
                    <option value="yellowToBlack">🟡 Amarillo-Negro</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="intensity">Intensidad:</label>
                <input type="range" id="intensity" min="0.3" max="1.0" step="0.1" value="0.8">
            </div>
            
            <div class="control-group">
                <label for="animation">Animación:</label>
                <input type="checkbox" id="animation" checked>
            </div>
            
            <button id="regenerateData">
                <i class="fas fa-flag-checkered"></i>
                Nueva Etapa
            </button>
            
            <button id="toggleStats">
                <i class="fas fa-tachometer-alt"></i>
                Telemetría
            </button>
        </div>

        <div class="stats-panel fade-in" id="statsPanel">
            <div class="stat-card">
                <span class="stat-value" id="maxValue">0</span>
                <div class="stat-label">Valor Máximo</div>
            </div>
            <div class="stat-card">
                <span class="stat-value" id="minValue">0</span>
                <div class="stat-label">Valor Mínimo</div>
            </div>
            <div class="stat-card">
                <span class="stat-value" id="avgValue">0</span>
                <div class="stat-label">Promedio</div>
            </div>
            <div class="stat-card">
                <span class="stat-value" id="totalStages">0</span>
                <div class="stat-label">Total Tramos</div>
            </div>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>🏔️ Preparando nueva etapa de montaña...</p>
        </div>

        <div class="table-container fade-in">
            <table class="heatmap-table" id="heatmapTable">
                <thead>
                    <tr id="tableHeader"></tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>

        <div class="legend" id="legend"></div>

        <div class="export-section">
            <button id="exportCSV">
                <i class="fas fa-download"></i>
                Exportar Tiempos
            </button>
            <button id="exportJSON">
                <i class="fas fa-file-code"></i>
                Datos Rally
            </button>
            <button id="printTable">
                <i class="fas fa-print"></i>
                Clasificación
            </button>
        </div>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
        class RallyHeatMap {
            constructor() {
                this.data = [];
                this.colorSchemes = {
                    classicRacing: ['#ff0000', '#ffff00'], // Rojo a amarillo
                    yellowToRed: ['#ffff00', '#ff0000'], // Amarillo a rojo
                    blackToWhite: ['#000000', '#ffffff'], // Negro a blanco
                    whiteToBlack: ['#ffffff', '#000000'], // Blanco a negro
                    redToBlack: ['#ff0000', '#000000'], // Rojo a negro
                    yellowToBlack: ['#ffff00', '#000000'] // Amarillo a negro
                };
                this.currentScheme = 'classicRacing';
                this.intensity = 0.8;
                this.animationEnabled = true;
                this.rows = 20;
                this.cols = 15;
                
                this.init();
            }

            init() {
                this.generateData();
                this.setupEventListeners();
                this.renderTable();
                this.applyHeatMap();
                this.updateStats();
                this.createLegend();
            }

            generateData() {
                this.data = [];
                for (let i = 0; i < this.rows; i++) {
                    const row = [];
                    for (let j = 0; j < this.cols; j++) {
                        // Generar datos más realistas para rally
                        const baseTime = 120 + Math.random() * 300; // 2-7 minutos
                        const variation = (Math.random() - 0.5) * 60; // ±30 segundos
                        row.push(Math.round(baseTime + variation));
                    }
                    this.data.push(row);
                }
            }

            setupEventListeners() {
                document.getElementById('colorScheme').addEventListener('change', (e) => {
                    this.currentScheme = e.target.value;
                    this.applyHeatMap();
                    this.createLegend();
                });

                document.getElementById('intensity').addEventListener('input', (e) => {
                    this.intensity = parseFloat(e.target.value);
                    this.applyHeatMap();
                });

                document.getElementById('animation').addEventListener('change', (e) => {
                    this.animationEnabled = e.target.checked;
                    this.applyHeatMap();
                });

                document.getElementById('regenerateData').addEventListener('click', () => {
                    this.showLoading();
                    setTimeout(() => {
                        this.generateData();
                        this.renderTable();
                        this.applyHeatMap();
                        this.updateStats();
                        this.hideLoading();
                    }, 1000);
                });

                document.getElementById('toggleStats').addEventListener('click', () => {
                    const panel = document.getElementById('statsPanel');
                    panel.style.display = panel.style.display === 'none' ? 'grid' : 'none';
                });

                document.getElementById('exportCSV').addEventListener('click', () => this.exportCSV());
                document.getElementById('exportJSON').addEventListener('click', () => this.exportJSON());
                document.getElementById('printTable').addEventListener('click', () => window.print());
            }

            renderTable() {
                const header = document.getElementById('tableHeader');
                const body = document.getElementById('tableBody');

                // Limpiar tabla
                header.innerHTML = '';
                body.innerHTML = '';

                // Crear header con nombres de tramos de montaña
                const stageNames = [
                    '🏔️ COL TURINI', '🌲 FORÊT', '❄️ GLACIER', '🏁 HAIRPINS', '⛰️ SUMMIT',
                    '🌪️ TORNANTE', '🗻 ALPINE', '🏔️ MONTAGNE', '❄️ NEIGE', '🌲 SAPIN',
                    '⛰️ ROCHERS', '🏁 ÉPINGLE', '🌪️ LACETS', '🗻 SOMMET', '❄️ VERGLAS'
                ];
                for (let j = 0; j < this.cols; j++) {
                    const th = document.createElement('th');
                    const stageName = stageNames[j] || `🏔️ SS${j + 1}`;
                    th.textContent = stageName;
                    th.title = `Tramo Especial ${j + 1} - ${stageName}`;
                    header.appendChild(th);
                }

                // Crear filas
                for (let i = 0; i < this.rows; i++) {
                    const tr = document.createElement('tr');
                    for (let j = 0; j < this.cols; j++) {
                        const td = document.createElement('td');
                        td.textContent = this.data[i][j];
                        td.dataset.value = this.data[i][j];
                        td.dataset.row = i;
                        td.dataset.col = j;
                        
                        // Tooltip events
                        td.addEventListener('mouseenter', (e) => this.showTooltip(e));
                        td.addEventListener('mousemove', (e) => this.updateTooltipPosition(e));
                        td.addEventListener('mouseleave', () => this.hideTooltip());
                        
                        tr.appendChild(td);
                    }
                    body.appendChild(tr);
                }
            }

            applyHeatMap() {
                const cells = document.querySelectorAll('.heatmap-table td');
                const values = Array.from(cells).map(cell => parseFloat(cell.dataset.value));
                const min = Math.min(...values);
                const max = Math.max(...values);
                const range = max - min || 1;

                const [color1, color2] = this.colorSchemes[this.currentScheme];

                cells.forEach(cell => {
                    const value = parseFloat(cell.dataset.value);
                    const percentage = (value - min) / range;
                    const adjustedPercentage = percentage * this.intensity;
                    
                    const color = this.interpolateColor(color1, color2, adjustedPercentage);
                    const textColor = this.getContrastColor(color);
                    
                    if (this.animationEnabled) {
                        cell.style.transition = 'all 0.3s ease';
                    } else {
                        cell.style.transition = 'none';
                    }
                    
                    cell.style.backgroundColor = color;
                    cell.style.color = textColor;
                });
            }

            interpolateColor(color1, color2, percentage) {
                const hex1 = color1.replace('#', '');
                const hex2 = color2.replace('#', '');
                
                const r1 = parseInt(hex1.substr(0, 2), 16);
                const g1 = parseInt(hex1.substr(2, 2), 16);
                const b1 = parseInt(hex1.substr(4, 2), 16);
                
                const r2 = parseInt(hex2.substr(0, 2), 16);
                const g2 = parseInt(hex2.substr(2, 2), 16);
                const b2 = parseInt(hex2.substr(4, 2), 16);
                
                const r = Math.round(r1 + (r2 - r1) * percentage);
                const g = Math.round(g1 + (g2 - g1) * percentage);
                const b = Math.round(b1 + (b2 - b1) * percentage);
                
                return `rgb(${r}, ${g}, ${b})`;
            }

            getContrastColor(rgb) {
                const match = rgb.match(/rgb\((\d+), (\d+), (\d+)\)/);
                if (!match) return '#000000';
                
                const r = parseInt(match[1]);
                const g = parseInt(match[2]);
                const b = parseInt(match[3]);
                
                const brightness = (r * 299 + g * 587 + b * 114) / 1000;
                return brightness > 128 ? '#000000' : '#ffffff';
            }

            showTooltip(e) {
                const tooltip = document.getElementById('tooltip');
                const cell = e.target;
                const value = cell.dataset.value;
                const row = parseInt(cell.dataset.row) + 1;
                const col = parseInt(cell.dataset.col) + 1;
                
                const driverNames = [
                    '🇫🇷 S.OGIER', '🇪🇸 D.SORDO', '🇧🇪 T.NEUVILLE', '🇫🇮 O.TÄNAK', 
                    '🇬🇧 E.EVANS', '🇫🇷 S.LOEB', '🇳🇴 M.SOLBERG', '🇮🇪 C.BREEN',
                    '🇫🇮 K.ROVANPERÄ', '🇫🇷 A.FOURMAUX', '🇰🇷 H.PARK', '🇯🇵 T.KATSUTA',
                    '🇪🇪 M.JÄRVEOJA', '🇫🇮 J.HUTTUNEN', '🇩🇪 F.KREIM', '🇬🇧 T.CAVE',
                    '🇮🇹 A.CRUGNOLA', '🇫🇷 Y.LOUBET', '🇦🇺 H.PADDON', '🇷🇴 S.TEMPESTINI'
                ];
                
                const stageConditions = [
                    '☀️ Seco', '🌧️ Mojado', '❄️ Nieve', '🌫️ Niebla', '🌪️ Viento'
                ];
                
                const values = Array.from(document.querySelectorAll('.heatmap-table td')).map(c => parseFloat(c.dataset.value));
                const min = Math.min(...values);
                const max = Math.max(...values);
                const percentage = ((value - min) / (max - min) * 100).toFixed(1);
                
                const driverName = driverNames[row - 1] || `🏎️ PILOT ${row}`;
                const condition = stageConditions[Math.floor(Math.random() * stageConditions.length)];
                const position = Math.floor(((max - value) / (max - min)) * 20) + 1;
                
                tooltip.innerHTML = `
                    <strong style="color: #ffff00;">${driverName}</strong><br>
                    <i class="fas fa-mountain" style="color: #ffffff;"></i> <strong>Tramo ${col}</strong><br>
                    <i class="fas fa-stopwatch" style="color: #ff0000;"></i> <strong>${value}s</strong><br>
                    <i class="fas fa-trophy" style="color: #ffff00;"></i> Pos: <strong>#${position}</strong><br>
                    <i class="fas fa-percentage" style="color: #ffffff;"></i> Perf: <strong>${percentage}%</strong><br>
                    <i class="fas fa-cloud" style="color: #ffff00;"></i> ${condition}
                `;
                
                tooltip.style.display = 'block';
                this.updateTooltipPosition(e);
            }

            updateTooltipPosition(e) {
                const tooltip = document.getElementById('tooltip');
                const offset = 15;
                tooltip.style.left = `${e.clientX + offset}px`;
                tooltip.style.top = `${e.clientY + offset}px`;
            }

            hideTooltip() {
                document.getElementById('tooltip').style.display = 'none';
            }

            updateStats() {
                const values = this.data.flat();
                const max = Math.max(...values);
                const min = Math.min(...values);
                const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1);
                const total = this.rows * this.cols;

                document.getElementById('maxValue').textContent = `${max}s`;
                document.getElementById('minValue').textContent = `${min}s`;
                document.getElementById('avgValue').textContent = `${avg}s`;
                document.getElementById('totalStages').textContent = total;
            }

            createLegend() {
                const legend = document.getElementById('legend');
                const [color1, color2] = this.colorSchemes[this.currentScheme];
                const steps = 5;
                
                legend.innerHTML = '<strong>Leyenda:</strong>';
                
                for (let i = 0; i < steps; i++) {
                    const percentage = i / (steps - 1);
                    const color = this.interpolateColor(color1, color2, percentage);
                    const label = i === 0 ? 'Mejor' : i === steps - 1 ? 'Peor' : 'Medio';
                    
                    const item = document.createElement('div');
                    item.className = 'legend-item';
                    item.innerHTML = `
                        <div class="legend-color" style="background-color: ${color}"></div>
                        <span>${label}</span>
                    `;
                    legend.appendChild(item);
                }
            }

            showLoading() {
                document.getElementById('loading').style.display = 'block';
                document.querySelector('.table-container').style.display = 'none';
            }

            hideLoading() {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.table-container').style.display = 'block';
            }

            exportCSV() {
                let csv = '';
                
                // Header
                for (let j = 0; j < this.cols; j++) {
                    csv += `SS${j + 1}${j < this.cols - 1 ? ',' : ''}`;
                }
                csv += '\n';
                
                // Data
                for (let i = 0; i < this.rows; i++) {
                    for (let j = 0; j < this.cols; j++) {
                        csv += `${this.data[i][j]}${j < this.cols - 1 ? ',' : ''}`;
                    }
                    csv += '\n';
                }
                
                this.downloadFile(csv, 'rally-heatmap.csv', 'text/csv');
            }

            exportJSON() {
                const jsonData = {
                    metadata: {
                        generated: new Date().toISOString(),
                        rows: this.rows,
                        cols: this.cols,
                        colorScheme: this.currentScheme
                    },
                    data: this.data
                };
                
                this.downloadFile(JSON.stringify(jsonData, null, 2), 'rally-heatmap.json', 'application/json');
            }

            downloadFile(content, filename, contentType) {
                const blob = new Blob([content], { type: contentType });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
            }
        }

        // Inicializar cuando el DOM esté listo
        document.addEventListener('DOMContentLoaded', () => {
            new RallyHeatMap();
        });
    </script>
</body>
</html>