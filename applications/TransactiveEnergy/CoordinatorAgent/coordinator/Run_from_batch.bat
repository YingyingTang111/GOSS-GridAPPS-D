@echo off
for /l %%i in (3,1,150) do python testram_t2.py -f %%i
pause