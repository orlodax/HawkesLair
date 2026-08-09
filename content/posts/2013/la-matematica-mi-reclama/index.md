---
title: La Matematica mi reclama...
date: '2013-03-04T10:20:11+01:00'
slug: la-matematica-mi-reclama
layout: single
categories:
- Ideas
cover: cover-dice-1.jpg
postLang: it
aliases:
- /2013/03/04/la-matematica-mi-reclama/
wp_original: https://orlotech.netsons.org/2013/03/04/la-matematica-mi-reclama/
---

Qualche giorno fa mentre svolgevo normali attività quali mangiare, chiacchierare, guidare, mi sono messo a pensare a un modo rapido per calcolare una serie di numeri da 1 a n. L'idea è partita dall'osservazione della seguente caratteristica dei dadi da gioco: le facce opposte di un dado, sommate, come risultato danno sempre il numero di facce di un dado +1. Ovvero, un dado da sei, il classico dado cubico, ha tre coppie di facce la cui somma fa 7 (6 e 1, 5 e 2, 3 e 4). Quindi la somma complessiva dei suoi sei numeri equivale a 7*3=21.

Ora questo, generalizzando, può essere scritto come (n+1)*n/2, dove "n" sta per l'ultimo numero della serie. Cosicché, nel caso del dado, si ha (6+1)*6/2 che fa appunto 21.

Ovviamente ho scoperto l'acqua calda, perché: *"Si racconta che questo metodo per calcolare le somme da una serie di numeri consecutivi fu  intuito anche dal famoso matematico tedesco Carl Fiedrich Gauss (1777 - 1855) che già all'età di 10 anni stupì il suo insegnante di matematica, un certo Buttner, persona ben nota per essere piuttosto cinica e irrispettosa (sopratutto nei confronti degli studenti di famiglie povere come era quella di Gauss). Un giorno che gli studenti erano particolarmente turbolenti, Buttner diede loro, come punizione, il compito di calcolare la somma dei primi 100 numeri (dall' 1...fino a100) pensando così di tenerli impegnati per lungo tempo ad eseguire un centinaio di somme. Ma dopo solo pochi minuti, fu interrotto dalla vocina di Gauss che gli pose sotto gli occhi il risultato (5050) che egli aveva già calcolato."*

Ma la soddisfazione è esserci arrivato da solo...

Inoltre, tale formula mi ricordava in maniera molto sospetta l'area del triangolo, in quanto può essere scritta come [(n+1)*(n)]/2, ovvero b*h/2, la classica base per altezza diviso 2.

|  |  |
| --- | --- |
| *Somma* da 1 a n = | *(n+1)* * *n* |
| 2 |

A pensarla sul piano cartesiano, infatti, otteniamo un triangolo rettangolo che ha per cateti proprio n. Per qualche ragione, però, la sommatoria in questione non è propriamente un triangolo rettangolo, ma un cateto è maggiore di un'unità all'altro.

Ne consegue però che:

— la sommatoria di numeri interi altro non è che l'integrale di quel triangolo, o meglio della sua ipotenusa;

— per n che tende a infinito abbiamo proprio un triangolo rettangolo, (o meglio, la funzione y=x).

Acqua calda, e neanche scaldata a puntino... Ma senza aiuto di nessuno ^_^

[(image credit)](http://www.tony-cragg.com/ "Scultura di dadi")
