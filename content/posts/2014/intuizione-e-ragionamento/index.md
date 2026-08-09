---
title: Intuizione E Ragionamento
date: '2014-10-20T12:37:17+01:00'
slug: intuizione-e-ragionamento
layout: single
categories:
- Ideas
postLang: it
aliases:
- /2014/10/20/2445/
wp_original: https://orlotech.netsons.org/2014/10/20/2445/
archived_comments:
- author: Roy
  date: '2014-10-20'
  content: "<p>Per me questo è intuitivo -.-<br />\nLeggo lea e vedo una somma, leggo imul e vedo dei\
    \ numeri che si combinano fra di loro !</p>\n\n<p>88 [1]                temp=pyro[x-2][y-5][(t-6)];//1<br\
    \ />\n0x400c7b          8b 45 fc              mov    eax,DWORD PTR [rbp-0x4]<br />\n0x400c7e     \
    \     8d 70 fe              lea    esi,[rax-0x2]<br />\n0x400c81          8b 45 f8              mov\
    \    eax,DWORD PTR [rbp-0x8]<br />\n0x400c84          8d 50 fb              lea    edx,[rax-0x5]<br\
    \ />\n0x400c87          8b 45 ec              mov    eax,DWORD PTR [rbp-0x14]<br />\n0x400c8a    \
    \      83 e8 06              sub    eax,0x6<br />\n0x400c8d          48 63 c8              movsxd\
    \ rcx,eax<br />\n0x400c90          48 63 c6              movsxd rax,esi<br />\n0x400c93          48\
    \ 63 d2              movsxd rdx,edx<br />\n0x400c96          48 69 f0 96 00 00 00  imul   rsi,rax,0x96\
    \ &amp;lt;&amp;lt;-- imul moltiplicazione fra interi<br />\n0x400c9d          48 89 d0           \
    \   mov    rax,rdx<br />\n0x400ca0          48 c1 e0 04           shl    rax,0x4<br />\n0x400ca4 \
    \         48 29 d0              sub    rax,rdx<br />\n0x400ca7          48 01 f0              add\
    \    rax,rsi<br />\n0x400caa          48 8d 14 08           lea    rdx,[rax+rcx*1]<br />\n0x400cae\
    \          48 8d 05 2b 14 20 00  lea    rax,[rip+0x20142b]        # 0x6020e0 <br />\n0x400cb5    \
    \      48 01 d0              add    rax,rdx<br />\n0x400cb8          0f b6 00              movzx \
    \ eax,BYTE PTR [rax]<br />\n0x400cbb          88 45 f7              mov    BYTE PTR [rbp-0x9],al<br\
    \ />\n        89 [1]                temp=pyro[x+8][y+3][(t+4)];//2<br />\n0x400cbe          8b 45\
    \ fc              mov    eax,DWORD PTR [rbp-0x4]<br />\n0x400cc1          8d 70 08              lea\
    \    esi,[rax+0x8]<br />\n0x400cc4          8b 45 f8              mov    eax,DWORD PTR [rbp-0x8]<br\
    \ />\n0x400cc7          8d 50 03              lea    edx,[rax+0x3]<br />\n0x400cca          8b 45\
    \ ec              mov    eax,DWORD PTR [rbp-0x14]<br />\n0x400ccd          83 c0 04              add\
    \    eax,0x4<br />\n0x400cd0          48 63 c8              movsxd rcx,eax<br />\n0x400cd3       \
    \   48 63 c6              movsxd rax,esi<br />\n0x400cd6          48 63 d2              movsxd rdx,edx<br\
    \ />\n0x400cd9          48 69 f0 96 00 00 00  imul   rsi,rax,0x96<br />\n0x400ce0          48 89 d0\
    \              mov    rax,rdx<br />\n0x400ce3          48 c1 e0 04           shl    rax,0x4<br />\n\
    0x400ce7          48 29 d0              sub    rax,rdx<br />\n0x400cea          48 01 f0         \
    \     add    rax,rsi<br />\n0x400ced          48 8d 14 08           lea    rdx,[rax+rcx*1]<br />\n\
    0x400cf1          48 8d 05 e8 13 20 00  lea    rax,[rip+0x2013e8]        # 0x6020e0 <br />\n0x400cf8\
    \          48 01 d0              add    rax,rdx<br />\n0x400cfb          0f b6 00              movzx\
    \  eax,BYTE PTR [rax]<br />\n0x400cfe          88 45 f7              mov    BYTE PTR [rbp-0x9],al</p>"
- author: Roy
  date: '2014-10-20'
  content: '<p>Aggiungo che il regrado è palese, siamo "abituati" che le cose da svolgere siano rese il
    più possibile elementari che il cervello della maggioranza si atrofizza senza nemmeno rendersene conto...<br
    />

    W l''assembler !</p>'
- author: Darayavaush
  date: '2014-10-20'
  content: <p>Devono mettere la funzione like o +1 sui commenti</p>
- author: poz
  date: '2014-11-08'
  content: '<p>Dario come spunto per un post della serie involuzione propongo la ricerca della mediocrità,
    quand''anche dello scrauso..<br />

    E il come puntare al (apparente) appena sufficente non fa altro che progressivamente abbassare i nostri
    standard .</p>'
---

Una o più generazioni di menti potrebbero essere state rovinate da qualcosa che si supponeva dovesse essere d'aiuto.

Quante volte abbiamo sentito dire (o ci siamo lamentati al riguardo): "Questo metodo di apprendimento non è intuitivo" o "Questo programma (software) non è intutivo" o "Compra il nuovo tablet smartphone computer: ancora più intuitivo".

Ma chi l'ha detto che tutto debba essere intuitivo? Quanto è intuitivo un libro? Qualsiasi cosa si studi, viene chiamata in causa la ragione, la riflessione e l'analisi.

[Dizionario](http://dizionari.corriere.it/dizionario_italiano/I/intuitivo.shtml "Definizione "):

# intuitivo

##### **[in-tui-tì-vo]** **agg., s.**

- • **agg.**
- **1** Dell'intuizione: *facoltà i. della mente*; che si attua per mezzo dell'intuizione: *conoscenza i.*; in cui predomina l'intuizione sul ragionamento: *giudizio i.* || metodo i., secondo il quale l'insegnamento deve prendere l'avvio dai dati acquisiti dal bambino con l'esperienza diretta
- **2** estens. Che si capisce o s'intuisce facilmente; evidente: *verità i.*
- **3** Istintivo, naturale: *i. purezza di stile*
- **4** Che procede più per intuizione che per ragionamento: *persona i.*
- • **s.m.** (**f.** *-va*) Nell'accez. 4 dell'agg.
- • **avv.** intuitivamente, in modo i.
- • sec. XVI

In pratica intuitivo è divenuto sinonimo di semplice, immediato, facilitato, rapido: l'equivalente un cervello in poltrona, obeso, col diabete, che non fa altro che guardare la tv.

La realtà dei fatti è che poche cose possono essere comprese od eseguite veramente bene in maniera esclusivamente intuitiva. La vita non è una costante partita a biliardino. L'universo è un sistema complesso e la vita che ognuno di noi svolge al suo interno segue protocolli semplici e complessi organicamente e dinamicamente correlati. Non possiamo, non dobbiamo vivere come scimmie.

E la chiamerebbero evoluzione? Quand'anche fosse presente una reale ed effettiva evoluzione biologica, quindi neurale e intellettuale, è chiaro a tutti che è in atto una pesante INvoluzione culturale, intellettuale, per non entrare nel merito della morale e dell'etica.
