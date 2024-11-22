onmessage = function(){                                 // El worker escucha
    console.log("ok hola");                             // Hace algo
    postMessage("ok soy el worker y vuelvo al proceso principal")       // Devuelve un mensaje al hilo principal
}
