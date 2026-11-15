CREATE TABLE IF NOT EXISTS usuarios (
    id                  INT GENERATED ALWAYS AS IDENTITY,
    identificacion      VARCHAR(200) NOT NULL UNIQUE,
    contrasena_hasheada VARCHAR(250) NOT NULL,
    rol                 VARCHAR(25)  NOT NULL
                        CHECK (rol IN ('administrador', 'profesor', 'estudiante')),
    creado_en           TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT pk_usuarios PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS estudiantes (
    id_estudiante INT GENERATED ALWAYS AS IDENTITY,
    id_usuario    INT          NOT NULL UNIQUE,
    nombre        VARCHAR(100) NOT NULL,
    grupo         VARCHAR(10)  NOT NULL,
    horas_meta    INT NOT NULL

    CONSTRAINT pk_estudiantes PRIMARY KEY (id_estudiante),
    CONSTRAINT fk_estudiantes_usuarios FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS administradores (
    id_administrador INT GENERATED ALWAYS AS IDENTITY,
    id_usuario       INT          NOT NULL UNIQUE,
    nombre           VARCHAR(100) NOT NULL,

    CONSTRAINT pk_administradores PRIMARY KEY (id_administrador),
    CONSTRAINT fk_administradores_usuarios FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS profesores (
    id_profesor INT GENERATED ALWAYS AS IDENTITY,
    id_usuario  INT          NOT NULL UNIQUE,
    nombre      VARCHAR(100) NOT NULL,

    CONSTRAINT pk_profesores PRIMARY KEY (id_profesor),
    CONSTRAINT fk_profesores_usuarios FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS proyectos (
    id_proyecto     INT GENERATED ALWAYS AS IDENTITY,
    id_profesor     INT           NOT NULL,
    nombre          VARCHAR(100)  NOT NULL,
    fecha_inicio    DATE          NOT NULL,
    descripcion     TEXT,
    lugar           VARCHAR(100)  NOT NULL,
    cupos           INT           NOT NULL CHECK (cupos >= 0),
    horas_otorgadas NUMERIC(5,2)  NOT NULL CHECK (horas_otorgadas > 0),

    CONSTRAINT pk_proyectos PRIMARY KEY (id_proyecto),
    CONSTRAINT fk_proyectos_profesores FOREIGN KEY (id_profesor)
        REFERENCES profesores(id_profesor)
);

CREATE TABLE IF NOT EXISTS horas (
    id_horas      INT GENERATED ALWAYS AS IDENTITY,
    id_estudiante INT           NOT NULL,
    id_profesor   INT           NOT NULL,
    id_proyecto   INT           NOT NULL,
    cantidad      NUMERIC(5,2)  NOT NULL CHECK (cantidad > 0),
    fecha         DATE          NOT NULL DEFAULT CURRENT_DATE,

    CONSTRAINT pk_horas PRIMARY KEY (id_horas),
    CONSTRAINT fk_horas_estudiantes FOREIGN KEY (id_estudiante)
        REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    CONSTRAINT fk_horas_profesores FOREIGN KEY (id_profesor)
        REFERENCES profesores(id_profesor),
    CONSTRAINT fk_horas_proyectos FOREIGN KEY (id_proyecto)
        REFERENCES proyectos(id_proyecto)
);

CREATE TABLE IF NOT EXISTS inscripciones (
    id_inscripcion INT GENERATED ALWAYS AS IDENTITY,
    id_estudiante  INT NOT NULL,
    id_proyecto    INT NOT NULL,

    CONSTRAINT pk_inscripciones PRIMARY KEY (id_inscripcion),
    CONSTRAINT uq_inscripcion UNIQUE (id_estudiante, id_proyecto),
    CONSTRAINT fk_inscripciones_estudiantes FOREIGN KEY (id_estudiante)
        REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    CONSTRAINT fk_inscripciones_proyectos FOREIGN KEY (id_proyecto)
        REFERENCES proyectos(id_proyecto) ON DELETE CASCADE
);
