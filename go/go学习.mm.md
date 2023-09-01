# GO网站
- <https://studygolang.com/dl>

# GO目录
- bin<br>第三方的可执行文件
- pkg<br>第三方的go语言包

# GO环境
- GOROOT
- GOPATH
- PATH
- GOPROXY:https://goproxy.cn,direct

# GO命令
- go version
- go env

# 打包和工具链



# 变量
- 变量声明(var)
- 变量类型
  - 整型(%d)-8个字节
  - 浮点型(%f)
    - 默认6位小数
  - 布尔型(%t)
  - 字节型(%d)
  - %p打印地址
- 变量的赋值
  - 未显式赋值的变量，其值为“0”
  - :=符号赋值，自动推断
  - 声明赋值一行完成
- %T输出变量类型

# 字符串
## 本质是不可修改的byte数组
- %c查看字母本身
- 一个汉字3个byte(utf-8)
- rune切片
- 双引号变反引号，原封不动
## 字符串拼接
- +

# map
## 类似于字典
- var m map[string]int
- 函数，切片不能为key
- make创建切片初始化
## 删除
- delete
- key不存在为0
- exists(返回两个)

# 结构体
- type struct(%v,%+v,%#v)

# if语句
- else
- else if
- ;之前初始化(局部变量)

# for循环
- i++
- break
- _作为占位符

# slice(切片)
## array数组
- 声明var arr [5]int
  - 明确告知长度
## 切片本质是结构体
- 三元素
  - array unsafe.Pointter指针
  - len int
  - cap int
- make创建切片
- append追加切片
- len查看长度
- cap查看capcity
- 数组越界
- 扩容2倍
  - 扩容后不再共享底层空间
## 遍历
- range

# 函数
## 函数创建
- func关键词
- 传递参数
- 返回参数类型
- return
## 函数名
## 异常就地处理
- error类型（errors包）
- nil
- if err=nil

# defer
- 注册