<?php

	$myfile = fopen("resultados.txt", "a");		// Abre un archivo en modo append
	$txt = $_GET['resultado']."\n";			// Crea una nueva linea con el resultado
	fwrite($myfile, $txt);				// Escribe la linea al archivo
	fclose($myfile);				// Cierra el archivo
	
?>
