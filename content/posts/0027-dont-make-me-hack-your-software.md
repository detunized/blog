---
title: Don't make me hack your software
date: 2019-04-17
published: true
tags:
    - hacks
    - osx
cover_image: https://i.imgur.com/B6lhau5.jpg
---

I got a new corporate VPN tool the other day. It's called [Pulse Secure](https://www.pulsesecure.net/). It worked fine, thank you very much, no complains there. But then I tried to quit

![exit](https://i.imgur.com/Nf6gDQ1.png)

and I got this

![disallowed](https://i.imgur.com/f8rI72s.png)

That pissed me off right then and there. Why would any remote admin tell me what to do on my local machine? Even if it's a company machine. When I do not use the VPN or maybe I'm not even connected to any WiFi, why should I have this running? It's just silly to try to prevent me doing something on the machine where I have the root access. When this gets pushed onto a developer's laptop (as opposed to an account or HR clerk) it simply becomes a challenge.

It has no impact on the security of the machine or the corporate network when it's simply running in the background. This is not anti-virus software. It has an impact on the battery life and other resources like RAM and CPU though. And I need those. It's exactly this type of programs that don't exit, hang around and prevent me from running yet another Electron app on my laptop. Sometimes one is not enough, you know.

I guess I'd have to get my hands dirty instead of doing something I was actually going to do. Simply killing it from the command line didn't work. It just starts over. Investigation it is, then.

First, I took a quick look at the list of the open files from the Activity Monitor. There I found a log file (bottom row):

![am](https://i.imgur.com/2g86MNQ.png)

The tool developers were very kind and dumped about half a meg of stuff on every restart cycle into the log. So it's wasting my disk space as well then. Amongst thousands of lines, I found a reference to `/Library/Application Support/Pulse Secure/Pulse/connstore.dat`. It sounded promising. After poking around in that file and trying this and that, I found a parameter that is responsible for that.

```js
ive "921sn438-qoo8-4pp4-85p7-68q5s2592o32" {
    ...
    connection-policy-override: "false"
    ...
}
```

When this parameter is changed to `true` and the tool is restarted I was able to quit. Voilà!

![done](https://i.imgur.com/xfEeC0C.png)

Yes, I do.

And here the script that automates the whole thing:

```bash
cd '/Library/Application Support/Pulse Secure/Pulse'
sudo sed -i '' \
      s'/connection-policy-override: "false"/connection-policy-override: "true"/' \
      connstore.dat
sudo killall PulseTray 'Pulse Secure' dsAccessService
```

Dear developers and sysadmins, please don't do that again. You're just wasting everybody's time. Rather put your efforts into making the software more reliable, less resource hungry, more secure.

*Also published on [DEV](https://dev.to/detunized/don-t-make-me-hack-your-software-2k8d) and [Medium](https://medium.com/@detunized/dont-make-me-hack-your-software-36116de3c4d2)*
