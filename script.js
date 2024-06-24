document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('nav ul li a');
    links.forEach(link => {
        link.addEventListener('click', function() {
            link.style.color = 'orange';  // Cambiar el color al hacer clic
        });
    });
});




document.addEventListener("DOMContentLoaded", function () {
    const table = document.querySelector("table.data-table");
    if (table) {
        const cells = table.getElementsByTagName("td");
        for (let cell of cells) {
            if (!isNaN(cell.innerText) && cell.innerText.trim() !== "") {
                cell.style.backgroundColor = "gold";
            }
        }
    }
});

function aplicarEstilos() {
    var tabla = document.getElementById("contenido").querySelector("table");
    tabla.classList.toggle("estilos-encabezado");
    var filas = tabla.querySelectorAll("tr");
    filas.forEach(function (fila) {
        fila.classList.toggle("estilos-fila");
    });
    alert('Estilos aplicados');
}

function corregirTabla() {
    let tabla =  document.getElementById('contenido').querySelector('table');
    let datos = [];    
    for (var i = 1; i < tabla.rows.length; i++) {
        var fila = tabla.rows[i];
        var filaDatos = [];
        for (var j = 0; j < fila.cells.length; j++) {
            filaDatos.push(fila.cells[j].innerText);
        }
        datos.push(filaDatos);
    }
    fetch('/corregir_datos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        actualizarTabla(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
    alert('Datos corregidos');
}

function actualizarTabla(datosCorregidos) {
    let tabla = document.getElementById('contenido').querySelector('table');
    for (var i = 1; i < tabla.rows.length; i++) {
        var fila = tabla.rows[i];        
        for (var j = 0; j < fila.cells.length; j++) {
            var celda = fila.cells[j];
            celda.innerText = datosCorregidos[i - 1][j]['valor'];
            celda.setAttribute('style', datosCorregidos[i - 1][j]['estilo']);
        }
    }
}

function limpiarTabla() {
    var tabla = document.getElementById('contenido').querySelector('table');
    var caracteresBuscar = document.getElementById('caracteresBuscar').value;
    var caracteresArray = caracteresBuscar.split(',').map(function(caracter) {
        return caracter.trim();
    });
    let A = ["B", "B-", "B+", "C+", "C", "C-"];
    let D = ["D+", "D-", "F"];
    var celdas = tabla.querySelectorAll('td');

    celdas.forEach(function(celda) {
        if (caracteresArray.includes(celda.innerHTML.trim())) {
            celda.innerHTML = '';
        } else {
            let verfi = 0;
            for (var i = 0; i < A.length; i++) {
                if (celda.innerHTML.trim() === A[i]) {
                    celda.innerHTML = 'A';
                    verfi = 1;
                    break;
                }
            }
            if (verfi === 0) {
                for (var j = 0; j < D.length; j++) {
                    if (celda.innerHTML.trim() === D[j]) {
                        celda.innerHTML = 'D';
                        break;
                    }
                }
            }
        }
    });
    alert('Tabla limpiada');
}

function dejarUltimaPalabra() {
    var tabla = document.getElementById('contenido').querySelector('table');
    var encabezados = tabla.querySelectorAll('th');
    encabezados.forEach(function (encabezado) {
        var textoEncabezado = encabezado.textContent.trim();
        var palabras = textoEncabezado.split(' ');
        var ultimaPalabra = palabras[palabras.length - 1];
        encabezado.textContent = ultimaPalabra;
    });
    alert('Última palabra dejada');
}

function enviarDatos() {
    var tablaHTML = document.getElementById('contenido').innerHTML;
    document.getElementById('tabla-datos').value = tablaHTML;
    document.getElementById('export-form').submit();
}
