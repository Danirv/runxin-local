# Instal·lar, configurar i actualitzar Runxin Local

[English](installation.md) | [Català](installation.ca.md) | [Español](installation.es.md) · [Documentació](index.md)

## Abans d’instal·lar

Cal **Home Assistant 2026.10.0+**, un mòdul BL3372 accessible (`0x520F`) i un controlador de la [matriu de suport](model-support.md). `hacs.json` declara la versió mínima. Home Assistant instal·la `broadlink-async>=1.1.0`; no instal·lis paquets manualment al seu entorn gestionat.

Amb HA anterior, conserva Runxin Local 2.9.3. Si havies utilitzat la dependència BroadLink compartida, consulta la [migració i recuperació](ha-2026-10.ca.md).

## Instal·lació amb HACS

Runxin Local forma part del [catàleg de HACS](https://github.com/hacs/default/pull/10717).

1. Amb [HACS configurat](https://www.hacs.dev/docs/use/), obre HACS i busca **Runxin Local**.
2. Obre el repositori i descarrega la integració.
3. Reinicia Home Assistant.
4. Continua amb l’alta del dispositiu. Descarregar els fitxers no configura el descalcificador.

Una incorporació al catàleg pot trigar fins a vuit hores a aparèixer. El projecte es va acceptar el 20 d’octubre de 2026; si encara no apareix, espera l’actualització de metadades de HACS. Les instal·lacions anteriors com a repositori personalitzat poden continuar actualitzant el mateix repositori sense reinstal·lar el dispositiu.

## Instal·lació manual

1. Descarrega el ZIP de la integració d’una [release publicada](https://github.com/Danirv/runxin-local/releases).
2. Desa una còpia de la carpeta `custom_components/ypsilon_local` existent abans de substituir-la.
3. Col·loca la carpeta **`custom_components/ypsilon_local`** del ZIP a **`/config/custom_components/ypsilon_local`**. Evita una carpeta `custom_components` duplicada i no la canviïs per `runxin_local`.
4. Reinicia Home Assistant i continua amb l’alta.

## Alta del dispositiu

Obre **Configuració → Dispositius i serveis → Afegeix integració → Runxin Local**, indica la IP local i segueix el formulari. HA ha de poder accedir al dispositiu per la LAN. Una reserva DHCP ajuda a mantenir-ne l’adreça.

La descoberta utilitza prefixos MAC BroadLink com a pistes i després comprova el tipus de mòdul i el controlador. Altres tipus BroadLink es descarten abans d’autenticar; un BL3372 amb problemes de connexió o un model Runxin desconegut pot oferir diagnòstic. El prefix MAC no demostra compatibilitat.

El model 1 mostra una explicació de les lectures Beta, unitats pendents i rellotge manual. Per defecte consulta cada minut, amb sondeig adaptatiu i correcció automàtica del rellotge desactivats. [Guia del model 1](models/model-1.ca.md).

Si havies desat una **entrada només de diagnòstic**, descarrega’n l’informe i elimina aquella entrada abans d’afegir el mateix dispositiu normalment. No té entitats operatives ni es converteix automàticament.

## Actualitzar una instal·lació existent

Actualitza amb HACS o substitueix els fitxers de la instal·lació manual i reinicia HA. Conserva entrades operatives, entitats i automatitzacions. El canvi de nom i l’acceptació a HACS no requereixen reaparellar ni eliminar la integració.

El domini, carpeta i prefix de serveis continuen sent **`ypsilon_local`**. Una migració futura és una feina separada. Per canviar la IP d’un equip configurat, utilitza **Reconfigura** en lloc de crear una entrada duplicada.

Actualitzar a la dependència aïllada no requereix per si sol reconstruir Core. Els casos amb BroadLink ja malmès a HA 2026.10.0/1 tenen un [procediment específic](ha-2026-10.ca.md).

## Després de l’alta

Consulta la [política per model](model-support.md) i la [guia d’ús](usage.ca.md). Si falla l’alta, utilitza la [resolució de problemes](troubleshooting.ca.md) o l’[informe de lectura](compatibility-report.md); no cal editar el registre de models per obtenir un informe.
