---
title: learn UV mapping in 8 hours
date: '2019-03-11T21:35:28+01:00'
slug: learn-uv-mapping-in-8-hours
layout: single
categories:
- English
- Ideas
postLang: en
aliases:
- /2019/03/11/learn-uv-mapping-in-8-hours/
wp_original: https://orlotech.netsons.org/2019/03/11/learn-uv-mapping-in-8-hours/
---

Such a catchy title, yet it is not an advertising. More of a personal experience.

As an architectural renderer, I've been acquainted with the concept of uv mapping for several years now. But i never actually delved into it - up until last week.

I received a proposal, an invitation, to submit a test job. The task was to model an object, then create physical-based-rendering textures, then map the texture to the model, export the finished product. Nice and neat. Or so it has seemed to me.

The major challenge: how on earth am I supposed to map a texture in a SketchUp model? What exactly do they mean by PBR workflow? And what's all this fuss about quads, n-gons, triangles?

The truth is I have always been aware of such issues, and that sooner or later i would have faced the moment when I would have been "forced" to deal with all this stuff. That is one reason I accepted the challenge.

Long story short, let's break up the work in phases (links below as footnotes):

#### Step 1 - Love your QUADS

The average SketchUp user does not bother much about quads. And it is not a coincidence. If you actually want to SEE them, or even work with them you will need QuadFace Tools, a free extension. Nice tool, quite simple to learn and use. Enough video tutorials to teach you on YouTube. A couple of hours or so, and you should be able to produce your first quad-based works. So far, so good.

#### Step 2 - PBR doesn't stand for PoopButtRigging

There would be so much to say about physics based rendering and material, and as a fan of MaxwellRender I could go on for quite a long time. I spare you, feel free to search around.

Just be aware that is more of a workflow than a specific tool or software. Yes, you will stumble upon Unity and Substance Painter as well, and for good reasons too. But once understood the principles behind the PBR maps (BaseColor/Diffuse, AmbientOcclusion, NormalMap, HeightMap/Roughness) you shall realize that with some work you can get out of Gimp what you need. (Just remember to install the normal map plugin, again, free).

#### Step 3 - The hardest part. UV mapping is not to be joked about

Sad but true: SketchUp won't let you directly UV-map anything per-se. You need another plugin. This time I used the one-week trial version of WrapR, a nice plugin made specifically for SketchUp. But you can obtain the same results with a very slightly different workflow using the free software Roadkill. Again, nice video tutorials, lots of people helping us out here. Thank you, by the way. After some 3-4 hours, you should be able to do you first and barely satisfying UV map of your model (given that it is your first try, like mine).

#### The last step - a sad conclusion (?)

The file was supposed to be delivered in a .fbx format. After all the effort and the work, I discovered that is not possible to directly export to this format from SketchUp. One more proof that the entire workflow was thought with 3dStudio in mind. Besides of this, it has been a really learning experience.

I do not have anything against a specific tool or software. But I actually do have a LOT against forcing people to use specific software rather than the ones they are familiar with. Even more if such software is heavy to run, costly, and made by huge software houses.

Power to the Open Source. Do your part and share with me in the fight for the freedom of software and workflow choice and interchangeability of formats. Woe to proprietary formats!

---

LINKS:

[Work with quads in SketchUp - QuadFace Tools](https://extensions.sketchup.com/en/content/quadface-tools)

[Download Gimp, just do it please.](https://www.gimp.org/)[And the Normal Map plugin here.](https://code.google.com/archive/p/gimp-normalmap/downloads)

[UV mapping - Roadkill](http://www.pullin-shapes.co.uk/page6.htm)

You may also be interested in [WrapR](https://wrap-r.com/), [SketchUv](https://extensions.sketchup.com/en/content/sketchuv) and a number of other tools which I am to lazy to list now.
