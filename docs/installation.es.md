# Instalar, configurar y actualizar Runxin Local

[English](installation.md) | [Català](installation.ca.md) | [Español](installation.es.md) · [Documentación](index.md)

## Antes de instalar

Se requiere **Home Assistant 2026.10.0+**, un módulo BL3372 accesible (`0x520F`) y un controlador de la [matriz de soporte](model-support.md). `hacs.json` declara la versión mínima. Home Assistant instala `broadlink-async>=1.1.0`; no instales paquetes manualmente en su entorno gestionado.

Con HA anterior, conserva Runxin Local 2.9.3. Si utilizabas la dependencia BroadLink compartida, consulta la [migración y recuperación](ha-2026-10.es.md).

## Instalación con HACS

Runxin Local forma parte del [catálogo de HACS](https://github.com/hacs/default/pull/10717).

1. Con [HACS configurado](https://www.hacs.dev/docs/use/), abre HACS y busca **Runxin Local**.
2. Abre el repositorio y descarga la integración.
3. Reinicia Home Assistant.
4. Continúa con el alta del dispositivo. Descargar los archivos no configura el descalcificador.

Una incorporación al catálogo puede tardar hasta ocho horas en aparecer. El proyecto se aceptó el 20 de octubre de 2026; si todavía no aparece, espera la actualización de metadatos de HACS. Las instalaciones anteriores como repositorio personalizado pueden seguir actualizando el mismo repositorio sin reinstalar el dispositivo.

## Instalación manual

1. Descarga el ZIP de la integración de una [release publicada](https://github.com/Danirv/runxin-local/releases).
2. Guarda una copia de la carpeta `custom_components/ypsilon_local` existente antes de reemplazarla.
3. Coloca la carpeta **`custom_components/ypsilon_local`** del ZIP en **`/config/custom_components/ypsilon_local`**. Evita otra carpeta `custom_components` anidada y no la renombres a `runxin_local`.
4. Reinicia Home Assistant y continúa con el alta.

## Alta del dispositivo

Abre **Ajustes → Dispositivos y servicios → Añadir integración → Runxin Local**, introduce la IP local y sigue el formulario. HA debe poder acceder al dispositivo por la LAN. Una reserva DHCP ayuda a mantener su dirección.

El descubrimiento usa prefijos MAC BroadLink como pistas y después comprueba el tipo de módulo y el controlador. Otros tipos BroadLink se descartan antes de autenticar; un BL3372 con problemas de conexión o un modelo Runxin desconocido puede ofrecer diagnóstico. El prefijo MAC no demuestra compatibilidad.

El modelo 1 muestra una explicación de sus lecturas Beta, unidades pendientes y reloj manual. Por defecto consulta cada minuto, con sondeo adaptativo y corrección automática del reloj desactivados. [Guía del modelo 1](models/model-1.es.md).

Si guardaste una **entrada solo de diagnóstico**, descarga su informe y elimina esa entrada antes de añadir el mismo dispositivo normalmente. No tiene entidades operativas ni se convierte automáticamente.

## Actualizar una instalación existente

Actualiza con HACS o reemplaza los archivos de la instalación manual y reinicia HA. Conserva entradas operativas, entidades y automatizaciones. El cambio de nombre y la aceptación en HACS no requieren volver a emparejar ni eliminar la integración.

El dominio, carpeta y prefijo de servicios siguen siendo **`ypsilon_local`**. Una futura migración es un trabajo separado. Para cambiar la IP de un equipo configurado, usa **Reconfigurar** en lugar de crear una entrada duplicada.

Actualizar a la dependencia aislada no requiere por sí solo reconstruir Core. Los casos con BroadLink ya dañado en HA 2026.10.0/1 tienen un [procedimiento específico](ha-2026-10.es.md).

## Después del alta

Consulta la [política por modelo](model-support.md) y la [guía de uso](usage.es.md). Si falla el alta, usa la [resolución de problemas](troubleshooting.es.md) o el [informe de lectura](compatibility-report.md); no hace falta editar el registro de modelos para obtener un informe.
