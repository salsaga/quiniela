## Requerimientos 

### 1. Posición y puntos del usuario en el header o subheader

**Qué queremos:** Un indicador discreto, arriba en la UI, que muestre la posición y los puntos del usuario en el torneo. Al hacer clic, redirige a la tabla de posiciones. No sé si lo mejor es rediseñar el header, o mejor dejar el header como está y agregar un subheader. Lo importante es que se vea bonito

#### Ajustes:
Al poner "🏆 1° 4pts" el title se desplaza a la derecha perdiendo simétría, además no resulta tan evidente que es un botón, ni qué hace, y ni siquiera sé si es tan entendible que esa info corresponde al usuario, porque además luego tenemos un ícono de usuario la derecha. Creo que sí necesitamos un rediseño, pero no sé bien como. Tal vez dejar arriba el title de identidad, de algún modo que no ocupe mucho espacio, y una seguna línea con lo demás aunque no sé en que orden. Incluso podríamos hacer visible el nombre de usuario y el botón de cerra sesión (aunque éste aún con un alert para cerrar sesión), pero no sé. Propón alternativas



---

### 2. Vista de tabla de posiciones 

**Qué queremos:** Una vista de tabla de posiciones que puede tener 3 columnas visibles: número de posición, nombre del usuario, y puntos (sin encabezados o que los encabezados sean íconos claros), si encontramos una forma elegante de hacerlo también podríamos mostrar cuántos diferencias y cuántos resultados exactos ha atinado el usuario, pero esto último no es tan importante

#### Ajustes:
Definitivamente no quiero el ícono 🎯 ahí. Una alternativaa podría ser un ícono hecho con svg que se vea más cómo una mira, y un 'dif' en lugar de '±'. Pero en cualquier caso esas columnas deben ser discretas e ir hasta laderecha. Me gusta el '#' en la columna de posición pero debemos ser coherentes, o usamos 🏆 o suamos # para posición (considerar para los ajustes del punto anterior). Me gusta que no tenga encabezado la columna de nombre, pero la de puntos creo que sí debería decir 'pts' y debería estar inmediatamente a la izquierda del nombre (conservándo su portagonismo, aunque no sé si con ese dorado, no me encanta que haya dos dorados distintos en la tabla, y creo que el dorado lo deberíamos reservar para sólo una de las columnas). Lo de las medallas para 1er, 2o y 3er lugar sí me gustó


---

### 3. Info en tarjetas de partidos ya jugados

**Qué queremos:** Que una vez que se tiene el resultado final de un partido, aparezca un row sutil arriba de la línea principal con el marcador final y los puntos que obtuvo el usuario. Se me ocurre que el marcador final vaya justo encima de los inputs (ya bloqueados) de predicción, podría ir con un label a la izquierda, y con un borde para que se distinga con claridad. Los puntos podrían ir con más font weigh a la derecha. Tal vez sea buena idea implementar un lenguaje en que, por ejemplo, el resultado errado vaya en rojo (con un cero en rojo), el resultado acertado en verde, y el resultado exacto en dorado, pero no sé bien cómo representaríamos el punto extra por diferencia. En este punto estoy abierto a sugerencias.

#### Ajustes:
El label final sin borde, debe decir 'final:' e ir pegado justo a la izquierda del marcador final, el cuál esta bien, pero lo podemos hacer un poquito más grande. . Más importatnte que eso: el usuario predijo 0-2 y el partido quedó 2-4, y se ve el 4pts en verde y el +1 en dorado, esos estilos bien, el problema es que el usario puede pensar que en total sacó 5 puntos. Creo que hay que desplazar la fecha otro par de días para ver más casos: uno de resultado sin punto extra y uno de resultado exacto con empate, y otro de resultado exacto con ganador. Y un detalle más, en el '3pts +1' el 3pts debería ir alineado con el '0pts' del caso no acertado y el +1 más a la derecha aunque se salga del subrayado.


---

### 4. Vista dinámica de partidos ordenados por fecha

**Qué queremos:** No sé si debería estar en otro chip posicionado a la derecha de 'grupos' cuando se estén jugando la fase de grupos, y a la derecha de 'octavos' cuando se esté jugando la fase de octavos. O podríamos, cuando corresponda, dividir el chip 'grupos' en dos partes, y una que diga 'en juego' o algo así. Pero siempre nos llevaría a la misma vista. Al entrar a esta página, debe posicionarnos automáticamente en los partidos de hoy. Las tarjetas de partidos en esta vista pueden verse distinto que en la vista que ya tenemos de 'grupos'. Puede ser algo como:

