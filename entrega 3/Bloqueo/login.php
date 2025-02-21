<?php
session_start();
require 'db.php';

// Obtener IP del usuario
$ip_address = $_SERVER['REMOTE_ADDR'];

// Verificar si la aplicación está bloqueada
$check_block = $pdo->prepare("SELECT COUNT(*) FROM login_attempts WHERE attempt_time >= NOW() - INTERVAL 5 MINUTE");
$check_block->execute();
$failed_attempts = $check_block->fetchColumn();

if ($failed_attempts >= 3) {
    die("❌ La aplicación está bloqueada por múltiples intentos fallidos. Intenta más tarde.");
    
}

// Si se envió el formulario
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = $_POST['password'];
    

    // Buscar el usuario en la base de datos
    $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
    $stmt->execute([$username]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);

    // Si el usuario existe y la contraseña es correcta
    if ($user && password_verify($password, $user['password_hash'])) {
        $_SESSION['user'] = $user['username'];

        // Eliminar intentos fallidos antiguos
        $pdo->query("DELETE FROM login_attempts");

        echo "✅ Inicio de sesión exitoso.";
    } else {
        // Registrar intento fallido
        $stmt = $pdo->prepare("INSERT INTO login_attempts (ip_address) VALUES (?)");
        $stmt->execute([$ip_address]);

        echo "❌ Usuario o contraseña incorrectos.";
    }
}
?>
