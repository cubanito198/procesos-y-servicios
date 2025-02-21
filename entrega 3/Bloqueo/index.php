<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏁 Rally Login 🏁</title>
    <link rel="stylesheet" href="estilo.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
</head>
<body>
    <div class="login-container">
        <h2><i class="fa-solid fa-flag-checkered"></i> Inicio de Sesión</h2>
        <form action="login.php" method="post">
            <label for="username"><i class="fa-solid fa-user"></i> Usuario:</label>
            <input type="text" name="username" required placeholder="Tu usuario">
            
            <label for="password"><i class="fa-solid fa-lock"></i> Contraseña:</label>
            <input type="password" name="password" required placeholder="Tu contraseña">
            
            <button type="submit"><i class="fa-solid fa-gas-pump"></i> Acelerar</button>
        </form>
    </div>
</body>
</html>
