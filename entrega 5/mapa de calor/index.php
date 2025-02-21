<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mapa de Calor - Rally</title>
    <script defer src="heatmap.js"></script>
    <style>
        /* Estilo general */
        body {
            font-family: 'Arial Black', sans-serif;
            background-color: #1e1e1e;
            color: white;
            text-align: center;
            padding: 20px;
        }
        h1 {
            color: #ffcc00;
            text-transform: uppercase;
            text-shadow: 3px 3px 5px black;
        }
        /* Estilo de la tabla */
        .heatmap-table {
            margin: auto;
            border-collapse: collapse;
            width: 90%;
            max-width: 1200px;
            box-shadow: 0px 0px 10px rgba(255, 255, 255, 0.3);
        }
        .heatmap-table th, .heatmap-table td {
            padding: 8px;
            border: 1px solid #ffcc00;
            text-align: center;
        }
        /* Estilos iniciales del mapa de calor */
        .heatmap-table {
            color: rgb(255, 255, 255);
            background: linear-gradient(180deg, rgb(255, 0, 0), rgb(0, 0, 0));
        }
        /* Botón para cambiar colores */
        .toggle-color {
            margin: 20px;
            padding: 12px 24px;
            background-color: #ff0000;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .toggle-color:hover {
            background-color: #cc0000;
        }
    </style>
</head>
<body>
    <?php
        $columnas = 24;
        $filas = 30;
    ?>
    <h1>Mapa de Calor - Rally Championship</h1>
    <table class="heatmap-table">
        <thead>
            <tr>
                <?php for($i = 0; $i < $columnas; $i++) echo "<th>SS $i</th>"; ?>
            </tr>
        </thead>
        <tbody>
            <?php
                for($i = 0; $i < $filas; $i++) {
                    echo '<tr>';
                    for($j = 0; $j < $columnas; $j++) {
                        echo '<td>'.rand(1, 500).'</td>';
                    }
                    echo '</tr>';
                }
            ?>
        </tbody>
    </table>
    <button class="toggle-color" id="toggleColorScheme">Cambiar esquema de color</button>
    <script>
        document.getElementById('toggleColorScheme').addEventListener('click', function() {
            const table = document.querySelector('.heatmap-table');
            if (!table) return;
            const currentColor = table.style.background;
            if (currentColor.includes("rgb(255, 0, 0)")) {
                table.style.background = "linear-gradient(180deg, rgb(0, 0, 255), rgb(255, 255, 255))";
                table.style.color = "black";
            } else {
                table.style.background = "linear-gradient(180deg, rgb(255, 0, 0), rgb(0, 0, 0))";
                table.style.color = "white";
            }
        });
    </script>
</body>
</html>
