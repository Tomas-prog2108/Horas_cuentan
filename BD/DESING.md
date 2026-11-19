# Diseño de la base de datos

## Sistema de control de horas de servicio social

## 1. Propósito

El propósito de esta base de datos es organizar y controlar la información relacionada con las horas de servicio social que realizan los estudiantes de la institución.

El proyecto busca solucionar el problema de llevar un registro manual o poco organizado de las horas que cada estudiante ha realizado. Con esta base de datos se podrá almacenar la información de los usuarios, estudiantes, docentes, proyectos de servicio social y las horas realizadas.

De esta manera, se busca facilitar el seguimiento de las horas sociales y permitir que los estudiantes y docentes puedan consultar y gestionar la información de una forma más organizada.

---

## 2. Alcance

La base de datos estará enfocada en el registro y seguimiento del servicio social de los estudiantes de la institución.

### El sistema permitirá manejar:

- Información de los usuarios del sistema.
- Información de los estudiantes.
- Información de los docentes encargados.
- Información de los proyectos de servicio social.
- Registro de las horas realizadas por los estudiantes.
- Seguimiento y validación de las horas realizadas.
- Consulta de las horas acumuladas por cada estudiante.

### El sistema no manejará:

- Calificaciones académicas.
- Asistencia general a clases.
- Información financiera de la institución.
- Matrículas académicas.
- Pagos.
- Información médica de los estudiantes.

El objetivo es mantener la base de datos enfocada en el control de las horas de servicio social.

---

## 3. Entidades

Las principales entidades de la base de datos serán las siguientes:

| Entidad | ¿Qué representa? |
|---|---|
| Usuario | Persona que tiene acceso al sistema y sus datos básicos de identificación. |
| Estudiante | Estudiante que debe realizar y registrar sus horas de servicio social. |
| Docente | Docente encargado de supervisar o validar las horas y proyectos. |
| Proyecto | Proyecto o actividad de servicio social, incluyendo la cantidad de horas establecidas para su realización. |
| Horas | Registro de las horas de servicio social realizadas por un estudiante. |
| Administrador | El administrador registra los docentes y estudiantes |
| Inscripciones | Entidad media donde se van a mostrar la relación de los estudiantes y los proyectos |

### Usuario

La tabla `usuario` almacenará la información necesaria para identificar a las personas que utilizan el sistema.

Esta tabla permitirá manejar los datos de acceso y diferenciar los diferentes tipos de usuarios, principalmente estudiantes y docentes.

Algunos datos que puede contener son:

- Identificador del usuario.
- Nombre de usuario.
- Correo.
- Contraseña.
- Tipo o rol de usuario.

La información de acceso se mantiene separada de la información específica de estudiantes y docentes para evitar repetir datos.

### Estudiantes

La tabla `estudiantes` almacenará la información propia de los estudiantes que realizan el servicio social.

Algunos datos que puede contener son:

- Identificador del estudiante.
- Nombre.
- Apellido.
- Documento de identificación.
- Grado o grupo.
- Identificador del usuario.

Esta tabla permitirá relacionar a cada estudiante con sus registros de horas.

### Docente

La tabla `docente` almacenará la información de los docentes encargados de supervisar los proyectos y validar las horas realizadas por los estudiantes.

Algunos datos que puede contener son:

- Identificador del docente.
- Nombre.
- Apellido.
- Correo.
- Identificador del usuario.

### Proyectos

La tabla `proyectos` representará los diferentes proyectos o actividades disponibles para realizar el servicio social.

Algunos datos que puede contener son:

- Identificador del proyecto.
- Nombre del proyecto.
- Descripción.
- Fecha de inicio.
- Fecha de finalización.
- Cantidad de horas establecidas para el proyecto.
- Estado del proyecto.
- Docente encargado.

Esta tabla permitirá conocer los proyectos disponibles, la cantidad de horas que requiere cada uno y el docente responsable.

### Horas

La tabla `horas` almacenará los registros de las horas de servicio social realizadas por los estudiantes.

Algunos datos que puede contener son:

- Identificador del registro.
- Estudiante que realizó las horas.
- Proyecto en el que se realizaron.
- Cantidad de horas realizadas.
- Fecha.
- Estado de validación.
- Observaciones.

Esta será una de las tablas principales del sistema, ya que permitirá llevar el seguimiento del progreso de cada estudiante.

---

## 4. Relaciones entre las entidades

Las tablas estarán relacionadas de la siguiente manera:

### Usuario - Estudiante

Un usuario puede estar asociado a un estudiante y un estudiante tendrá un usuario para ingresar al sistema.

**Relación: 1:1**

Esto permite separar la información de acceso de los datos específicos del estudiante.

### Usuario - Docente

Un usuario puede estar asociado a un docente y un docente tendrá un usuario para ingresar al sistema.

**Relación: 1:1**

De esta manera, los datos de acceso se mantienen separados de la información propia del docente.

### Docente - Proyecto

Un docente puede estar encargado de varios proyectos, mientras que cada proyecto tendrá un docente encargado.

**Relación: 1:N**

### Estudiante - Horas

Un estudiante puede tener muchos registros de horas, ya que puede realizar diferentes actividades durante el cumplimiento del servicio social.

Cada registro de horas pertenece a un estudiante.

**Relación: 1:N**

### Proyecto - Horas

