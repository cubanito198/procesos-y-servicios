onmessage = function(datos){
    console.log("worker arrancado, vamos a trabajar")
    for(let i = 0;i<datos.data.length;i+=4){              // Recorro cada pixel
        let c = datos.data                                  // Cargo los datos de ese pixel
        /* GRIS
        let gris = Math.round((c[i] + c[i+1] + c[i+2])/3)   // Saco el promedio
        datos.data[i] = gris;                               // actualizo el color rojo para que sea gris
        datos.data[i+1] = gris;                             // actualizo el color verde para que sea gris
        datos.data[i+2] = gris;                             // actualizo el color azul para que sea gris
        */
        
        /* NEGATIVO
        datos.data[i] = 255-datos.data[i];                               // actualizo el color rojo para que sea gris
        datos.data[i+1] = 255-datos.data[i+1];                             // actualizo el color verde para que sea gris
        datos.data[i+2] = 255-datos.data[i+2];                             // actualizo el color azul para que sea gris
        */
        
         //UMBRAL 
        if(datos.data[i] < 100){
            datos.data[i] = 0;                              
            datos.data[i+1] = 0;                             
            datos.data[i+2] = 0;                             
        }else{
            datos.data[i] = 255;                            
            datos.data[i+1] = 255;                            
            datos.data[i+2] = 255;                          
        }
      }
      
      
      //console.log(datos.data)
      console.log("worker finalizado, devolvemos al hilo principal")
     postMessage(datos.data)
}
