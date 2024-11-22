<?php
    $file = 'tareas.txt';

    // Read the file into an array, where each element is a line
    $lines = file($file);

    // Output the first line
    echo $lines[0];

    // Remove the first line
    array_shift($lines);

    // Save the remaining lines back into the file, using "\n" to keep the file's line breaks
    file_put_contents($file, implode('', $lines));

?>