Un proyecto puede tener muchos registros de horas correspondientes a diferentes registros realizados.

Cada registro de horas pertenece a un proyecto específico.

**Relación: 1:N**

De esta manera, la tabla `horas` permite relacionar los registros de horas con el estudiante y el proyecto correspondiente.

---

## 5. Decisiones y optimizaciones

Para que la base de datos sea organizada y eficiente se tomarán diferentes decisiones de diseño.

### Claves primarias

Cada tabla tendrá una clave primaria que permitirá identificar de manera única cada registro.

Por ejemplo:

- `id_usuario`
- `id_estudiante`
- `id_docente`
- `id_proyecto`
- `id_hora`

Esto evita confusiones y facilita la búsqueda de información.

### Claves foráneas

Se utilizarán claves foráneas para conectar las diferentes tablas.

Por ejemplo:

- `estudiantes` se relacionará con `usuario`.
- `docente` se relacionará con `usuario`.
- `proyectos` se relacionará con `docente`.
- `horas` se relacionará con `estudiantes`.
- `horas` se relacionará con `proyectos`.

Las claves foráneas permitirán mantener la relación entre los datos y evitar registros que hagan referencia a información inexistente.

### Evitar información repetida

La información estará dividida en diferentes tablas para evitar almacenar los mismos datos varias veces.

Por ejemplo, los datos de acceso de un estudiante estarán en `usuario`, mientras que sus datos específicos estarán en `estudiantes`.

De igual manera, no será necesario guardar nuevamente el nombre del proyecto cada vez que se registre una hora. El registro utilizará el identificador del proyecto.

### Índices

Se podrán utilizar índices en campos que sean consultados frecuentemente, como:

- Correo del usuario.
- Documento del estudiante.
- Identificador del estudiante en `horas`.
- Identificador del proyecto en `horas`.
- Estado de las horas.

Esto ayudará a mejorar el rendimiento de las consultas cuando aumente la cantidad de información.

### Restricciones

Se utilizarán restricciones para evitar información incorrecta.

Por ejemplo:

- Las horas registradas no podrán tener valores negativos.
- Un registro de horas debe pertenecer a un estudiante existente.
- Un registro de horas debe pertenecer a un proyecto existente.
- Un proyecto debe tener un docente encargado.
- Los correos o documentos que deban ser únicos no podrán repetirse.
- Los campos obligatorios no podrán quedar vacíos.

---

## 6. Funcionamiento general

El funcionamiento del sistema será el siguiente:

1. Se registran los usuarios que tendrán acceso al sistema.
2. Se registra la información correspondiente a los estudiantes y docentes.
3. Los docentes pueden estar encargados de diferentes proyectos de servicio social.
4. Se registran las horas realizadas por cada estudiante.
5. Se relaciona cada registro de horas con el estudiante y el proyecto correspondiente.
6. El docente puede revisar y validar los registros de horas.
7. El sistema permite consultar las horas realizadas por cada estudiante.
8. El estudiante puede conocer su progreso y las horas que tiene registradas.

De esta manera, el sistema permite llevar un control más organizado del cumplimiento del servicio social.

---

## 7. Limitaciones

Una de las principales limitaciones del sistema es que está enfocado específicamente en el seguimiento del servicio social y no en la gestión académica completa de la institución.

Por esta razón, no incluye procesos como calificaciones, asistencia general, matrículas o pagos.

Otra limitación es que la información depende de que los usuarios registren correctamente las horas realizadas y de que los docentes realicen la validación correspondiente.

Además, en esta primera versión no se contempla un sistema de notificaciones automáticas para avisar a los estudiantes cuando una hora haya sido aprobada o cuando exista alguna actualización en sus registros.

---

## 8. Proyección del proyecto

En futuras versiones, el sistema podría ampliarse con nuevas funcionalidades, como:

- Notificaciones automáticas para los estudiantes.
- Generación de certificados de cumplimiento.
- Estadísticas sobre el avance de los estudiantes.
- Filtros para buscar estudiantes y proyectos.
- Historial de cambios en los registros.
- Panel de administración para docentes.
- Sistema de alertas para estudiantes que tengan pocas horas registradas.

Estas funcionalidades permitirían mejorar el sistema sin cambiar su objetivo principal.

---

## 9. Conclusión

El diseño de esta base de datos busca proporcionar una estructura organizada para controlar las horas de servicio social de los estudiantes de la institución.

Las cinco tablas principales, `usuario`, `estudiantes`, `docente`, `proyectos` y `horas`, permiten separar la información de acuerdo con su función y establecer relaciones entre los diferentes elementos del sistema.

La tabla `horas` cumple un papel fundamental porque permite registrar el tiempo realizado por cada estudiante y relacionarlo con el proyecto correspondiente. A su vez, los docentes pueden supervisar los proyectos y validar los registros.

El uso de claves primarias, claves foráneas, restricciones e índices permitirá mantener la información organizada, evitar duplicaciones y facilitar las consultas.

Este diseño servirá como base para desarrollar el archivo `schema.sql`, donde se crearán las tablas, relaciones y restricciones necesarias, y posteriormente el archivo `queries.sql`, donde se realizarán las operaciones para gestionar y consultar la información.


Video: https://youtu.be/BqZrUN-cCck?si=TKEzlkBE155_4EpP