---
title: "NUnit to xUnit automatic test conversion"
date: 2019-03-13
published: true
tags:
    - c-sharp
    - refactoring
    - roslyn
---

I'm currently working on a major refactoring of a C# library which has many NUnit tests. I decided, without having any good reason, it would be a good idea to migrate them to xUnit. I did a few by hand and it turns out to be tedious. Like really tedious. The most common pattern is the following:

The test in NUnit

```c#
Assert.That(actual, Is.EqualTo(expected));
```

becomes the test in xUnit:

```c#
Assert.Equal(expected, actual);
```

To convert each by hand requires a lot of patience and stamina. Since I don't have either, after doing a few dozens manually I decided to automate the whole thing. The first most obvious approach would be to use a regexp and convert one to the other like so:

```
/Assert\.That\((.*?), Is\.EqualTo\((.*)\)\)/ -> Assert.Equal($2, $1)
```

It does work for some simple cases, but throw in something a bit hairier and the whole thing goes sideways. A perfectly valid small test tears this regexp to shreds:

```c#
Assert.That("));", Is.EqualTo("));")); -> Assert.Equal(", "));");;"));
```

Not good.

The better way to do that would be to parse the source file into an AST (Abstract Syntax Tree) and perform source to source transformations on it. I've done a bit of this in the past with C++ using [Clang/LLVM](https://clang.llvm.org/) and with JavaScript using [Acorn parser](https://github.com/acornjs/acorn). For C# there's [Roslyn](https://github.com/dotnet/roslyn).

How difficult could this be? Let's find out. There's some amount of documentation out there and some samples. Also, it's possible to generate a starter project with VS2017 that would do the file loading and minimal AST traversal. It's a good start, we can build on it. Here's a good [starting point](https://github.com/dotnet/roslyn/wiki/Getting-Started-C%23-Syntax-Transformation) for source transformation, for example.

So here's a simplest NUnit module:

```c#
using NUnit.Framework;

namespace Test
{
    [TestFixture]
    class DumpTests
    {
        [Test]
        public void One_plus_one_should_be_two()
        {
            Assert.That(1 + 1, Is.EqualTo(2));
        }
    }
}
```

When converted to xUnit, it becomes this:

```c#
using Xunit;

namespace Test
{
    class DumpTests
    {
        [Fact]
        public void One_plus_one_should_be_two()
        {
            Assert.Equal(2, 1 + 1);
        }
    }
}
```

Precisely the following needs to be done:

- change `using` directive
- remove `TextFixture` class attribute
- replace `Test` attribute with `Fact`
- change `Assert.That` to `Assert.Equal` and swap arguments

The syntax rewriter does all the work, we just need to fill in some logic:

```c#
public class NunitToXunitRewriter: CSharpSyntaxRewriter
{
    ...
}
```

Let's start with the easiest, removing the `TextFixture` attribute:

```c#
public class NunitToXunitRewriter: CSharpSyntaxRewriter
{
    public override SyntaxNode VisitAttributeList(AttributeListSyntax node)
    {
        if (ShouldRemoveTestFixture(node))
            return null;

        return base.VisitAttributeList(node);
    }

    // Checks if the node is "[TestFixture]" and should be removed
    private bool ShouldRemoveTestFixture(AttributeListSyntax node)
    {
        return node.Attributes.Count == 1
            && node.Attributes[0].Name.ToString() == "TestFixture"
            && node.Parent is ClassDeclarationSyntax;
    }
}
```

The code, in this case, is quite simple. The `VisitAttributeList` function gets called for every attribute in the source file. We just check that the attribute list has only one attribute, that its name is `TextFixture` and the parent node is a class. If it's all true, then we just return `null` from the visitor method to indicate that the node should be deleted from the syntax tree. Easy.

Next up is the `Test` attribute:

```c#
public class NunitToXunitRewriter: CSharpSyntaxRewriter
{
    public override SyntaxNode VisitAttributeList(AttributeListSyntax node)
    {
        var newNode = TryConvertTestAttribute(node);
        if (newNode != null)
            return newNode;

        return base.VisitAttributeList(node);
    }

    // Converts "[Test]" to "[Fact]"
    private SyntaxNode TryConvertTestAttribute(AttributeListSyntax node)
    {
        if (node.Attributes.Count != 1)
            return null;

        if (node.Attributes[0].Name.ToString() != "Test")
            return null;

        if (!(node.Parent is MethodDeclarationSyntax))
            return null;

        return
            AttributeList(
                AttributeList<AttributeSyntax>(
                    Attribute(
                        IdentifierName("Fact"))))
            .NormalizeWhitespace()
            .WithTriviaFrom(node);
    }
}
```

What we do here is quite similar to the previous example, with one exception that we're not deleting the node, but replacing it with something else. First, we check that it's a single attribute named `Test` and it's attached to a function. To replace it, we need to construct a new syntax node. In this case, it's the same thing, just the name is different. To build the syntax node we use `SyntaxFactory` methods, like `AttributeList`, `Attribute` and so on. The small quirk is the `NormalizeWhitespace` and
`WithTriviaFrom` bits. Those make sure the resulting code is formatted and has the whitespace copied from the original node. Otherwise, the output code would look out of place and would require reformatting.

The `using` directive change is also trivial. It's very similar to the `Fact` attribute situation above:

```c#
public class NunitToXunitRewriter: CSharpSyntaxRewriter
{
    public override SyntaxNode VisitUsingDirective(UsingDirectiveSyntax node)
    {
        var newNode = TryConvertUsingNunit(node);
        if (newNode != null)
            return newNode;

        return base.VisitUsingDirective(node);
    }

    // Converts "using NUnit.Framework" to "using Xunit"
    private SyntaxNode TryConvertUsingNunit(UsingDirectiveSyntax node)
    {
        if (node.Name.ToString() != "NUnit.Framework")
            return null;

        return
            UsingDirective(IdentifierName("Xunit"))
            .NormalizeWhitespace()
            .WithTriviaFrom(node);
    }
}
```

The `Assert` conversion is a much more complicated case. The problem that the expression we want to match is quite complex, even though it doesn't look like that. There's a member function access `Assert.That` and a function call `Assert.That(...)` and the argument list made up of two arguments, where the second one is a member function call as well: `Assert.That(actual, Is.EqualTo(expected))`. Using [Roslyn Quoter](http://roslynquoter.azurewebsites.net/) tool it's possible to generate the code that creates such an expression:

```c#
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
                    IdentifierName("actual")),
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
                                    IdentifierName("expected"))))))})))
```

In the AST form this little snippet of code looks pretty huge. When we want to replace this pattern with a different piece of code, we need to find it first. And that means we need to check against the structure of every function call expression in the file and see if it's similar:

```c#
public class NunitToXunitRewriter: CSharpSyntaxRewriter
{
    public override SyntaxNode VisitInvocationExpression(InvocationExpressionSyntax node)
    {
        var newNode = TryConvertAssertThatIsEqualTo(node);
        if (newNode != null)
            return newNode;

        return base.VisitInvocationExpression(node);
    }

    // Converts Assert.That(actual, Is.EqualTo(expected)) to Assert.Equal(expected, actual)
    private SyntaxNode TryConvertAssertThatIsEqualTo(InvocationExpressionSyntax node)
    {
        // Check it's Assert.That member
        if (!IsMethodCall(node, "Assert", "That"))
            return null;

        // It must have exactly two arguments
        var assertThatArgs = GetCallArguments(node);
        if (assertThatArgs.Length != 2)
            return null;

        // The second argument must be a `Is.EqualTo`
        var isEqualTo = assertThatArgs[1].Expression;
        if (!IsMethodCall(isEqualTo, "Is", "EqualTo"))
            return null;

        // With exactly one argument
        var isEqualToArgs = GetCallArguments(isEqualTo);
        if (isEqualToArgs.Length != 1)
            return null;

        // Grab the arguments
        var expected = isEqualToArgs[0];
        var actual = assertThatArgs[0];

        // Build a new AST with the actual and expected nodes inserted into it
        return
            InvocationExpression(
                MemberAccessExpression(
                    SyntaxKind.SimpleMemberAccessExpression,
                    IdentifierName("Assert"),
                    IdentifierName("Equal")))
            .WithArgumentList(
                ArgumentList(
                    SeparatedList<ArgumentSyntax>(
                        new SyntaxNodeOrToken[] {expected, Token(SyntaxKind.CommaToken), actual})))
            .NormalizeWhitespace()
            .WithTriviaFrom(node);
    }
}
```

To match the expression we have to drill down into the AST and compare node by node. It's very tedious, but luckily after the code is written it will convert all the tests that have a similar structure. Write once, run many times. The two helper functions that are used in this matching code look like this:

```c#
private bool IsMethodCall(ExpressionSyntax node, string objekt, string method)
{
    var invocation = node as InvocationExpressionSyntax;
    if (invocation == null)
        return false;

    var memberAccess = invocation.Expression as MemberAccessExpressionSyntax;
    if (memberAccess == null)
        return false;

    if ((memberAccess.Expression as IdentifierNameSyntax)?.Identifier.ValueText != objekt)
        return false;

    if (memberAccess.Name.Identifier.ValueText != method)
        return false;

    return true;
}

private ArgumentSyntax[] GetCallArguments(ExpressionSyntax node)
{
    return ((InvocationExpressionSyntax)node).ArgumentList.Arguments.ToArray();
}
```

In case the expression is a match, we take the `expected` and `actual` arguments, or the AST nodes that represent them, to be exact and wrap them into a different AST that represents the xUnit equivalent: `Assert.Equal(expected, actual)`.

Not that crazy difficult. But now we have a tool that can convert a majority of tests from NUnit to xUnit automagically. And it not only converts the `Assert` expressions but the whole file. Nice!

The sucky part is that the matching code is very specific to the expression we're trying to convert. So if we have a few variations of the `Assert` it would take writing so much code for every case. It's gonna very quickly get out of control. Imagine just a few very simple variations:

```c#
Assert.That(actual, Is.True());
Assert.That(actual, Is.EqualTo(true));
Assert.That(actual, Is.False());
Assert.That(actual, Is.EqualTo(false));
```

To cover most common NUnit cases we'd have to write hundreds of those matching functions with very repetitive code. That would be a **LOT** of work. Can we do better? Yes, we can! I have an idea and I'll describe in the next post.

## Conclusion

In only [175 lines of code](https://gist.github.com/detunized/8d548bb3b6808f7f076ed1a5f2c6ddd4) we have a fully functional converter that does in a second what takes a lot of time to do by hand. Even though it's just a proof of concept and doesn't cover any significant amount of NUnit assertions, I was able to convert a few files with tests with almost no additional fixing.
