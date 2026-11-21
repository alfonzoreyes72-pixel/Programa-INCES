-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-11-2026 a las 04:22:23
-- Versión del servidor: 10.11.16-MariaDB
-- Versión de PHP: 8.3.36

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `inces`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asistencias`
--

CREATE TABLE `asistencias` (
  `id_asistencia` int(11) NOT NULL,
  `cedula_trabajador_fk` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `hora_entrada` time NOT NULL,
  `hora_salida` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `centros_votacion`
--

CREATE TABLE `centros_votacion` (
  `id_centro_votacion` int(11) NOT NULL,
  `nombre_centro` varchar(100) NOT NULL,
  `direccion_centro` varchar(255) NOT NULL,
  `id_parroquia_fk` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `centros_votacion`
--

INSERT INTO `centros_votacion` (`id_centro_votacion`, `nombre_centro`, `direccion_centro`, `id_parroquia_fk`) VALUES
(2, 'Liceo Miguel José Sanz', 'Avenida Bolívar , diagonal a la Redoma Juana Ramírez \"La Avanzadora\" y al lado de la Casa de la Cultura, en el centro de Maturín', 1),
(3, 'Escuela Técnica \"Eloy Palacios Cabello\"', 'Calle Bermúdez, entre Calles 9 y 10. Cerca del Museo Mateo Manaure, laPlaza Bolívar de Maturín y la Iglesia San Simón. En el centro de Maturín', 1),
(4, 'upt ludovico', 'bello monte', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentos`
--