{TeamNameA}{TeamFlagA} vs {TeamFlagB}{TeamNameB}  -> en el header (aunque debe haber un indicador de a qué grupo o fase pertenece, pero no sé dónde colocarlo);

Luego abajo de {TeamNameA}, más o menos grande, los goles de TeamA, y abajo de {TeamNameB} los goles de TeamB
Abajo un desglose completo con, cuántas tarjetas amarillas y rojas, y una lista con "- 35' Fulano Goleador", "- 90' Sutaninho". La info de cada equipo en la columna correspondiente. Finalmente un subtítulo 'tu prediccón' y volver a poner los goles predichos en las columnas correspondientes. Luego podríamos poner el puntaje obtenido por la predicción bien desglosado. Y hasta abajo de todo un details con 'ver predicciones rivales' que abra una lista con las predicciones de ese partido de todos los usuarios

Idealmente el usuario debe entender que scrolleando hacia arriba puede ver partidos de días anteriores (puede que sea un poco más obvio que scrolleando hacia abajo vea partidos de días posteriores, aunque las tarjetas irían vacías o con una leyenda 'partido por jugar'). Una solución que se me ocurre es que cada partido sea un details que al abrir venga todo el desglose, así cabrían segmentos de fechas anteriores y posteriores

#### Ajustes:
Debemos tener el mismo elemento 'chevron' que tenemos en los details de grupo para que sea evidente que las tarjetas desglosadas de partidos jugados se pueden abrir. El 'vs debe ir en la misma lína que los equipos, y los goles visibles en el centro de sus respectivas columnas, hay que revisar los gaps para que se vea mejor el conjunto. Las tarjetas amarillas y rojas, también en el centro de sus respectivas columnas. En el desglose de puntos no necesitamos la fila total si no hay que sumar nada. El link de ver predicciones rivales que sea un poco más prominente, y también con un poco más de aire.


---

### 5. Spinner en el botón de enviar

**Qué queremos:** En la vida real los usuarios ya utilizaron el botón de enviar y no fue visulamente súper claro si la operación había tenido éxito (aunque rápidamente les llegó el email, pero aún así)

#### Sin ajustes, tengo que probarlo pero no es tan importante

---

### 6. Depurar estilos

**Qué queremos:** Homogeneizar un poco más los estilos, por ejemplo los colores que se utilicen de manera más consistente. Tal vez introducir tailwind o al menos mejorar el sistema de variables.

#### Sin ajustes


---

### 7. Unit tests mínimos

**Qué queremos:** Implementar unit tests para el nuevo archivo de 'scoring.py' 

#### Ajustes:
Se actualizó la redacción de las reglas. Hay que actualizar la pestaña reglas con lo siguiente:

- Si atinas al resultado del partido (ganador o empate): 3 puntos
- Si atinas diferencia de goles: 1 punto extra (excepto en empates). Este punto extra solo te lo puedes llevar si le atinaste al resultado del partido.
- Resultado exacto: 1 punto extra.
- Es decir, por un resultado exacto te llevas 5 puntos totales si hay ganador o 4 puntos totales si es empate.
- En play offs se considerará el marcador sin penales, calcula tu resultado pensando en que el partido puede durar hasta 120 minutos. (goles en tiempos extras sí cuentan)
- Para todas las fases, si su quiniela no está llena a las 11:59 pm del día previo a que empiecen los partidos, quedan fuera.

En realidad la lógica debería ser la misma (verificar), pero también hay que mejorar el código de scoring.py, evitemos líneas como esta: 
    return 0 if diff == 0 else (1 if diff > 0 else -1)
con un triple ternario
Tuve feedback: 'me está costando mucho leerla, está muy enredada'. Que sea mucho más legible porfa.

---

#### ESTO ÚLTIMO NO ENTRA EN ESTA SESIÓN 
### Considerar también

**Qué queremos:** Cuando lleguemos a las siguientes fases nos gustaría un simulador para que los usuarios vean como quedarían los partidos de la fase posterios con sus predicciones, esto se podría implementar incluso desde la fase de grupos aunque no es súper importante. En todo caso, para esa simulación quizá sería bueno que no tenga que ir a pedir info al servidor, sino que sea inmediato en cuánto se de clicj al botón correspondiente. ¿Tal vez valga la pena empezar a considerar react o alguna otra herramienta que nos permita robustecer el frontend (sólo si realmente vale la pena)? No sé si se pueda tener un sistema híbrido ligero, o quizá frameworks más ligeros. No sé si svelte, por ejemplo tenga más sentido. Si de plano es mejor seguir con una arquitectura similar a la que tenemos, pues también está bien.
#### ESTO ÚLTIMO NO ENTRA EN ESTA SESIÓN 
