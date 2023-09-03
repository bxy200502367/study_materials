package main

import (
	"fmt"
)

func main() {
	arr1 := [5]string{"red", "blue", "green", "yello", "pink"}
	arr2 := arr1
	arr1[4] = "black"
	fmt.Println(arr1)
	fmt.Println(arr2)
	var arr3 [5]*string
	arr4 := [5]*string{new(string), new(string), new(string), new(string), new(string)}
	*arr4[0] = "red"
	arr3 = arr4
	fmt.Println(arr3)
	fmt.Println(arr4)
	slice := []int{10, 20, 30, 40, 50}
	newslice := slice[1:3]
	slice[6] = 45
	fmt.Println(newslice)
}
