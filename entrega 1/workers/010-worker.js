onmessage = function(datos){
    console.log("worker arrancado, vamos a trabajar")
    for(let i = 0;i<datos.data.length;i+=4){              // Recorro cada pixel
        let c = datos.data                                  // Cargo los datos de ese pixel
        let gris = Math.round((c[i] + c[i+1] + c[i+2])/3)   // Saco el promedio
        datos.data[i] = gris;                               // actualizo el color rojo para que sea gris
        datos.data[i+1] = gris;                             // actualizo el color verde para que sea gris
        datos.data[i+2] = gris;                             // actualizo el color azul para que sea gris
      }
      //console.log(datos.data)
      console.log("worker finalizado, devolvemos al hilo principal")
     postMessage(datos.data)
}
