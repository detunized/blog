---
title: "DEV zen mode: userscript"
date: 2019-02-19
published: true
series:
    - DEV zen reading mode
tags:
    - devto
    - meta
    - javascript
    - showdev
---

For a long time I've been killing the top and the bottom bars on Medium while reading longer articles. This is especially true on mobile, where a huge amount of precious vertical reading space is taken up by all kinds of bars. Now it seems Medium got rid of those and it got much nicer to read.

DEV has a similar problem. I'm easily distracted by the visual noise and I find it difficult to concentrate on reading when there I see something but text. I can ignore the sidebar, but ignoring the horizontal bar on the bottom is difficult, especially when it cuts a line of text in the middle.

![Zen off](https://i.imgur.com/bGd1T78.png)

So this time I decided to automate the process and make a *userscript* that removes the top, bottom and sidebars with a keyboard shortcut. Welcome [DEV zen mode](https://github.com/detunized/dev-zen-mode). Install it, press Shift-Z while in the article section and all the boxes go away. Press the same key again to bring them back.

![Zen on](https://i.imgur.com/UOCjwkN.png)

To install the script you'd need a userscript manager extension installed in your browser. That would be [Tampermonkey](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=en) for Chrome or [Greasemonkey](https://addons.mozilla.org/en-US/firefox/addon/greasemonkey/) for Firefox.

The script itself is available on [openuser.js](https://openuserjs.org/scripts/detunized/DEV_Zen_mode). Alternatively it's possible to create a new script with Tampermonkey/Greasemonkey and paste the file form [GitHub](https://github.com/detunized/dev-zen-mode/blob/master/dev-zen-mode.user.js) into it.

The core of the feature was not that difficult to put together. Adding a keyboard shortcut and hiding some elements is pretty trivial with vanilla JavaScript. I'm sure the code is not very robust yet and could benefit from some cleaning up. For one thing, I'm not saving the original `display` property, just assuming it's blank. It works not, but might get broken when CSS changes.

There was one problem I ran into though. I wanted to be able to bring back the hidden elements when the user navigates away from the page. To make this happen I tried to find an event that is fired when the URL changes. To my surprise everything I found online didn't work. I tried to add a listener for [`hashchange` event](https://developer.mozilla.org/en-US/docs/Web/API/WindowEventHandlers/onhashchange), but couldn't get any callbacks to trigger. After a while I gave up and used some [hack](https://stackoverflow.com/a/18950690/362938) I found on StackOverflow.

I would really love to see this becoming a feature of DEV. It doesn't have to be exactly like this, but some kind of a reading mode would be really nice to have. I'm not a web developer and I don't think I have the chops to contribute a feature like this to the codebase. Anyone interested? =)
