---
title: "NUnit to xUnit automatic test conversion: source code transformation"
date: 2019-03-26
published: true
tags:
    - c-sharp
    - refactoring
    - roslyn
    - dotnet
cover_image: https://images.unsplash.com/photo-1480515883589-dcaa74351fd6
---

In the [previous post]({{<ref "/posts/0020-nunit-to-xunit-2.md">}}) I wrote about how I find the patterns in the code that I would like to refactor using simple C# syntax. Basically, I write the exact expression I would like to find with some wildcards that match the varying parts and the rest is matched as is. A bit like a regexp or a shell file glob. Like this:

```c#
Assert.That(_, Is.EqualTo(_))
Assert.That(_, Throws.TypeOf<_>())
```

or

```c#
_._(_, _)
```

if you'd like to go extreme and match every member function call with two parameters.

What I would like to be able to do, though, is to transform the code, not just match. I'd like to specify how to convert the patterns to the form I'm after. For example:

```c#
Assert.That(@actual, Is.EqualTo(@expected)) -> Assert.Equal(@expected, @actual)
```

Well, this is exactly the syntax I'm going to use. The placeholders `@actual` and `@expected` match any expression subtrees in the AST, anything that could be placed as arguments in those two positions. It's actually a valid C# code as it allows `@` at the beginning of an identifier. In my matcher I treat any identifier that starts with an `@` as a placeholder.

The code in the previous post only matched the patterns (`_` matches anything, a bit like `.*` in a regex). Now we need to store the named matches, like the match groups in a regex. The code would have to be changed from

```c#
// A placeholder matches anything
if (IsPlaceholder(pattern))
    return true;
```

to

```c#
// A placeholder matches anything
if (IsPlaceholder(pattern))
{
    var name = pattern.ToFullString();
    if (name != "_")
        Matches[name] = code;

    return true;
}
```

The rest of the matching code stays practically untouched. We have a matcher, the next step would be to write a *"substituter"* or *"replacer"*, the *replace* part of the find-and-replace tool.

Since I like to keep my code [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself), first I spent a bunch of time thinking about how to reuse the matching code for the substitution part. I failed there. So I decided to go with [WET](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself#DRY_vs_WET_solutions) instead and rewrite that giant switch once again.

```c#
// _variables is populated in the constructor
public SyntaxNode Replace(SyntaxNode template)
{
    // A placeholder found. Substitute.
    if (IsPlaceholder(template))
    {
        var name = template.ToFullString();
        if (_variables.TryGetValue(name, out var v))
            return v;

        return template;
    }

    switch (template)
    {
    case ArgumentSyntax t:
        return t.Update(t.NameColon,
                        t.RefKindKeyword,
                        (ExpressionSyntax)Replace(t.Expression));
    case ArgumentListSyntax t:
        return t.Update(t.OpenParenToken,
                        Replace(t.Arguments),
                        t.CloseParenToken);
    case IdentifierNameSyntax t:
        return t.Update(Replace(t.Identifier));
    case InvocationExpressionSyntax t:
        return t.Update((ExpressionSyntax)Replace(t.Expression),
                        (ArgumentListSyntax)Replace(t.ArgumentList));
    case LiteralExpressionSyntax t:
        return t.Update(Replace(t.Token));
    case MemberAccessExpressionSyntax t:
        return t.Update((ExpressionSyntax)Replace(t.Expression),
                        t.OperatorToken,
                        (SimpleNameSyntax)Replace(t.Name));
    case GenericNameSyntax t:
        return t.Update(Replace(t.Identifier),
                        (TypeArgumentListSyntax)Replace(t.TypeArgumentList));
    case TypeArgumentListSyntax t:
        return t.Update(t.LessThanToken, Replace(t.Arguments), t.GreaterThanToken);
    default:
        return template;
    }
}
```

This code recursively walks the replace template AST and substitutes the placeholders (like `@actual` and `@expected`) with the matches found in the previous step. The end result of this substitution is then swapped with the matched expression node in the original source file AST. And that's it. Works like a charm.

> A side note on the choice of keywords here. I'm not an OOP aficionado. I think it has its place and in C# it's quite natural to use classes and member functions to represent and do stuff. Though most of the time I try to stick to more of a functional style, where functions don't have any hidden state and take all their input as parameters and return the result.  Most of my functions and classes are static, actually. But common sense wins most of the time for me (or so I hope). So, in this case, I went with a class and non-static functions to not to pass around the state into every function, as there are quite many recursive calls. I kept it DRY in a sense.

I wrote a small driver application for this algorithm. It takes care of the loading, parsing, writing out the result. All the patterns are hardcoded for now, but there's nothing but my laziness stopping me from putting that into a config file.

Here are the patterns I used to convert the bulk of my tests:

```c#
Assert.That(@actual, Is.EqualTo(true))      -> Assert.True(@actual)
Assert.That(@actual, Is.EqualTo(false))     -> Assert.False(@actual)
Assert.That(@actual, Is.EqualTo(@expected)) -> Assert.Equal(@expected, @actual)
Assert.That(@code, Throws.TypeOf<@type>())  -> Assert.Throws<@type>(@code)
```

## Conclusion

The solution described here is not a working tool ready to be picked up and used by anyone. It's a proof of concept that happens to work and it has value. At least for me. I was able to convert hundreds of tests across dozens of files, saving myself a couple of hours of tedious manual labor. The time I put into this tool I didn't get back. Pure ROI is negative here. But it's not only about time. I got plenty of satisfaction from learning something new, from automating an annoying task, from blogging about it and sharing it with the world.

The code could be found [here](https://github.com/detunized/nunit2xunit).

## Future work

Not every AST node type is covered by the pattern matching code and not every possible `Assert` expression is covered by the patterns. That is something to expand on. Maybe this could also be turned into a Visual Studio [Code] extension. In general this doesn't have to be a unit test conversion tool. With this mini-DSL it's possible to refactor/convert any code really. It's also possible to search for the matches in the codebase. Lots of ideas and not so much time.

*Also published on [DEV](https://dev.to/detunized/nunit-to-xunit-automatic-test-conversion-source-code-transformation-16pc) and [Medium](https://medium.com/@detunized/82e8529fd415)*
