#gonads

Just playing around with implementing monads in Python by abusing metaclasses.

Quick Examples
--------------

It comes with Maybe implemented.

Put a value in a monadic context:

```python
Maybe.unit(4) # Returns Just(4)
```

Use a bastardized version of Haskell's `>>=`:

```python
Just(4) >> (lambda v: Maybe(v+2))
```

Chain them together with excessive parens:

```
Maybe.unit(4) >> (lambda v: Maybe(v+2)) >> (lambda v: Nothing)
```
