# plugin.video.sosac.ph

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d6eb929d7cbb4c2681bffa6a43dcd9e3)](https://www.codacy.com/app/zbyna/plugin-video-sosac-ph?utm_source=github.com&utm_medium=referral&utm_content=zbyna/plugin.video.sosac.ph&utm_campaign=badger)
[![Code Climate](https://codeclimate.com/github/zbyna/plugin.video.sosac.ph/badges/gpa.svg)](https://codeclimate.com/github/zbyna/plugin.video.sosac.ph)

[![Issue Count](https://codeclimate.com/github/zbyna/plugin.video.sosac.ph/badges/issue_count.svg)](https://codeclimate.com/github/zbyna/plugin.video.sosac.ph)

[![Code Health](https://landscape.io/github/zbyna/plugin.video.sosac.ph/master/landscape.svg?style=flat)](https://landscape.io/github/zbyna/plugin.video.sosac.ph/master)

This version is based on version 1.2.11 https://github.com/kodi-czsk/plugin.video.sosac.ph (fork)

Thanks to the authors.

For the plugin to function properly, needs to be installed **current version of stream.resolver** from https://github.com/zbyna/script.module.stream.resolver/releases

# Extensions and edits:

![](http://i.imgur.com/f0VVTHB.png)
- when **playing from the media library** adds:
  1. support for **viewed status automatic setting**
     at 90% play of the item
  2. **osd menu with poster** (movies), **preview** (serials), **storyline
     and occupation** requires stream.resolver min 1.6.435 and skin support
     
- added **automatic resume playback when re-running video from media library**.
  The restore point is created only when a minimum of 5 and max 90% of the video is played.
  When you re-play the video, you can choose whether to resume playback or play from the beginning.
  After selecting one of the options, the restore point is deleted.
  
- Added **Simple Subscription Manager for TV Series**

- Added item **"Movies by Year"**

- Added **"csfd Rankings"** (Best Movies, Best TV Series, Overall
  and by genre)
  
- Added **"Awards from csfd"** (Oscars, Golden Palm)

- added context menu **"Add All To Library"** for **Genre** in "Movies by Genre" a
  **year** in "Movies by Year"
  
- added context menu **"Sign up for subscription"** for items in Subscription Manager a
  **"Log out all subscriptions"** for the root item "Subscription Manager"
  
- option **not to subscribe when adding all** series to the library

- Added the dubbing info to the movie or series name

- Added stream info - video, audio, subtitles
  - required skin icon support (tested by AEON MQ.7) and stream resolver at least 2.0

 ![](http://i.imgur.com/hO4Xg3k.jpg)

- Added user scans feature:
  - **Settings / Library service / Check subscriptions**
  
  - **Context Menu / Subscription Manager / Check subscriptions**

- added **memory cache implementation** for time and demanding operations

- Added **Multithread implementation** IO operations

- Added add-on settings
    - **Tab General - to force English names**,
      1. **Sort by - czech, english, os**
          - if there is no selected location in the operating system, the default is selected,
this is a problem, for example, in LibreElec or OpenElec, where the cs_CZ.utf8 location is not available, but it comes to better times: https://forum.libreelec.tv/thread-7356.html
          - according to the standard, the Czech sorting is first alphabetical up to the letters, for me the surprise 🙂, windows it does not solve it at all, but in Linux if localization is installed, everything works according to the standard

      2. **Show 'CH' in Movies & Serials**
          - Plays them in the Movies & Serial list
        
    - **Tab Cache - Flush Cache**,
    
    - **Tab Library service - subscription and addition to the library**
      - to set the options for simultaneous execution of these items
                              
- Added option **to download to SMB sources**, requires stream.resolver min. 1.6.447

- added **translations of previously unlisted addon items** - into English, Slovak, Czech

- added **Buggalo** add-on support for optional error message sending, after user reconciliation, to sosac.comli.com
- added option **setting the plugin library to any source directly from Kodi**,
  (after restoring the default values ​​(special: // ...) you need to restart the sock)
  
- fixed **download files with subtitles**, requires stream.resolver min. 1.6.435

- Fixed **Retrieving subtitles when playing from media library** on slower internet
  connection, requires stream.resolver min. 1.6.447

- fixed WARNING: XFILE :: CFileFactory :: CreateLoader -, requires stream.resolver min 1.6.435

- Fixed subtitles for Krypton when playing outside the Kodi media library
  (requires stream resolver at least 1.6.448)
