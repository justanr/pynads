#pynads

Just playing around with implementing monads in Python.

There's also a little metaclass muckery thrown in for good measure!

Don't take it too seriously, this is just a toy project.

I was good enough to include a test suite though.


Quick Examples
--------------

It comes with Maybe and Either implemented. Other concrete monads are coming.

###Putting values in Context

```python
Maybe.unit(4) # Returns Just(4)
```

Or use a functional approach:

```python
unit(4, Maybe)
```

Or emulate Haskell poorly:

```python
4 & Maybe
```

###Bind, Shove, `>>=`, et. al

Use a bastardized version of Haskell's `>>=`:

```python
Just(4) >> (lambda v: Maybe(v+2))
```

Chain them together with excessive parens:

```python
Maybe.unit(4) >> (lambda v: Maybe(v+2)) >> (lambda v: Nothing)
```

Here's this thing:

```python
(2 & Just) >> (lambda x: Just(x+2))
```

Use the bind assignment operator:
```python
m = Just(2)
m <<= lambda x: Just(x+2) # now it's Just 4
```

Do lots of bind operations easily:
```python
from itertools import repeat
multibind(Just(0), *repeat(lambda x: Just(x+2), 3))
```

###Functors
There are here too!

```python
class FMapDict(dict, Functor):
    def fmap(self, f):
        return FMapDict((k, f(v)) for k,v in self.items())
```

Two ways to use!:

```Python
fmd = FMapDict((i,i) for i in range(10))
fmd.fmap(lambda x: x+1)
# or more Haskell-y!
fmap(lambda x: x+1, fmd)
```

###Applicatives
We got applicatives!

```python
Just(lambda x: x+2).apply(Just(2))
```

But wait, there's an operator!

```python
Just(lambda x: x+2) * Just(2)
```

*Just* like before, take operator overloading abuse to 11!

```python
((lambda x: x+2) & Just) * Just(2)
```

Got a curried function (or just a bunch of nest single argument lambdas)?!

```python
fake_curry = lambda x: lambda y: lambda z: x+y+z

multiapply(Just(fake_curry), Just(1), Just(2), Just(3))
```