CREATE TABLE `departamentos` (
  `id_departamento` int(11) NOT NULL,
  `nombre_departamento` varchar(100) NOT NULL,
  `ubicacion_fisica` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `departamentos`
--

INSERT INTO `departamentos` (`id_departamento`, `nombre_departamento`, `ubicacion_fisica`) VALUES
(3, 'Recursos Humanos', 'al lado de la biblioteca '),
(4, 'Tutor de Formaciones', '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estados`
--

CREATE TABLE `estados` (
  `id_estado` int(11) NOT NULL,
  `nombre_estado` varchar(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estados`
--

INSERT INTO `estados` (`id_estado`, `nombre_estado`) VALUES
(2, 'Monagas'),
(3, 'Sucre');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estados_laborales`
--

CREATE TABLE `estados_laborales` (
  `id_estado_laboral` int(11) NOT NULL,
  `descripcion_estado` varchar(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estados_laborales`
--

INSERT INTO `estados_laborales` (`id_estado_laboral`, `descripcion_estado`) VALUES
(2, 'Trabajador fijo'),
(3, 'Retirado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `incidencias`
--

CREATE TABLE `incidencias` (
  `id_incidencia` int(11) NOT NULL,
  `tipo_incidencia` varchar(100) NOT NULL,
  `color` varchar(20) NOT NULL DEFAULT 'gris'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `incidencias`
--

INSERT INTO `incidencias` (`id_incidencia`, `tipo_incidencia`, `color`) VALUES
(1, 'Reposo médico', 'rojo'),
(2, 'Vacaciones', 'verde'),
(3, 'Permiso', 'ambar'),
(4, 'Comisión de servicio', 'morado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `municipios`
--

CREATE TABLE `municipios` (
  `id_municipio` int(11) NOT NULL,
  `nombre_municipio` varchar(60) NOT NULL,
  `id_estado_fk` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `municipios`
--

INSERT INTO `municipios` (`id_municipio`, `nombre_municipio`, `id_estado_fk`) VALUES
(5, 'Maturin', 2),
(6, 'caripito', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `novedades_operativas`
--

CREATE TABLE `novedades_operativas` (
  `id_novedad` int(11) NOT NULL,
  `cedula_trabajador_fk` int(11) NOT NULL,
  `id_incidencia_fk` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date DEFAULT NULL,
  `justificacion` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `novedades_operativas`
--

INSERT INTO `novedades_operativas` (`id_novedad`, `cedula_trabajador_fk`, `id_incidencia_fk`, `fecha_inicio`, `fecha_fin`, `justificacion`) VALUES
(1, 31776780, 2, '2026-11-20', '2026-11-27', 'el gotdito se tomo unas vacaciones para seguir comiendo'),
(2, 32270636, 1, '2026-11-20', NULL, 'esta mal mal'),
(3, 32753323, 3, '2026-11-20', NULL, 'el pana esta de permiso ps');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `parroquias`
--

CREATE TABLE `parroquias` (
  `id_parroquia` int(11) NOT NULL,
  `nombre_parroquia` varchar(100) NOT NULL,
  `id_municipio_fk` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `parroquias`
--

INSERT INTO `parroquias` (`id_parroquia`, `nombre_parroquia`, `id_municipio_fk`) VALUES
(1, 'San Simon', 5),
(2, 'Bello monte', 6);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `privilegios_ventanas`
--

CREATE TABLE `privilegios_ventanas` (
  `id_usuario_fk` int(11) NOT NULL,
  `ventana` varchar(40) NOT NULL,
  `permitido` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `privilegios_ventanas`
--

INSERT INTO `privilegios_ventanas` (`id_usuario_fk`, `ventana`, `permitido`) VALUES
(2, 'asistencias', 0),
(2, 'operativas', 1),
(2, 'reportes', 1),
(2, 'trabajadores', 1),
(2, 'usuarios', 0),
(2, 'votacion', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL,
  `nombre_rol` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id_rol`, `nombre_rol`) VALUES
(1, 'Administrador'),
(2, 'Recursos Humanos'),
(3, 'Secretario/a');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `trabajadores`
--

CREATE TABLE `trabajadores` (
  `cedula_trabajador` int(11) NOT NULL,
  `nombres` varchar(60) NOT NULL,
  `apellidos` varchar(60) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `telefono` varchar(20) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `sexo` varchar(10) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `id_departamento_fk` int(11) NOT NULL,
  `id_estado_laboral_fk` int(11) NOT NULL,
  `id_centro_votacion_fk` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `trabajadores`
--

INSERT INTO `trabajadores` (`cedula_trabajador`, `nombres`, `apellidos`, `fecha_nacimiento`, `telefono`, `correo`, `sexo`, `direccion`, `id_departamento_fk`, `id_estado_laboral_fk`, `id_centro_votacion_fk`) VALUES
(123, 'doris', 'farias5', '1999-12-30', '04264840997', 'dorisisidra8@gmail.com', 'Femenino', 'fr', 3, 3, 4),
(12345678, 'juan', 'andres', '1900-01-02', '123-12345', 'juansito@gmail.com', 'Masculino', 'por ahi', 4, 2, 2),
(31776780, 'Ángel', 'Malavé', '2006-11-18', '0412-1234567', 'angel@gmail.com', 'Masculino', 'las Cocuizas', 4, 2, 2),
(32270636, 'Rolando Alfonzo', 'Reyes Perez', '2006-11-18', '04128335530', 'alfonzoreyes72@gmail.com', 'Masculino', 'Invasión de la Puente, Calle 10', 4, 2, 3),
(32753323, 'Jesús', 'López', '2006-11-18', '0412-1234567', 'jesus@gmail.com', 'Masculino', 'El Elevado de Maturín', 3, 2, 2),
(338614649, 'YUSLEN ANTONELA', 'FACURE PEREZ', '2010-10-10', '04128614649', '', 'Femenino', 'la libertad', 4, 3, 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre_usuario` varchar(20) NOT NULL,
  `contraseña` varchar(60) NOT NULL,
  `cedula_trabajador_fk` int(11) NOT NULL,
  `id_rol_fk` int(11) NOT NULL,
  `ultimo_acceso` datetime DEFAULT NULL,
  `bloqueado` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `nombre_usuario`, `contraseña`, `cedula_trabajador_fk`, `id_rol_fk`, `ultimo_acceso`, `bloqueado`) VALUES
(1, 'Rolando', '1234', 32270636, 1, '2026-11-19 11:17:39', 0),
(2, 'Jesus', '1234', 32753323, 2, '2026-11-19 11:16:13', 0),
(3, 'Angel', '1234', 31776780, 3, '2026-11-19 11:16:40', 0);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `asistencias`
--
ALTER TABLE `asistencias`
  ADD PRIMARY KEY (`id_asistencia`),
  ADD KEY `cedula_trabajador_fk` (`cedula_trabajador_fk`);

--
-- Indices de la tabla `centros_votacion`
--
ALTER TABLE `centros_votacion`
  ADD PRIMARY KEY (`id_centro_votacion`),
  ADD KEY `id_parroquia_fk` (`id_parroquia_fk`);

--
-- Indices de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  ADD PRIMARY KEY (`id_departamento`);

--
-- Indices de la tabla `estados`
--
ALTER TABLE `estados`
  ADD PRIMARY KEY (`id_estado`);

--
-- Indices de la tabla `estados_laborales`
--
ALTER TABLE `estados_laborales`
  ADD PRIMARY KEY (`id_estado_laboral`);

--
-- Indices de la tabla `incidencias`
--
ALTER TABLE `incidencias`
  ADD PRIMARY KEY (`id_incidencia`);

--
-- Indices de la tabla `municipios`
--
ALTER TABLE `municipios`
  ADD PRIMARY KEY (`id_municipio`),
  ADD KEY `id_estado_fk` (`id_estado_fk`);

--
-- Indices de la tabla `novedades_operativas`
--
ALTER TABLE `novedades_operativas`
  ADD PRIMARY KEY (`id_novedad`),
  ADD KEY `cedula_trabajador_fk` (`cedula_trabajador_fk`),
  ADD KEY `id_incidencia_fk` (`id_incidencia_fk`);

--
-- Indices de la tabla `parroquias`
--
ALTER TABLE `parroquias`
  ADD PRIMARY KEY (`id_parroquia`),
  ADD KEY `id_municipio_fk` (`id_municipio_fk`);

--
-- Indices de la tabla `privilegios_ventanas`
--
ALTER TABLE `privilegios_ventanas`
  ADD PRIMARY KEY (`id_usuario_fk`,`ventana`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_rol`);

--
-- Indices de la tabla `trabajadores`
--
ALTER TABLE `trabajadores`
  ADD PRIMARY KEY (`cedula_trabajador`),
  ADD KEY `id_estado_laboral_fk` (`id_estado_laboral_fk`),
  ADD KEY `id_departamento_fk` (`id_departamento_fk`),
  ADD KEY `id_centro_votacion_fk` (`id_centro_votacion_fk`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD KEY `cedula_trabajador_fk` (`cedula_trabajador_fk`),
  ADD KEY `id_rol_fk` (`id_rol_fk`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `asistencias`
--
ALTER TABLE `asistencias`
  MODIFY `id_asistencia` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `centros_votacion`
--
ALTER TABLE `centros_votacion`
  MODIFY `id_centro_votacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  MODIFY `id_departamento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `estados`
--
ALTER TABLE `estados`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `estados_laborales`
--
ALTER TABLE `estados_laborales`
  MODIFY `id_estado_laboral` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `incidencias`
--
ALTER TABLE `incidencias`
  MODIFY `id_incidencia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `municipios`
--
ALTER TABLE `municipios`
  MODIFY `id_municipio` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `novedades_operativas`
--
ALTER TABLE `novedades_operativas`
  MODIFY `id_novedad` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `parroquias`
--
ALTER TABLE `parroquias`
  MODIFY `id_parroquia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `asistencias`
--
ALTER TABLE `asistencias`
  ADD CONSTRAINT `asistencias_ibfk_1` FOREIGN KEY (`cedula_trabajador_fk`) REFERENCES `trabajadores` (`cedula_trabajador`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `centros_votacion`
--
ALTER TABLE `centros_votacion`
  ADD CONSTRAINT `centros_votacion_ibfk_1` FOREIGN KEY (`id_parroquia_fk`) REFERENCES `parroquias` (`id_parroquia`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `municipios`
--
ALTER TABLE `municipios`
  ADD CONSTRAINT `municipios_ibfk_1` FOREIGN KEY (`id_estado_fk`) REFERENCES `estados` (`id_estado`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `novedades_operativas`
--
ALTER TABLE `novedades_operativas`
  ADD CONSTRAINT `novedades_operativas_ibfk_1` FOREIGN KEY (`id_incidencia_fk`) REFERENCES `incidencias` (`id_incidencia`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `novedades_operativas_ibfk_2` FOREIGN KEY (`cedula_trabajador_fk`) REFERENCES `trabajadores` (`cedula_trabajador`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `parroquias`
--
ALTER TABLE `parroquias`
  ADD CONSTRAINT `parroquias_ibfk_1` FOREIGN KEY (`id_municipio_fk`) REFERENCES `municipios` (`id_municipio`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `privilegios_ventanas`
--
ALTER TABLE `privilegios_ventanas`
  ADD CONSTRAINT `privilegios_ventanas_ibfk_1` FOREIGN KEY (`id_usuario_fk`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `trabajadores`
--
ALTER TABLE `trabajadores`
  ADD CONSTRAINT `trabajadores_ibfk_1` FOREIGN KEY (`id_estado_laboral_fk`) REFERENCES `estados_laborales` (`id_estado_laboral`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `trabajadores_ibfk_2` FOREIGN KEY (`id_departamento_fk`) REFERENCES `departamentos` (`id_departamento`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `trabajadores_ibfk_3` FOREIGN KEY (`id_centro_votacion_fk`) REFERENCES `centros_votacion` (`id_centro_votacion`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`id_rol_fk`) REFERENCES `roles` (`id_rol`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`cedula_trabajador_fk`) REFERENCES `trabajadores` (`cedula_trabajador`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
