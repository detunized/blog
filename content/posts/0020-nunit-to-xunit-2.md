---
title: "NUnit to xUnit automatic test conversion: pattern match"
date: 2019-03-16
published: true
tags:
    - c-sharp
    - refactoring
    - roslyn
    - dotnet
---

In the [previous post]({{< ref "/posts/0019-nunit-to-xunit-1.md" >}}) I described how to use the Roslyn API to find code patterns in the C# AST and how to change the AST to rewrite the original code to something else. The goal was to automate the conversion of NUnit tests to xUnit. The approach I used was quite tedious, as I had to write a very long chain or ifs and typecasts to get the job done. Let's try to do better this time. Let's start with just the search part in our search-and-replace tool.

What would be great is to be able to specify structural patterns like this:

```c#
Assert.That(_, Is.EqualTo(_))
Assert.That(_, Is.EqualTo(true))
Assert.That(_, Is.Throws.TypeOf<_>())
```

And they would match the actual code:

```c#
// Matched by 'Assert.That(_, Is.EqualTo(_))'
Assert.That(account.Id, Is.EqualTo(id))
Assert.That("".ToBytes(), Is.EqualTo(new byte[] {}))

// Matched by 'Assert.That(_, Is.EqualTo(true))'
Assert.That(info.IsMd5, Is.EqualTo(true));
Assert.That(token.BoolAt(path, true), Is.EqualTo(true));

// Matched by 'Assert.That(_, Is.Throws.TypeOf<_>())'
Assert.That(() => Quad[-1], Throws.TypeOf<ArgumentOutOfRangeException>())
Assert.That(() => access(token, path), Throws.TypeOf<JTokenAccessException>())
```

At first it looks like a quite difficult task. But as it turns out in its simple form is not even that hard. I got the idea first when I was generating code for AST replacement with [Roslyn Quoter](https://roslynquoter.azurewebsites.net/). Looking at its source code I discovered a bunch of `Parse*` methods of the [`SyntaxFactory` class](https://docs.microsoft.com/en-us/dotnet/api/microsoft.codeanalysis.csharp.syntaxfactory?view=roslyn-dotnet).

So basically one function call will parse the snippet and return an AST for the given pattern:

```c#
var patternAst = SyntaxFactory.ParseExpression("Assert.That(_, Is.EqualTo(_))");
```

The one line above is equivalent to a wall of code like this:

```c#
var patternAst =
    InvocationExpression(
        MemberAccessExpression(
            SyntaxKind.SimpleMemberAccessExpression,
            IdentifierName("Assert"),
            IdentifierName("That")))
    .WithArgumentList(
        ArgumentList(
            SeparatedList<ArgumentSyntax>(
                new SyntaxNodeOrToken[]{
                    Argument(
                        IdentifierName("_")),
                    Token(SyntaxKind.CommaToken),
                    Argument(
                        InvocationExpression(
                            MemberAccessExpression(
                                SyntaxKind.SimpleMemberAccessExpression,
                                IdentifierName("Is"),
                                IdentifierName("EqualTo")))
                        .WithArgumentList(
                            ArgumentList(
                                SingletonSeparatedList<ArgumentSyntax>(
                                    Argument(
                                        IdentifierName("_"))))))})));
```

It feels like a total win already and we have not even done anything useful yet. But let's find this pattern in a source AST. First, we need to parse the file we're searching in:

```c#
var sourceAst = CSharpSyntaxTree.ParseText(File.ReadAllText(filename));
```

This gives us the list of all expression nodes in the AST:

```c#
var nodes = sourceAst.GetRoot().DescendantNodes().OfType<ExpressionSyntax>();
```

And now we find the nodes that match:

```c#
foreach (var e in nodes)
{
    if (Ast.Match(e, patternAst))
    {
        var line = e.GetLocation().GetLineSpan().StartLinePosition.Line;
        var code = e.NormalizeWhitespace();
        Console.WriteLine($"  {line}: {code}");
    }
}
```

Obviously the `Ast.Match` function is the tricky one. But not as tricky, really. We recursively traverse both ASTs in parallel and see if they match:

```c#
public bool Match(SyntaxNode code, SyntaxNode pattern)
{
    // A placeholder matches anything
    if (IsPlaceholder(pattern))
        return true;

    // Node types don't match. Clearly not a match.
    if (code.GetType() != pattern.GetType())
        return false;

    switch (code)
    {
    case ArgumentSyntax c:
        {
            var p = (ArgumentSyntax)pattern;
            return Match(c.Expression, p.Expression);
        }
    case ArgumentListSyntax c:
        {
            var p = (ArgumentListSyntax)pattern;
            return Match(c.OpenParenToken, p.OpenParenToken)
                && Match(c.Arguments, p.Arguments)
                && Match(c.CloseParenToken, p.CloseParenToken);
        }
    case IdentifierNameSyntax c:
        {
            var p = (IdentifierNameSyntax)pattern;
            return Match(c.Identifier, p.Identifier);
        }
    case InvocationExpressionSyntax c:
        {
            var p = (InvocationExpressionSyntax)pattern;
            return Match(c.Expression, p.Expression)
                && Match(c.ArgumentList, p.ArgumentList);
        }
    case LiteralExpressionSyntax c:
        {
            var p = (LiteralExpressionSyntax)pattern;
            return Match(c.Token, p.Token);
        }
    case MemberAccessExpressionSyntax c:
        {
            var p = (MemberAccessExpressionSyntax)pattern;
            return Match(c.Expression, p.Expression)
                && Match(c.Name, p.Name);
        }
    case GenericNameSyntax c:
        {
            var p = (GenericNameSyntax)pattern;
            return Match(c.Identifier, p.Identifier)
                && Match(c.TypeArgumentList, p.TypeArgumentList);
        }
    case TypeArgumentListSyntax c:
        {
            var p = (TypeArgumentListSyntax)pattern;
            return Match(c.LessThanToken, p.LessThanToken)
                && Match(c.Arguments, p.Arguments)
                && Match(c.GreaterThanToken, p.GreaterThanToken);
        }
    default:
        return false;
    }
}
```

So it's basically a giant switch with every node type in it. By far not every type is covered here, just those that I needed to get my examples to work. I imagine to cover the most of C# syntax I'd have to tediously write a couple of thousand lines of repetitive code. I'm not going to do it all any time soon. Just the stuff I need to cover my use cases.

With a [few more lines of code added this already becomes a useful tool](https://gist.github.com/detunized/d02a0640986f44243dc01e5f50f42e74) for searching for code patterns in a codebase. Next time we see how we can implement the replace part. The goal was to refactor, not just to search, wasn't it? I have some ideas on how it could be done. See you next time.

## Conclusion

Thanks to Roslyn awesome API with just [172 lines of code](https://gist.github.com/detunized/d02a0640986f44243dc01e5f50f42e74) we have a pretty advanced code grep. Surely, it's just a toy and a proof of concept at the moment. It would take a serious effort to make it something more than that. But I'm happy with what is possible with so little effort. Amazing.
