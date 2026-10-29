-- ============================================================
-- BASE DE DATOS: Centro de Competencias Digitales (CCD) - UNAB
-- Archivo: 01_crear_base_datos.sql
-- Ejecutar en PostgreSQL como usuario n8nuser
-- ============================================================

-- ── Crear esquema dedicado ────────────────────────────────
CREATE SCHEMA IF NOT EXISTS ccd;

-- ── Tabla de programas académicos ────────────────────────
CREATE TABLE IF NOT EXISTS ccd.programas (
    id_programa     SERIAL PRIMARY KEY,
    codigo          VARCHAR(10) UNIQUE NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    facultad        VARCHAR(100)
);

-- ── Tabla de cursos de competencias digitales ─────────────
CREATE TABLE IF NOT EXISTS ccd.cursos (
    id_curso        SERIAL PRIMARY KEY,
    codigo_curso    VARCHAR(10) UNIQUE NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    pilar           VARCHAR(50) NOT NULL,  -- 'basico', 'analitica', 'transformativo'
    obligatorio     BOOLEAN DEFAULT FALSE,
    creditos        INT DEFAULT 2,
    descripcion     TEXT
);

-- ── Tabla de estudiantes ──────────────────────────────────
CREATE TABLE IF NOT EXISTS ccd.estudiantes (
    id_estudiante   VARCHAR(12) PRIMARY KEY,  -- cédula o código UNAB
    nombre          VARCHAR(100) NOT NULL,
    apellido        VARCHAR(100) NOT NULL,
    email           VARCHAR(150),
    telegram_id     VARCHAR(50),
    id_programa     INT REFERENCES ccd.programas(id_programa),
    semestre_actual INT,
    fecha_ingreso   DATE
);

-- ── Tabla de cursos tomados por estudiante ────────────────
CREATE TABLE IF NOT EXISTS ccd.cursos_tomados (
    id              SERIAL PRIMARY KEY,
    id_estudiante   VARCHAR(12) REFERENCES ccd.estudiantes(id_estudiante),
    id_curso        INT REFERENCES ccd.cursos(id_curso),
    semestre        VARCHAR(10),   -- ej: '2025-1'
    estado          VARCHAR(20) DEFAULT 'en_curso',  -- 'aprobado','reprobado','en_curso'
    nota            NUMERIC(4,2),
    fecha_inicio    DATE,
    fecha_fin       DATE
);

-- ── Tabla de tareas/solicitudes (para Google Sheets) ─────
CREATE TABLE IF NOT EXISTS ccd.solicitudes (
    id              SERIAL PRIMARY KEY,
    id_estudiante   VARCHAR(12),
    nombre_estudiante VARCHAR(200),
    tipo_solicitud  VARCHAR(100),
    descripcion     TEXT,
    fecha           TIMESTAMP DEFAULT NOW(),
    estado          VARCHAR(20) DEFAULT 'pendiente',
    enviado_sheets  BOOLEAN DEFAULT FALSE
);

-- ── Tabla de conversaciones del chatbot ───────────────────
CREATE TABLE IF NOT EXISTS ccd.conversaciones (
    id              SERIAL PRIMARY KEY,
    telegram_id     VARCHAR(50),
    id_estudiante   VARCHAR(12),
    pregunta        TEXT,
    respuesta       TEXT,
    timestamp       TIMESTAMP DEFAULT NOW(),
    tipo            VARCHAR(50)  -- 'consulta','solicitud','saludo'
);

-- ============================================================
-- DATOS: Programas académicos
-- ============================================================
INSERT INTO ccd.programas (codigo, nombre, facultad) VALUES
('ING-SIS', 'Ingeniería de Sistemas', 'Ingeniería'),
('ING-IND', 'Ingeniería Industrial', 'Ingeniería'),
('ING-ELE', 'Ingeniería Electrónica', 'Ingeniería'),
('ADM-EMP', 'Administración de Empresas', 'Ciencias Económicas'),
('CONT',    'Contaduría Pública', 'Ciencias Económicas'),
('DER',     'Derecho', 'Ciencias Jurídicas'),
('PSI',     'Psicología', 'Ciencias de la Salud'),
('MED',     'Medicina', 'Ciencias de la Salud'),
('COM-SOC', 'Comunicación Social', 'Humanidades'),
('DIS-GRA', 'Diseño Gráfico', 'Humanidades'),
('ARQ',     'Arquitectura', 'Arquitectura'),
('EDU',     'Educación', 'Humanidades')
ON CONFLICT DO NOTHING;

