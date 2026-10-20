# Runxin Local para Home Assistant

[English](../README.md) | [Català](README.ca.md) | [Español](README.es.md)

Lectura y control local de descalcificadores con controladores **Runxin compatibles** y módulo Wi-Fi **BroadLink BL3372**. Funciona por la LAN sin depender de la nube del fabricante.

**Empieza aquí:** [Instalación y actualización](installation.es.md) · [Modelos soportados](model-support.md) · [Guía de uso](usage.es.md) · [Problemas de conexión](troubleshooting.es.md) · [Índice completo](index.md)

## Requisitos y compatibilidad

Se requiere **Home Assistant 2026.10.0+**, un BL3372 accesible (`0x520F`) y un controlador compatible. Home Assistant instala `broadlink-async>=1.1.0` en el espacio aislado `broadlink_async`. Con HA anterior, conserva Runxin Local 2.9.3 y revisa la [migración](ha-2026-10.es.md) antes de actualizar HA.

| Controlador | Hardware reportado | Soporte actual |
|---|---|---|
| 9 / F79D | ATH/BWT Ypsilon G6 | Hardware de referencia |
| 1 / F150, nombre de la API | Equipo sin marca de la issue #17 | Lecturas Beta y reloj manual validado; otros controles con opciones de pruebas |
| 12 / F105 | Euro-Clear Midnight 25 / ECOPRO+ | Beta; escrituras verificadas y pendientes diferenciadas |
| 14 / F136 | Euro-Clear Midnight 25 / ECOPRO+ | Beta; conversión de resina propia confirmada |

La [matriz](model-support.md) concreta permisos, límites y evidencia. Alpha/Beta es el estado de cada modelo, no el canal de release de la integración. Otros controladores pueden generar un [informe de lectura](compatibility-report.md) sin editar archivos ni preparar Python.

## Instalar con HACS

Runxin Local está en el **catálogo de HACS**, aceptado en [hacs/default#10717](https://github.com/hacs/default/pull/10717) el 20 de octubre de 2026.

1. Abre **HACS**, busca **Runxin Local** y descarga la integración.
2. Reinicia Home Assistant.
3. Abre **Ajustes → Dispositivos y servicios → Añadir integración → Runxin Local** e introduce la IP local, o acepta un descubrimiento compatible.

La [guía de instalación](installation.es.md) explica actualizaciones, instalación manual, entradas de diagnóstico y dependencias antiguas. Las instalaciones existentes no necesitan eliminar ni volver a emparejar el dispositivo por la aceptación en HACS.

## Uso habitual

- Estado, caudal, consumo diario, capacidad restante, regeneración y avisos del controlador.
- **Consumo diario** como fuente de agua en el panel de Energía; la media semanal y capacidad por ciclo son magnitudes distintas.
- Entidades de diagnóstico para fases, recordatorios, resina y comunicación.
- Controles según el modelo, con comprobación mediante una lectura nueva. Un ACK no confirma por sí solo el cambio.

**La sal añadida es un ajuste del controlador, no un nivel físico. Vacaciones es solo lectura.** Consulta la [guía de uso](usage.es.md) para estadísticas, opciones y servicios avanzados. La integración puede mover la válvula y no sustituye una protección independiente contra fugas.

## Instalaciones Ypsilon existentes

El proyecto antes se llamaba Ypsilon / ypsilon-local. El dominio, carpeta, servicios e identificadores siguen siendo **`ypsilon_local`**. Conserva las entradas y automatizaciones. Una futura migración del dominio es un trabajo separado.

<a id="autodiagnóstico-y-cambio-de-nombre-280"></a>
<a id="cambio-principal-de-la-263"></a>
<a id="cambios-principales-de-la-261"></a>
<a id="compatibilidad-en-292"></a>
<a id="consumo-de-agua"></a>
<a id="correcciones-en-293"></a>
<a id="descubrimiento-automático--2103"></a>
<a id="estadísticas-antiguas-de-home-assistant"></a>
<a id="euro-clear-midnight--modelo-12"></a>
<a id="home-assistant-202610-y-transporte-asíncrono-2101"></a>
<a id="instalación"></a>
<a id="modelos-1-y-12-en-beta--2102"></a>
<a id="problemas-de-conexión"></a>
<a id="seguridad"></a>

## Ayuda y proyecto

[Documentación completa](index.md) · [Contribuir](../CONTRIBUTING.es.md) · [Publicar releases](../PUBLISHING.es.md) · [Historial](../CHANGELOG.md) · [Seguridad](../SECURITY.es.md) · [Nota legal](../LEGAL.es.md) · [Dependencias](../THIRD_PARTY.md) · [Licencia](../LICENSE)

Proyecto comunitario independiente, no afiliado ni avalado por ATH, BWT, Runxin o BroadLink. No distribuye aplicaciones del fabricante, firmware ni credenciales. La financiación opcional no modifica funciones ni prioridades de soporte.
