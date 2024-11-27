<?php
	///////////////////// TAREAS /////////////////////////////////////////////////
	
    	$file = 'tareas.txt';				// Abro el archivo de tareas

    	$lines = file($file);				// Me lee el contenido de las tareas
	$tarea = $lines[0];				// Se queda con la primera tarea
    	echo $lines[0];					// Me saca la primera tarea por pantalla (lo lleva a JS)

    	array_shift($lines);				// Al archivo le quita la primera linea

    	
    	file_put_contents($file, implode('', $lines));	// Guarda esas lineas en el archivo (sobreescribe)
    	
    	///////////////////// ASIGNACIONES /////////////////////////////////////////////////
    	
    	$myfile = fopen("asignaciones.txt", "a");	// Abre un archivo
	$txt = "Al usuario".$_GET['usuario']." le ha tocado la tarea: ".$tarea."\n";	// Guarda un registro
	fwrite($myfile, $txt);				// escribe el registro
	fclose($myfile);				// Cierra el archivo

?>
