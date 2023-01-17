# Experimentation with MD5

The core "mixer" function is at md5.c:97, where 4 bytes from the input block is added into the state:

```
  t = a[as] + funcs[fi](a[(as+1)&3], a[(as+2)&3], a[(as+3)&3])
      + *((uint32_t*)block) + md5_T[i];
```