-- ============================================================
-- DATOS: Cursos de competencias digitales
-- ============================================================
INSERT INTO ccd.cursos (codigo_curso, nombre, pilar, obligatorio, creditos, descripcion) VALUES
-- Pilar 1: Básico (obligatorio)
('CD-101', 'Interacción Digital', 'basico', TRUE, 2,
 'Curso obligatorio. Fundamentos de la ciudadanía digital, uso ético de tecnologías, seguridad en línea y comunicación digital efectiva.'),

-- Pilar 2: Analítica y Contenido Digital (elige 1)
('CD-201', 'Habilidades en Analítica Digital', 'analitica', FALSE, 2,
 'Introducción al análisis de datos, visualización, uso de hojas de cálculo avanzadas y dashboards para toma de decisiones.'),
('CD-202', 'Productividad y Marca Personal Digital', 'analitica', FALSE, 2,
 'Gestión del tiempo digital, herramientas de productividad, construcción de marca personal y presencia profesional en redes.'),
('CD-203', 'Creación de Contenidos Digitales', 'analitica', FALSE, 2,
 'Diseño y producción de contenido digital: videos, podcasts, infografías y materiales educativos digitales.'),

-- Pilar 3: Tecnologías Transformativas (elige 1)
('CD-301', 'IA Generativa', 'transformativo', FALSE, 2,
 'Fundamentos y aplicaciones prácticas de la inteligencia artificial generativa: ChatGPT, Midjourney, Copilot y otras herramientas de IA aplicadas al contexto profesional.'),
('CD-302', 'Marco Legal Digital', 'transformativo', FALSE, 2,
 'Derechos digitales, protección de datos personales (Ley 1581), propiedad intelectual en entornos digitales y regulación de IA.'),
('CD-303', 'Cuidado y Bienestar Digital', 'transformativo', FALSE, 2,
 'Salud mental digital, gestión del bienestar en entornos tecnológicos, desconexión digital y uso saludable de dispositivos.')
ON CONFLICT DO NOTHING;

