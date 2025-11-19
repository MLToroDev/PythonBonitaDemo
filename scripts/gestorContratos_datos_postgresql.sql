-- ============================================================================
-- Script de carga de datos para PostgreSQL
-- Adaptado del modelo SQLAlchemy (bdm_models.py)
-- Esquema: SeguimientoDAP
-- ============================================================================
-- Nota:
--   * Este script está diseñado para PostgreSQL, NO para H2 (Bonita)
--   * Usa UUIDs en lugar de PERSISTENCEID
--   * Las tablas están en el esquema 'SeguimientoDAP'
--   * Ejecuta este script después de crear las tablas con init_db.py
-- ============================================================================

-- Configurar el esquema por defecto
SET search_path TO "SeguimientoDAP", public;

-- =============================
-- 1. CONTRATOS INTERADMINISTRATIVOS
-- =============================
INSERT INTO "SeguimientoDAP".contrato_inter_administrativo (id, numero_contrato, supervisor, contratista)
VALUES 
    ('00000000-0000-0000-0000-000000000002'::uuid, 'CIA-2024-002', 1002, 2002),
    ('00000000-0000-0000-0000-000000000003'::uuid, 'CIA-2024-003', 1003, 2003);

-- =============================
-- 2. COMPONENTES Y SUBCOMPONENTES
-- =============================
-- Componentes principales (sin padre)
INSERT INTO "SeguimientoDAP".componente (id, indice, descripcion, contrato_marco_id, componente_padre_id)
VALUES 
    ('00000000-0000-0000-0000-000000000105'::uuid, 1, 'Componente de Desarrollo de Software', '00000000-0000-0000-0000-000000000002'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000106'::uuid, 2, 'Componente de Mantenimiento y Soporte', '00000000-0000-0000-0000-000000000002'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000109'::uuid, 1, 'Componente de Capacitación y Formación', '00000000-0000-0000-0000-000000000003'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000110'::uuid, 2, 'Componente de Auditoría y Control', '00000000-0000-0000-0000-000000000003'::uuid, NULL);

-- Subcomponentes (con padre)
INSERT INTO "SeguimientoDAP".componente (id, indice, descripcion, contrato_marco_id, componente_padre_id)
VALUES 
    ('00000000-0000-0000-0000-000000000107'::uuid, 1, 'Subcomponente de Aplicaciones Web', '00000000-0000-0000-0000-000000000002'::uuid, '00000000-0000-0000-0000-000000000105'::uuid),
    ('00000000-0000-0000-0000-000000000108'::uuid, 2, 'Subcomponente de Aplicaciones Móviles', '00000000-0000-0000-0000-000000000002'::uuid, '00000000-0000-0000-0000-000000000105'::uuid),
    ('00000000-0000-0000-0000-000000000111'::uuid, 1, 'Subcomponente de Capacitación Presencial', '00000000-0000-0000-0000-000000000003'::uuid, '00000000-0000-0000-0000-000000000109'::uuid),
    ('00000000-0000-0000-0000-000000000112'::uuid, 2, 'Subcomponente de Capacitación Virtual', '00000000-0000-0000-0000-000000000003'::uuid, '00000000-0000-0000-0000-000000000109'::uuid);

-- =============================
-- 3. OBJETIVOS POR COMPONENTE
-- =============================
INSERT INTO "SeguimientoDAP".objetivo_contrato (id, indice, descripcion, componente_id)
VALUES 
    ('00000000-0000-0000-0000-000000000201'::uuid, 1, 'Desarrollar aplicaciones web modernas y responsivas', '00000000-0000-0000-0000-000000000105'::uuid),
    ('00000000-0000-0000-0000-000000000202'::uuid, 2, 'Implementar arquitectura de microservicios', '00000000-0000-0000-0000-000000000105'::uuid),
    ('00000000-0000-0000-0000-000000000203'::uuid, 3, 'Garantizar escalabilidad y rendimiento de las aplicaciones', '00000000-0000-0000-0000-000000000105'::uuid),
    ('00000000-0000-0000-0000-000000000204'::uuid, 1, 'Proporcionar soporte técnico 24/7', '00000000-0000-0000-0000-000000000106'::uuid),
    ('00000000-0000-0000-0000-000000000205'::uuid, 2, 'Realizar mantenimiento preventivo y correctivo', '00000000-0000-0000-0000-000000000106'::uuid),
    ('00000000-0000-0000-0000-000000000206'::uuid, 1, 'Capacitar al personal en nuevas tecnologías', '00000000-0000-0000-0000-000000000109'::uuid),
    ('00000000-0000-0000-0000-000000000207'::uuid, 2, 'Certificar competencias técnicas del equipo', '00000000-0000-0000-0000-000000000109'::uuid),
    ('00000000-0000-0000-0000-000000000208'::uuid, 3, 'Desarrollar material didáctico especializado', '00000000-0000-0000-0000-000000000109'::uuid),
    ('00000000-0000-0000-0000-000000000209'::uuid, 1, 'Realizar auditorías de calidad del software', '00000000-0000-0000-0000-000000000110'::uuid),
    ('00000000-0000-0000-0000-000000000210'::uuid, 2, 'Implementar controles de seguridad informática', '00000000-0000-0000-0000-000000000110'::uuid);

-- =============================
-- 4. EVIDENCIAS POR OBJETIVO
-- =============================
INSERT INTO "SeguimientoDAP".evidencia_contrato (id, indice, descripcion, objetivo_contrato_id, obligacion_id)
VALUES 
    ('00000000-0000-0000-0000-000000000301'::uuid, 1, 'Código fuente de las aplicaciones desarrolladas', '00000000-0000-0000-0000-000000000201'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000302'::uuid, 2, 'Documentación técnica de APIs', '00000000-0000-0000-0000-000000000201'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000303'::uuid, 3, 'Reportes de pruebas de funcionalidad', '00000000-0000-0000-0000-000000000201'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000304'::uuid, 1, 'Diagramas de arquitectura de microservicios', '00000000-0000-0000-0000-000000000202'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000305'::uuid, 2, 'Configuraciones de contenedores Docker', '00000000-0000-0000-0000-000000000202'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000306'::uuid, 1, 'Logs de tickets de soporte', '00000000-0000-0000-0000-000000000204'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000307'::uuid, 2, 'Reportes de tiempo de respuesta', '00000000-0000-0000-0000-000000000204'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000308'::uuid, 1, 'Certificados de capacitación del personal', '00000000-0000-0000-0000-000000000206'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000309'::uuid, 2, 'Evaluaciones de competencias técnicas', '00000000-0000-0000-0000-000000000206'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000310'::uuid, 1, 'Informes de auditoría de calidad', '00000000-0000-0000-0000-000000000209'::uuid, NULL),
    ('00000000-0000-0000-0000-000000000311'::uuid, 2, 'Planes de mejora continua', '00000000-0000-0000-0000-000000000209'::uuid, NULL);

-- =============================
-- 5. PERFIL DEL CONTRATISTA
-- =============================
INSERT INTO "SeguimientoDAP".perfil_contratista (id, nombre_completo, documento_identidad, id_usuario_bonita, estado)
VALUES 
    ('00000000-0000-0000-0000-000000005001'::uuid, 'Juan Carlos Pérez López', '1234567890', '5001', 1);

-- =============================
-- 6. CONTRATO ESPECÍFICO DEL CONTRATISTA
-- =============================
INSERT INTO "SeguimientoDAP".contrato (
    id,
    numero_contrato,
    fecha_inicio,
    estado,
    plazo,
    objeto,
    valor_contrato,
    supervisor,
    perfil_contratista_id,
    padre_id
) VALUES (
    '00000000-0000-0000-0000-000000004001'::uuid,
    'CONT-2024-0015',
    '2024-10-01'::date,
    'Activo',
    '12 meses',
    'Prestación de servicios de desarrollo de aplicaciones web para la entidad contratante',
    150000000.00,
    1002,
    '00000000-0000-0000-0000-000000005001'::uuid,
    '00000000-0000-0000-0000-000000000002'::uuid
);

-- =============================
-- 7. OBLIGACIONES DEL CONTRATO
-- =============================
INSERT INTO "SeguimientoDAP".obligacion (id, indice, descripcion, contrato_id)
VALUES 
    ('00000000-0000-0000-0000-000000000401'::uuid, 1, 'Entregar informes mensuales de avance', '00000000-0000-0000-0000-000000004001'::uuid),
    ('00000000-0000-0000-0000-000000000402'::uuid, 2, 'Asistir a reuniones de seguimiento semanales', '00000000-0000-0000-0000-000000004001'::uuid),
    ('00000000-0000-0000-0000-000000000403'::uuid, 3, 'Cumplir con los estándares de calidad definidos', '00000000-0000-0000-0000-000000004001'::uuid),
    ('00000000-0000-0000-0000-000000000404'::uuid, 4, 'Mantener confidencialidad de la información', '00000000-0000-0000-0000-000000004001'::uuid);

-- =============================
-- 8. INFORMES DEL CONTRATO
-- =============================
INSERT INTO "SeguimientoDAP".informe (
    id,
    valor_periodo,
    estado,
    mes,
    anio,
    fecha_inicio_periodo,
    fecha_fin_periodo,
    contrato_id
) VALUES 
    (
        '00000000-0000-0000-0000-000000005001'::uuid,
        12500000.00,
        'Aprobado',
        10,
        2024,
        '2024-10-01'::date,
        '2024-10-31'::date,
        '00000000-0000-0000-0000-000000004001'::uuid
    ),
    (
        '00000000-0000-0000-0000-000000005002'::uuid,
        12500000.00,
        'En Revisión',
        11,
        2024,
        '2024-11-01'::date,
        '2024-11-30'::date,
        '00000000-0000-0000-0000-000000004001'::uuid
    );

-- =============================
-- 9. EJECUCIONES DE OBLIGACIONES
-- =============================
INSERT INTO "SeguimientoDAP".ejecucion (
    id,
    evidencia_adjunta,
    obligacion_id,
    informe_id
) VALUES 
    (
        '00000000-0000-0000-0000-000000006001'::uuid,
        'informe_octubre_2024.pdf',
        '00000000-0000-0000-0000-000000000401'::uuid,
        '00000000-0000-0000-0000-000000005001'::uuid
    ),
    (
        '00000000-0000-0000-0000-000000006002'::uuid,
        'actas_reuniones_octubre.pdf',
        '00000000-0000-0000-0000-000000000402'::uuid,
        '00000000-0000-0000-0000-000000005001'::uuid
    ),
    (
        '00000000-0000-0000-0000-000000006003'::uuid,
        'pruebas_calidad_octubre.pdf',
        '00000000-0000-0000-0000-000000000403'::uuid,
        '00000000-0000-0000-0000-000000005001'::uuid
    );

-- =============================
-- 10. DESCRIPCIONES DE LAS EJECUCIONES
-- =============================
INSERT INTO "SeguimientoDAP".descripcion_ejecucion (id, indice, descripcion, ejecucion_id)
VALUES 
    ('00000000-0000-0000-0000-000000007001'::uuid, 1, 'Informe entregado con todas las actividades realizadas en octubre', '00000000-0000-0000-0000-000000006001'::uuid),
    ('00000000-0000-0000-0000-000000007002'::uuid, 1, 'Asistencia a cuatro reuniones de seguimiento durante octubre', '00000000-0000-0000-0000-000000006002'::uuid),
    ('00000000-0000-0000-0000-000000007003'::uuid, 1, 'Entregables cumplen con los estándares ISO 9001', '00000000-0000-0000-0000-000000006003'::uuid);

-- =============================
-- 11. CONSULTAS DE VERIFICACIÓN
-- =============================
-- Contratos inter administrativos
SELECT * FROM "SeguimientoDAP".contrato_inter_administrativo 
WHERE id IN ('00000000-0000-0000-0000-000000000002'::uuid, '00000000-0000-0000-0000-000000000003'::uuid);

-- Componentes asociados a contratos marco
SELECT 
    cia.numero_contrato AS contrato_marco,
    comp.descripcion AS componente,
    comp.indice
FROM "SeguimientoDAP".contrato_inter_administrativo cia
JOIN "SeguimientoDAP".componente comp ON cia.id = comp.contrato_marco_id
WHERE cia.id IN ('00000000-0000-0000-0000-000000000002'::uuid, '00000000-0000-0000-0000-000000000003'::uuid)
ORDER BY cia.id, comp.indice;

-- Objetivos por componente
SELECT 
    comp.descripcion AS componente,
    obj.descripcion AS objetivo,
    obj.indice
FROM "SeguimientoDAP".componente comp
JOIN "SeguimientoDAP".objetivo_contrato obj ON comp.id = obj.componente_id
WHERE comp.id IN (
    '00000000-0000-0000-0000-000000000105'::uuid,
    '00000000-0000-0000-0000-000000000106'::uuid,
    '00000000-0000-0000-0000-000000000109'::uuid,
    '00000000-0000-0000-0000-000000000110'::uuid
)
ORDER BY comp.id, obj.indice;

-- Evidencias por objetivo
SELECT 
    obj.descripcion AS objetivo,
    ev.descripcion AS evidencia,
    ev.indice
FROM "SeguimientoDAP".objetivo_contrato obj
JOIN "SeguimientoDAP".evidencia_contrato ev ON obj.id = ev.objetivo_contrato_id
WHERE obj.id IN (
    '00000000-0000-0000-0000-000000000201'::uuid,
    '00000000-0000-0000-0000-000000000202'::uuid,
    '00000000-0000-0000-0000-000000000204'::uuid,
    '00000000-0000-0000-0000-000000000206'::uuid,
    '00000000-0000-0000-0000-000000000209'::uuid
)
ORDER BY obj.id, ev.indice;

-- Contrato específico con obligaciones e informes
SELECT * FROM "SeguimientoDAP".contrato 
WHERE id = '00000000-0000-0000-0000-000000004001'::uuid;

SELECT 
    c.numero_contrato,
    o.indice,
    o.descripcion
FROM "SeguimientoDAP".contrato c
JOIN "SeguimientoDAP".obligacion o ON c.id = o.contrato_id
WHERE c.id = '00000000-0000-0000-0000-000000004001'::uuid
ORDER BY o.indice;

SELECT 
    c.numero_contrato,
    i.mes,
    i.anio,
    i.estado,
    i.valor_periodo
FROM "SeguimientoDAP".contrato c
JOIN "SeguimientoDAP".informe i ON c.id = i.contrato_id
WHERE c.id = '00000000-0000-0000-0000-000000004001'::uuid
ORDER BY i.anio, i.mes;

-- Ejecuciones por informe
SELECT 
    i.mes,
    i.anio,
    o.descripcion AS obligacion,
    e.evidencia_adjunta
FROM "SeguimientoDAP".informe i
JOIN "SeguimientoDAP".ejecucion e ON i.id = e.informe_id
JOIN "SeguimientoDAP".obligacion o ON e.obligacion_id = o.id
WHERE i.contrato_id = '00000000-0000-0000-0000-000000004001'::uuid
ORDER BY i.anio, i.mes, o.indice;

-- Consulta resumen del contrato
SELECT 
    c.numero_contrato,
    pc.nombre_completo AS contratista,
    c.estado,
    c.valor_contrato,
    cia.numero_contrato AS contrato_marco,
    COUNT(DISTINCT o.id) AS total_obligaciones,
    COUNT(DISTINCT inf.id) AS total_informes
FROM "SeguimientoDAP".contrato c
JOIN "SeguimientoDAP".perfil_contratista pc ON c.perfil_contratista_id = pc.id
JOIN "SeguimientoDAP".contrato_inter_administrativo cia ON c.padre_id = cia.id
LEFT JOIN "SeguimientoDAP".obligacion o ON c.id = o.contrato_id
LEFT JOIN "SeguimientoDAP".informe inf ON c.id = inf.contrato_id
WHERE c.id = '00000000-0000-0000-0000-000000004001'::uuid
GROUP BY c.numero_contrato, pc.nombre_completo, c.estado, c.valor_contrato, cia.numero_contrato;

-- ============================================================================
-- Fin del script
-- ============================================================================

