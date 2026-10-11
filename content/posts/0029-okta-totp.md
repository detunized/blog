---
title: "Getting the TOTP secret out of Okta Verify"
date: 2026-10-11
draft: true
tags:
    - reverse-engineering
    - okta
    - totp
    - android
---

I keep all my 2FA codes in 1Password. It's convenient, everything is in one place and the codes get filled in automatically. Then Okta came along and wanted me to install Okta Verify. There's no Google Authenticator option and no way to see the secret. So, another app on my phone and I have to pull it out of my pocket every time I log in.

I've been here [before]({{< ref "/posts/0027-dont-make-me-hack-your-software.md" >}}). Investigation it is, then.

## The QR code

Okta Verify is enrolled by scanning a QR code. It's easy to decode a screenshot of it and inside there's a URL like this:

```
oktaverify://...?t=XXXX&f=YYYY&s=https://company.okta.com
```

`t` is a one time token, `f` is the authenticator ID and `s` is the Okta server. The app takes all this, talks to the server and somewhere in that conversation there should be a TOTP secret. TOTP is just a function of a secret and the current time. If I get the secret, any authenticator app would do. How difficult could this be? Let's find out.

## The app

I grabbed the Android APK of Okta Verify 8.22.2 and ran it through [jadx](https://github.com/skylot/jadx). I got about 23 thousand Java files out of it. Most of them are libraries, but Okta's own code was there too. And it was unreadable. Every string in it is encrypted with DexGuard and looks like this:

```java
C13441 c134416 = new C13441("_{@j){(t&`3");
```

Each string is decoded at runtime by a little function full of arithmetic like `(a + b) - (a | b)`, which is just a convoluted way to write `a & b`. The constants are different in every decoder class. Without the strings there's no way to see what the app sends to the server. And that's exactly what I needed to see.

This is where AI agents came in handy. I pointed them at the problem and let them do the grunt work. The first attempt was to port the decoder to Python. It kinda worked, but some of the constants came out wrong and many strings turned into garbage. The second attempt was to not reimplement anything and run the real thing instead. Convert the DEX to a JAR, load the actual obfuscated classes into a JVM and call the decoders via reflection. That decoded 20,703 strings. Each decoded value went into a comment next to the original:

```java
C13441 c134416 = new C13441("_{@j){(t&`3"); /* decoded: "okta_verify" */
```

After 17 throwaway scripts in Java and Python I finally had readable code. I would never have the patience to do this by hand.

## Enrollment

Now that I could read the code, the enrollment turned out to be just one request. A `POST` to `/idp/authenticators` on the Okta server with `Authorization: OTDT <t>` and a JSON body that describes the "device": an Android phone with a model name, an OS version and a public key. For TOTP the private half of that key is never used, so any key will do. In the list of methods I ask only for `totp`.

There was one catch, though. The request needs `"key": "okta_verify"` and the server refuses to cooperate without it. That's the string from the example above. There's no way I would have guessed that without decoding the strings first.

The response contains `sharedSecret`. It's a regular base32 secret, SHA-1, 6 digits, 30 seconds. I pasted it into 1Password and the codes matched the ones in Okta Verify. Voilà!

## The tool

A script in the terminal is fine for me, but I wanted something I could just open. So I made a tiny web page. Paste a screenshot of the QR code, it gets decoded right in the browser, press the button and get the secret. Okta doesn't allow requests from random web pages, so there's a small Cloudflare Worker that forwards that one request. It doesn't store anything. If you don't trust me, the code is on [GitHub](https://github.com/detunized/okta-totp), deploy your own.

It lives [here](https://okta-totp.detunized.workers.dev/). The new device shows up in the Okta account under whatever name you give it. Mine is called "1Password".

Dear Okta, TOTP is a standard. Please just let me use whatever app I want and nobody would have to decrypt twenty thousand strings.
