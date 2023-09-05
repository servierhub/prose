package test;

public class helloworld
{
    public static int add(final int x, final int y) {
        return x + y;
    }

    public static void main(final String[] args) {
        final int x = 1;
        if (x == add(1, 0)) {
            System.out.println("Hello the world");
        }
        System.out.println("Hello the world");
    }
}