int
putstr(char *s)
{
    while(*s)
    putchar(*s++);
}

int
fac(int n)
{
    if (n == 0)
return 1;
    else
return n*fac(n-1);
}

int
putn(int n)
{
    if (9 < n)
putn(n / 10);
    putchar((n%10) + '0');
}

int
facpr(int n)
{
    putstr("factorial ");
    putn(n);
    putstr(" = ");
    putn(fac(n));
    putstr("\n");
}

int
main()
{
    int i;
    i = 0;
    while(i < 10)
facpr(i++);
    return 0;
}