-- ============================================================
-- DATOS SINTÉTICOS: 30 estudiantes
-- ============================================================
INSERT INTO ccd.estudiantes (id_estudiante, nombre, apellido, email, id_programa, semestre_actual, fecha_ingreso) VALUES
('1098765432', 'Laura',     'Martínez',    'l.martinez@unab.edu.co',   1, 4, '2023-01-15'),
('1098765433', 'Carlos',    'Rodríguez',   'c.rodriguez@unab.edu.co',  1, 6, '2022-01-15'),
('1098765434', 'Ana',       'López',       'a.lopez@unab.edu.co',      2, 3, '2023-07-15'),
('1098765435', 'Jhon',      'García',      'j.garcia@unab.edu.co',     2, 5, '2022-07-15'),
('1098765436', 'María',     'Hernández',   'm.hernandez@unab.edu.co',  3, 2, '2024-01-15'),
('1098765437', 'Luis',      'Torres',      'l.torres@unab.edu.co',     3, 7, '2021-07-15'),
('1098765438', 'Sofía',     'Ramírez',     's.ramirez@unab.edu.co',    4, 4, '2023-01-15'),
('1098765439', 'Diego',     'Vargas',      'd.vargas@unab.edu.co',     4, 3, '2023-07-15'),
('1098765440', 'Valentina', 'Castro',      'v.castro@unab.edu.co',     5, 5, '2022-07-15'),
('1098765441', 'Andrés',    'Morales',     'a.morales@unab.edu.co',    5, 6, '2022-01-15'),
('1098765442', 'Camila',    'Jiménez',     'c.jimenez@unab.edu.co',    6, 4, '2023-01-15'),
('1098765443', 'Sebastián', 'Díaz',        's.diaz@unab.edu.co',       6, 2, '2024-01-15'),
('1098765444', 'Isabella',  'Reyes',       'i.reyes@unab.edu.co',      7, 5, '2022-07-15'),
('1098765445', 'Felipe',    'Gómez',       'f.gomez@unab.edu.co',      7, 3, '2023-07-15'),
('1098765446', 'Natalia',   'Sánchez',     'n.sanchez@unab.edu.co',    8, 6, '2022-01-15'),
('1098765447', 'Mateo',     'Perez',       'm.perez@unab.edu.co',      8, 4, '2023-01-15'),
('1098765448', 'Luciana',   'Flores',      'l.flores@unab.edu.co',     9, 3, '2023-07-15'),
('1098765449', 'Santiago',  'Ruiz',        's.ruiz@unab.edu.co',       9, 5, '2022-07-15'),
('1098765450', 'Daniela',   'Núñez',       'd.nunez@unab.edu.co',      10, 2, '2024-01-15'),
('1098765451', 'Nicolás',   'Medina',      'n.medina@unab.edu.co',     10, 4, '2023-01-15'),
('1098765452', 'Gabriela',  'Ortega',      'g.ortega@unab.edu.co',     11, 6, '2022-01-15'),
('1098765453', 'Alejandro', 'Aguilar',     'a.aguilar@unab.edu.co',    11, 3, '2023-07-15'),
('1098765454', 'Mariana',   'Mendoza',     'm.mendoza@unab.edu.co',    12, 4, '2023-01-15'),
('1098765455', 'Ricardo',   'Guerrero',    'r.guerrero@unab.edu.co',   12, 5, '2022-07-15'),
('1098765456', 'Paulina',   'Ríos',        'p.rios@unab.edu.co',       1,  7, '2021-07-15'),
('1098765457', 'Esteban',   'Delgado',     'e.delgado@unab.edu.co',    2,  2, '2024-01-15'),
('1098765458', 'Juanita',   'Vega',        'j.vega@unab.edu.co',       3,  5, '2022-07-15'),
('1098765459', 'Tomás',     'Rojas',       't.rojas@unab.edu.co',      4,  3, '2023-07-15'),
('1098765460', 'Manuela',   'Herrera',     'm.herrera@unab.edu.co',    5,  6, '2022-01-15'),
('1098765461', 'Simón',     'Molina',      's.molina@unab.edu.co',     6,  4, '2023-01-15')
ON CONFLICT DO NOTHING;

-- ============================================================
-- DATOS SINTÉTICOS: cursos tomados por estudiantes
-- Regla: cada estudiante debe tomar 3 cursos:
--   CD-101 (obligatorio) + 1 de analitica + 1 de transformativo
-- ============================================================
INSERT INTO ccd.cursos_tomados (id_estudiante, id_curso, semestre, estado, nota, fecha_inicio, fecha_fin) VALUES
-- Laura Martínez: CD-101 aprobado, CD-201 aprobado, CD-301 en curso
('1098765432', 1, '2023-2', 'aprobado', 4.2, '2023-07-15', '2023-11-30'),
('1098765432', 2, '2024-1', 'aprobado', 3.8, '2024-01-15', '2024-05-30'),
('1098765432', 5, '2024-2', 'en_curso', NULL, '2024-07-15', NULL),

-- Carlos Rodríguez: los 3 aprobados
('1098765433', 1, '2022-2', 'aprobado', 4.5, '2022-07-15', '2022-11-30'),
('1098765433', 3, '2023-1', 'aprobado', 4.0, '2023-01-15', '2023-05-30'),
('1098765433', 6, '2023-2', 'aprobado', 3.7, '2023-07-15', '2023-11-30'),

-- Ana López: CD-101 aprobado, resto en curso
('1098765434', 1, '2024-1', 'aprobado', 3.5, '2024-01-15', '2024-05-30'),
('1098765434', 4, '2024-2', 'en_curso', NULL, '2024-07-15', NULL),

-- Jhon García: CD-101 aprobado, CD-202 aprobado, CD-302 aprobado
('1098765435', 1, '2023-1', 'aprobado', 4.1, '2023-01-15', '2023-05-30'),
('1098765435', 3, '2023-2', 'aprobado', 3.9, '2023-07-15', '2023-11-30'),
('1098765435', 7, '2024-1', 'aprobado', 4.3, '2024-01-15', '2024-05-30'),

-- María Hernández: solo CD-101 en curso (semestre 2)
('1098765436', 1, '2024-2', 'en_curso', NULL, '2024-07-15', NULL),

