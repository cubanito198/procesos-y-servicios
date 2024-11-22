<?php
	$myfile = fopen("usuarios.txt", "a");
	$txt = $_GET['usuario']."\n";
	fwrite($myfile, $txt);
	fclose($myfile);
?>