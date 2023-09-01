package main

import (
	"fmt"
)

func main() {
	var a int
	var b int
	var c int
	var age byte
	var sex bool
	var price float64

	a = 10
	b = 20
	c = a + b
	f := 40.0
	g := c - a

	var h int = 4
	var m = 4
	fmt.Println(c)
	fmt.Println(age)
	fmt.Println(sex)
	fmt.Println(price)
	fmt.Printf("%d %d %t %f\n", c, age, sex, price)
	fmt.Printf("%T %T\n", f, g)
}
