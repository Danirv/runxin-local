# Runxin Local per a Home Assistant

[English](../README.md) | [Català](README.ca.md) | [Español](README.es.md)

Lectura i control local de descalcificadors amb controladors **Runxin compatibles** i mòdul Wi-Fi **BroadLink BL3372**. Funciona per la LAN sense dependre del núvol del fabricant.

**Comença aquí:** [Instal·lació i actualització](installation.ca.md) · [Models suportats](model-support.md) · [Guia d’ús](usage.ca.md) · [Problemes de connexió](troubleshooting.ca.md) · [Índex complet](index.md)

## Requisits i compatibilitat

Cal **Home Assistant 2026.10.0+**, un BL3372 accessible (`0x520F`) i un controlador compatible. Home Assistant instal·la `broadlink-async>=1.1.0` a l’espai aïllat `broadlink_async`. Amb HA anterior, conserva Runxin Local 2.9.3 i revisa la [migració](ha-2026-10.ca.md) abans d’actualitzar HA.

| Controlador | Maquinari reportat | Suport actual |
|---|---|---|
| 9 / F79D | ATH/BWT Ypsilon G6 | Maquinari de referència |
| 1 / F150, nom de l’API | Equip sense marca de la issue #17 | Lectures Beta i rellotge manual validat; altres controls amb opcions de proves |
| 12 / F105 | Euro-Clear Midnight 25 / ECOPRO+ | Beta; escriptures verificades i pendents diferenciades |
| 14 / F136 | Euro-Clear Midnight 25 / ECOPRO+ | Beta; conversió de resina pròpia confirmada |

La [matriu](model-support.md) concreta permisos, límits i evidència. Alpha/Beta és l’estat de cada model, no el canal de release de la integració. Altres controladors poden generar un [informe de lectura](compatibility-report.md) sense editar fitxers ni preparar Python.

## Instal·lar amb HACS

Runxin Local és al **catàleg de HACS**, acceptat a [hacs/default#10717](https://github.com/hacs/default/pull/10717) el 20 d’octubre de 2026.

1. Obre **HACS**, busca **Runxin Local** i descarrega la integració.
2. Reinicia Home Assistant.
3. Obre **Configuració → Dispositius i serveis → Afegeix integració → Runxin Local** i indica la IP local, o accepta una descoberta compatible.

La [guia d’instal·lació](installation.ca.md) explica actualitzacions, instal·lació manual, entrades de diagnòstic i dependències antigues. Les instal·lacions existents no necessiten eliminar ni reaparellar el dispositiu per l’acceptació a HACS.

## Ús habitual

- Estat, cabal, consum diari, capacitat restant, regeneració i avisos del controlador.
- **Consum diari** com a font d’aigua al panell d’Energia; la mitjana setmanal i capacitat per cicle són magnituds diferents.
- Entitats de diagnòstic per a fases, recordatoris, resina i comunicació.
- Controls segons el model, amb comprovació mitjançant una lectura nova. Un ACK no confirma per si sol el canvi.

**La sal afegida és un ajust del controlador, no un nivell físic. Vacances és només lectura.** Consulta la [guia d’ús](usage.ca.md) per a estadístiques, opcions i serveis avançats. La integració pot moure la vàlvula i no substitueix una protecció independent contra fuites.

## Instal·lacions Ypsilon existents

El projecte abans es deia Ypsilon / ypsilon-local. El domini, carpeta, serveis i identificadors continuen sent **`ypsilon_local`**. Conserva les entrades i automatitzacions. Una futura migració del domini és una feina separada.

<a id="autodiagnòstic-i-canvi-de-nom-280"></a>
<a id="canvi-principal-de-la-263"></a>
<a id="canvis-principals-de-la-261"></a>
<a id="compatibilitat-a-la-292"></a>
<a id="consum-daigua"></a>
<a id="correccions-a-la-293"></a>
<a id="descobriment-automàtic--2103"></a>
<a id="estadístiques-antigues-de-home-assistant"></a>
<a id="euro-clear-midnight--model-12"></a>
<a id="home-assistant-202610-i-transport-asíncron-2101"></a>
<a id="installació"></a>
<a id="models-1-i-12-en-beta--2102"></a>
<a id="problemes-de-connexió"></a>
<a id="seguretat"></a>

## Ajuda i projecte

[Documentació completa](index.md) · [Contribuir](../CONTRIBUTING.ca.md) · [Publicar releases](../PUBLISHING.ca.md) · [Historial](../CHANGELOG.md) · [Seguretat](../SECURITY.ca.md) · [Nota legal](../LEGAL.ca.md) · [Dependències](../THIRD_PARTY.md) · [Llicència](../LICENSE)

Projecte comunitari independent, no afiliat ni avalat per ATH, BWT, Runxin o BroadLink. No distribueix aplicacions del fabricant, firmware ni credencials. El finançament opcional no modifica funcions ni prioritats de suport.
