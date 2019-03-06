---
title: "Base64 decoding bug that is present in all version of .NET"
date: 2019-03-06
published: true
tags:
    - c-sharp
    - dotnet
    - bug
    - base64
---

One sunny morning I was sitting in front of my laptop refactoring some C# code. Everything was going very smooth and it was going to be a productive day. And then I added one too many equal signs to a constant string literal and things just blew up. Gone the productivity. Gone the peaceful refactoring Sunday. Even the sun decided to hide behind the cloud.

After spending 30-40 minutes trying to figure out what I did wrong, I realized it wasn't me. It was Microsoft. Apparently, I stumbled upon an ancient bug in Base64 decoding function. This bug must be present since the introduction of `Convert.FromBase64String` in .NET 1.1 in the year of 2003. Whoa! That's old. And it's not very difficult to reproduce. Here you go:

```c#
Convert.FromBase64String("abc==");
```

Technically this is an illegal Base64. The legal version is `"abc="`. Notice only one padding character `=`. The Base64 encoding represents every 6 bits of the binary input with one ASCII character. This means every 4 characters in the Base64 encoded string represent 3 bytes. When the encoded data is not a multiple of 3 bytes Base64 encoder adds padding characters to make the Base64 a multiple of 4 characters. This makes `"abc="` a correctly padded Base64 string. Adding another `=` to it makes it invalid.

Base64 `"abc="` decodes to two bytes `[105, 183]`. This is correct. Adding another padding character at the end shouldn't really change the encoded value. It's like adding a space at end of the sentence. Yes, it's there, but it doesn't change the meaning of the sentence. But .NET doesn't think so. `"abc=="` decodes to one byte of `[109]`. Not only it got shorter, which is weird since we made the input longer. It also got different. The first byte changed from 105 to 109. And an exception didn't get thrown either. Add another `=` and you'll get an exception. Amazing!

[Code](https://dotnetfiddle.net/JarxXF):

```c#
using System;

public class Program
{
    public static void Main()
    {
        DecodeAndPrint("abc=");
        DecodeAndPrint("abc==");
    }

    static void DecodeAndPrint(string base64)
    {
        Console.WriteLine(
            "'{0}' -> [{1}]",
            base64,
            string.Join(", ", Convert.FromBase64String(base64)));
    }
}
```

Output:

```
'abc=' -> [105, 183]
'abc==' -> [109]
```

And what is *really* amazing, is that no one discovered this for so many years. Or it got discovered, but it didn't get fixed. Base64 is quite fundamental in the information exchange over the wire. It is used all over the place. Yet, .NET got away with a totally broken Base64 decoder for so many years.

At first I couldn't believe it and started to investigate it. I googled for a while and didn't really find much. Then I posted on [StackOverflow](https://stackoverflow.com/q/54852219/362938), but didn't get much luck there either. I had to even [answer](https://stackoverflow.com/a/54852796/362938) my own question once I figured out what's going on. After searching on GitHub for a while I stumbled upon a [fix](https://github.com/dotnet/corefx/pull/30814) in .NET Core made in July 2018. So the latest .NET Core version handles this correctly and throws an exception:

```
Unhandled Exception: System.FormatException: The input is not a valid Base-64 string as it contains a non-base 64 character, more than two padding characters, or an illegal character among the padding characters.
   at System.Convert.FromBase64CharPtr(Char* inputPtr, Int32 inputLength)
   at System.Convert.FromBase64String(String s)
   at Program.DecodeAndPrint(String base64) in ./base64/Program.cs:line 13
   at Program.Main() in ./base64/Program.cs:line 8
```

It took them about 15 years to find this and fix it. What's interesting is that no one really tried to fix it specifically. It happened while they [rewrote the code to make it faster](https://github.com/dotnet/corefx/pull/30814#issue-199014852):

> Convert.FromBase64() had a subtle bug where an illicit
second padding character at the end of the string caused
the decode to "succeed" by dropping the fifth to
last character.

> We inadvertently fixed this bug while optimizing that
api in .NetCore 2.1. Adding test to document bug and
ensure we don't regress.

So this is fixed in .NET Core 2.2. But it's still broken in the current latest version of .NET Framework 4.7.2. And it looks like it's broken in [Mono too](https://repl.it/repls/FriendlyOnlyVerification).

A workaround for .NET 4.7.2 would be to repad incorrectly padded strings with something like this:

```c#
// This only works for base64 without spaces or linebreaks.
string Repad(string base64)
{
    var l = base64.Length;
    return l % 4 == 1 && base64[l - 1] == '='
        ? base64.Substring(0, l - 1)
        : base64;
}
```

*Also published on [DEV](https://dev.to/detunized/base64-decoding-bug-that-is-present-in-all-version-of-net-1fkp) and [Medium](https://medium.com/@detunized/base64-decoding-bug-that-is-present-in-all-version-of-net-f53733cecdc1)*
