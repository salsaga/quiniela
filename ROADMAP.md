## Requerimientos 

### 1. Posición y puntos del usuario en el header o subheader

**Qué queremos:** Un indicador discreto, arriba en la UI, que muestre la posición y los puntos del usuario en el torneo. Al hacer clic, redirige a la tabla de posiciones. No sé si lo mejor es rediseñar el header, o mejor dejar el header como está y agregar un subheader. Lo importante es que se vea bonito

---

### 2. Vista de tabla de posiciones 

**Qué queremos:** Una vista de tabla de posiciones que puede tener 3 columnas visibles: número de posición, nombre del usuario, y puntos (sin encabezados o que los encabezados sean íconos claros), si encontramos una forma elegante de hacerlo también podríamos mostrar cuántos diferencias y cuántos resultados exactos ha atinado el usuario, pero esto último no es tan importante


---

### 3. Info en tarjetas de partidos ya jugados

**Qué queremos:** Que una vez que se tiene el resultado final de un partido, aparezca un row sutil arriba de la línea principal con el marcador final y los puntos que obtuvo el usuario. Se me ocurre que el marcador final vaya justo encima de los inputs (ya bloqueados) de predicción, podría ir con un label a la izquierda, y con un borde para que se distinga con claridad. Los puntos podrían ir con más font weigh a la derecha. Tal vez sea buena idea implementar un lenguaje en que, por ejemplo, el resultado errado vaya en rojo (con un cero en rojo), el resultado acertado en verde, y el resultado exacto en dorado, pero no sé bien cómo representaríamos el punto extra por diferencia. En este punto estoy abierto a sugerencias.

---

### 4. Vista dinámica de partidos ordenados por fecha

**Qué queremos:** No sé si debería estar en otro chip posicionado a la derecha de 'grupos' cuando se estén jugando la fase de grupos, y a la derecha de 'octavos' cuando se esté jugando la fase de octavos. O podríamos, cuando corresponda, dividir el chip 'grupos' en dos partes, y una que diga 'en juego' o algo así. Pero siempre nos llevaría a la misma vista. Al entrar a esta página, debe posicionarnos automáticamente en los partidos de hoy. Las tarjetas de partidos en esta vista pueden verse distinto que en la vista que ya tenemos de 'grupos'. Puede ser algo como:

{TeamNameA}{TeamFlagA} vs {TeamFlagB}{TeamNameB}  -> en el header (aunque debe haber un indicador de a qué grupo o fase pertenece, pero no sé dónde colocarlo);

Luego abajo de {TeamNameA}, más o menos grande, los goles de TeamA, y abajo de {TeamNameB} los goles de TeamB
Abajo un desglose completo con, cuántas tarjetas amarillas y rojas, y una lista con "- 35' Fulano Goleador", "- 90' Sutaninho". La info de cada equipo en la columna correspondiente. Finalmente un subtítulo 'tu prediccón' y volver a poner los goles predichos en las columnas correspondientes. Luego podríamos poner el puntaje obtenido por la predicción bien desglosado. Y hasta abajo de todo un details con 'ver predicciones rivales' que abra una lista con las predicciones de ese partido de todos los usuarios

Idealmente el usuario debe entender que scrolleando hacia arriba puede ver partidos de días anteriores (puede que sea un poco más obvio que scrolleando hacia abajo vea partidos de días posteriores, aunque las tarjetas irían vacías o con una leyenda 'partido por jugar'). Una solución que se me ocurre es que cada partido sea un details que al abrir venga todo el desglose, así cabrían segmentos de fechas anteriores y posteriores


---

### 5. Spinner en el botón de enviar

**Qué queremos:** En la vida real los usuarios ya utilizaron el botón de enviar y no fue visulamente súper claro si la operación había tenido éxito (aunque rápidamente les llegó el email, pero aún así)


---

### 4. Depurar estilos

**Qué queremos:** Homogeneizar un poco más los estilos, por ejemplo los colores que se utilicen de manera más consistente. Tal vez introducir tailwind o al menos mejorar el sistema de variables. 


---

### 4. Unit tests mínimos

**Qué queremos:** Implementar unit tests para el nuevo archivo de 'scoring.py' 



---

### Considerar también

**Qué queremos:** Cuando lleguemos a las siguientes fases nos gustaría un simulador para que los usuarios vean como quedarían los partidos de la fase posterios con sus predicciones, esto se podría implementar incluso desde la fase de grupos aunque no es súper importante. En todo caso, para esa simulación quizá sería bueno que no tenga que ir a pedir info al servidor, sino que sea inmediato en cuánto se de clicj al botón correspondiente. ¿Tal vez valga la pena empezar a considerar react o alguna otra herramienta que nos permita robustecer el frontend (sólo si realmente vale la pena)? No sé si se pueda tener un sistema híbrido ligero, o quizá frameworks más ligeros. No sé si svelte, por ejemplo tenga más sentido. Si de plano es mejor seguir con una arquitectura similar a la que tenemos, pues también está bien.
