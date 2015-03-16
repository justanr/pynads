#gonads

Just playing around with implementing monads in Python by abusing metaclasses.

Quick Examples
--------------

It comes with Maybe implemented.

Put a value in a monadic context:

```python
4 > Maybe # returns Just(4)
```

Use a bastardized version of Haskell's `>>=`:

```python
Just(4) >= (lambda v: v+2 > Maybe)
```

Chain them together with excessive parens:

```
(4 > Maybe) >= (lambda v: v+2 > Maybe)
```
