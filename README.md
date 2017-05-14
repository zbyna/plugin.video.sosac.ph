# plugin.video.sosac.ph

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d6eb929d7cbb4c2681bffa6a43dcd9e3)](https://www.codacy.com/app/zbyna/plugin-video-sosac-ph?utm_source=github.com&utm_medium=referral&utm_content=zbyna/plugin.video.sosac.ph&utm_campaign=badger)
[![Code Climate](https://codeclimate.com/github/zbyna/plugin.video.sosac.ph/badges/gpa.svg)](https://codeclimate.com/github/zbyna/plugin.video.sosac.ph)

[![Issue Count](https://codeclimate.com/github/zbyna/plugin.video.sosac.ph/badges/issue_count.svg)](https://codeclimate.com/github/zbyna/plugin.video.sosac.ph)

[![Code Health](https://landscape.io/github/zbyna/plugin.video.sosac.ph/master/landscape.svg?style=flat)](https://landscape.io/github/zbyna/plugin.video.sosac.ph/master)

Tato verze je založena na verzi 1.2.11 https://github.com/kodi-czsk/plugin.video.sosac.ph (fork)

Děkuji autorům.

Pro správnou funkci doplňku je třeba **nejprve** nainstalovat také **aktuální verzi stream.resolveru** z https://github.com/zbyna/script.module.stream.resolver/releases

# Rozšíření a úpravy:

![](http://i.imgur.com/f0VVTHB.png)
- při **přehrávání z media library** přidává:
  1. podporu pro **automatické nastavení statusu zhlédnuto** 
     při min 90 % přehrání položky  
  2. **osd menu s posterem** (filmy), **náhledem** (seriály), **dějem
     a obsazením**, vyžaduje stream.resolver min 1.6.435 a podporu skinu 
     
- přidáno **automatické obnovení přehrávání při opětovném spuštění videa z media library**.  
  Bod obnovení se vytvoří pouze když je přehráno minimálně 5 a max 90 % videa.
  Při znovu přehrání videa je na výběr zda obnovit přehrávání nebo přehrát od začátků.
  Po vybrání jedné z voleb se bod obnovení vymaže.  
  
- přidán **jednoduchý manažer odběru pro seriály** 

- přidána položka **"Filmy dle roku"**

- přidáno **"Žebříčky csfd"** (nejlepší filmy, nejlepší seriály, celkově
  a podle žánru) 
  
- přidáno **"Ocenění z csfd"** (Oskary, Zlatá palma) 

- přidáno kont. menu **"Přidej vše do knihovny"** pro **žánr** ve "Filmy podle žánrů" a 
  **rok** ve "Filmy podle roku" 
  
- přidáno kont. menu **"Přihlas k odběru"** pro položky ve správci odběrů a 
  **"Odhlásit všechny odběry"** pro root položku "Správce odběrů" 
  
- možnost **nepřihlašovat k odběru při přidání všech** seriálů do knihovny

- přidáno info o dabingu do názvu filmu či seriálů 

- přidáno  stream info - video, audio,titulky 
  - nutná podpora ikonek ve skinu (vyzkoušen AEON MQ.7)  a stream resolver alespoň 2.0

 ![](http://i.imgur.com/hO4Xg3k.jpg)

- přidána možnost uživatelského scanu odběrů:
  - **Nastavení/Služba knihovny/Zkontroluj odběry**
  
  - **kontextové menu Správce odběru/Zkontroluj odběry** 

- pridáno **implementace memory cache** pro časově a početně náročné operace 

- přidáno **implementace multithread** zpracování u IO operací

- přidáno nastavení doplňku 
    - **karta Obecné - vynutit anglické názvy**,
      1. **Třídit podle - czech, english, os**
          - pokud v operačním systému neexistuje zvolená lokalizace tak se vybere defaultní, 
je to problém třeba v LibreElec nebo OpenElec, kde skutečně lokalizace cs_CZ.utf8 není k dispozici, ale blíská se na lepší časy:  https://forum.libreelec.tv/thread-7356.html
          - podle normy je české třídění nejprve abeceda až po ní písmena, pro mě překvapení 🙂 , windows to vůbec neřeší, ale v Linuxu pokud teda je lokalizace nainstalovaná, vše funguje podle normy

      2. **Zobrazit 'CH' ve Filmy a Seriály**
		    - zařadí 'ch' do seznamu Filmy a Seriály
        
    - **karta Cache - vyprádnit cache**, 
    
    - **karta Služba knihovny - odběr a přidání do knihovny**
      - pro nastavení možnosti současného provedení těchto položek 
                              
- přidána možnost **stahování na SMB zdroje**, vyžaduje  stream.resolver min. 1.6.447 

- přídán **překlad dosud nelokalizovaných položek addonu** - do angličtiny, slovenštiny, češtiny

- přidána **podpora addonu Buggalo** pro volitelné odeslání chybového hlášení, po odsouhlasení uživatelem, na web:     sosac.comli.com 
- přidána možnost **nastavení knihovny sosáče na libovolný zdroj přímo z Kodi**,
  (po obnovení defaultních hodnot (special:// ...) je  třeba restartovat sosáč)
  
- opraven **download souborů s titulky**, vyžaduje stream.resolver min. 1.6.435 

- opraveno **získávání titulků při přehrávání z media library** na pomalejším internetovém
  připojení, vyžaduje stream.resolver min. 1.6.447 

- opraveno WARNING: XFILE::CFileFactory::CreateLoader -,  vyžaduje stream.resolver min 1.6.435  

- opraveno načítání titulků pro Krypton při přehrávání mimo Kodi media library  
  (vyžaduje stream resolver min. 1.6.448)

  
