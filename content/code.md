---
title: "Code"
date: 2026-10-11T12:00:00+02:00
draft: false
---

A few things I've built that are worth a look. The rest is on [GitHub](https://github.com/detunized).

## Password Manager Access

A .NET library with read only access to nine online password managers: 1Password, Bitwarden, Dashlane, LastPass, Proton Pass, RoboForm, Sticky Password, True Key and Zoho Vault. It logs in, downloads the vault and decrypts it locally, just like the official apps. It also reads the offline OPVault format.

C# · [GitHub](https://github.com/detunized/password-manager-access) · [NuGet](https://www.nuget.org/packages/PasswordManagerAccess/)

## Earlier password manager libraries

Before Password Manager Access each service had its own library. The LastPass ones are still the most popular things I've published.

LastPass in [Ruby](https://github.com/detunized/lastpass-ruby), [C#](https://github.com/detunized/lastpass-sharp) and [C++](https://github.com/detunized/lastpass-cpp) · [1Password](https://github.com/detunized/1password-ruby), [Bitwarden](https://github.com/detunized/bitwarden-ruby) and [Dashlane](https://github.com/detunized/dashlane-ruby) in Ruby

## nunit2xunit

A proof of concept that converts NUnit tests to xUnit by rewriting the C# syntax tree. I wrote about it in [three](/posts/2019-03-12-nunit-to-xunit-automatic-test-conversion/) [blog](/posts/2019-03-16-nunit-to-xunit-automatic-test-conversion-pattern-match/) [posts](/posts/2019-03-26-nunit-to-xunit-automatic-test-conversion-source-code-transformation/).

C# · [GitHub](https://github.com/detunized/nunit2xunit)

## OTP Web

A single page TOTP code viewer. Import an authenticator export and see live codes. There is no backend, everything stays in the browser.

JavaScript · [Open it](https://1otp.netlify.app/) · [GitHub](https://github.com/detunized/otp-web)

## Pentomino calendar solver

Finds every way to cover a pentomino calendar puzzle board for any date, using backtracking search in a Web Worker.

JavaScript · [Try it](https://tubular-kringle-bb7f7b.netlify.app/) · [GitHub](https://github.com/detunized/pentomino-cal-solver)