-- Luis Torres: todos aprobados (semestre 7)
('1098765437', 1, '2021-2', 'aprobado', 4.8, '2021-07-15', '2021-11-30'),
('1098765437', 2, '2022-1', 'aprobado', 4.5, '2022-01-15', '2022-05-30'),
('1098765437', 5, '2022-2', 'aprobado', 4.7, '2022-07-15', '2022-11-30'),

-- Sofía Ramírez
('1098765438', 1, '2023-2', 'aprobado', 3.6, '2023-07-15', '2023-11-30'),
('1098765438', 4, '2024-1', 'aprobado', 4.0, '2024-01-15', '2024-05-30'),
('1098765438', 6, '2024-2', 'en_curso', NULL, '2024-07-15', NULL),

-- Diego Vargas
('1098765439', 1, '2024-1', 'aprobado', 3.8, '2024-01-15', '2024-05-30'),
('1098765439', 2, '2024-2', 'en_curso', NULL, '2024-07-15', NULL),

-- Valentina Castro: todos aprobados
('1098765440', 1, '2022-2', 'aprobado', 4.3, '2022-07-15', '2022-11-30'),
('1098765440', 3, '2023-1', 'aprobado', 4.1, '2023-01-15', '2023-05-30'),
('1098765440', 7, '2023-2', 'aprobado', 3.9, '2023-07-15', '2023-11-30'),

-- Andrés Morales
('1098765441', 1, '2022-1', 'aprobado', 4.0, '2022-01-15', '2022-05-30'),
('1098765441', 4, '2022-2', 'aprobado', 3.7, '2022-07-15', '2022-11-30'),
('1098765441', 5, '2023-1', 'aprobado', 4.2, '2023-01-15', '2023-05-30')
ON CONFLICT DO NOTHING;

-- ============================================================
-- VISTAS ÚTILES PARA EL CHATBOT
-- ============================================================

-- Vista: estado completo de un estudiante en la ruta CCD
CREATE OR REPLACE VIEW ccd.v_estado_estudiante AS
SELECT
    e.id_estudiante,
    e.nombre || ' ' || e.apellido AS nombre_completo,
    e.email,
    p.nombre AS programa,
    e.semestre_actual,
    COUNT(ct.id) AS cursos_tomados,
    SUM(CASE WHEN ct.estado = 'aprobado' THEN 1 ELSE 0 END) AS cursos_aprobados,
    SUM(CASE WHEN ct.estado = 'en_curso' THEN 1 ELSE 0 END) AS cursos_en_curso,
    CASE
        WHEN SUM(CASE WHEN ct.estado = 'aprobado' THEN 1 ELSE 0 END) >= 3 THEN 'Ruta completada ✓'
        WHEN COUNT(ct.id) = 0 THEN 'Sin cursos inscritos'
        ELSE 'En progreso'
    END AS estado_ruta
FROM ccd.estudiantes e
LEFT JOIN ccd.programas p ON e.id_programa = p.id_programa
LEFT JOIN ccd.cursos_tomados ct ON e.id_estudiante = ct.id_estudiante
GROUP BY e.id_estudiante, e.nombre, e.apellido, e.email, p.nombre, e.semestre_actual;

-- Vista: cursos pendientes por estudiante
CREATE OR REPLACE VIEW ccd.v_cursos_pendientes AS
SELECT
    e.id_estudiante,
    e.nombre || ' ' || e.apellido AS nombre_completo,
    c.codigo_curso,
    c.nombre AS curso_pendiente,
    c.pilar,
    c.obligatorio
FROM ccd.estudiantes e
CROSS JOIN ccd.cursos c
WHERE NOT EXISTS (
    SELECT 1 FROM ccd.cursos_tomados ct
    WHERE ct.id_estudiante = e.id_estudiante
    AND ct.id_curso = c.id_curso
    AND ct.estado IN ('aprobado', 'en_curso')
)
ORDER BY e.id_estudiante, c.pilar;

-- ============================================================
-- Verificación final
-- ============================================================
SELECT 'Programas:'   AS tabla, COUNT(*) AS registros FROM ccd.programas
UNION ALL
SELECT 'Cursos:',      COUNT(*) FROM ccd.cursos
UNION ALL
SELECT 'Estudiantes:', COUNT(*) FROM ccd.estudiantes
UNION ALL
SELECT 'Cursos tomados:', COUNT(*) FROM ccd.cursos_tomados;
