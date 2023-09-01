package main

import (
	"fmt"
	"unsafe"
)

type slice struct {
	array unsafe.Pointer
	len   int
	cap   int
}

func foo() int {
	a, b := 3, 5
	c := a + b
	defer fmt.Println("111")
	fmt.Println(c)
	defer fmt.Println("222")
	return c
}

func main() {
	foo()
}
