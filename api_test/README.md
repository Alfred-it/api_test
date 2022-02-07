# Auto-API
#### 介绍
接口自动化测试框架
#### 程序描述
将接口信息存放到excel表中，相关请求体数据写入json文件，程序从中读取，运行后将结果回写到表格中并输出一份html测试报告，
报告中包含所有接口的测试日志，按异常错误，执行失败，执行成功分类。
#### 使用说明

##### 框架结构说明

大致分三块：
1. 接口数据：存放在excel中
2. 代码数据：修改case中的执行函数
3. 测试数据：在j对应的son文件中，json文件分大致三块（header，config：主要是放参数化的数据，各请求的body）

##### 使用流程
1. 根据表格模式填写接口信息，json数据信息
2. excel表格和相关json数据文件放在data目录下（只支持restful风格的接口自动化）
3. 添加case，调用函数运行
##### excel表格说明
1. name：当前接口的作用
2. execute：当前接口是否需要执行,0不执行，1执行
3. method: 请求方法
4. header：请求头的 "key"，根据配置文件里自己写的值自定义
5. http/https：请求协议
6. ip：域名或者ip地址
7. path：请求路径
8. body：配置文件中亲求体的 "key"，没有可不填
9. ~~ex_answer：请求返回之中的关键词，断言用的，没有可不填～~~
10. ~~pre_result	dev_result：不同环境下回写的测试结果（不执行，失败，成功三种状态）~~
11. 当前只有result，不区分环境（不执行，失败，成功三种状态）
12. 新增sleep_time字段，可以自定义每个接口结束后的等待时间，不填默认1s。
13. extract_key：json数据提取，标准的json格式，当要提取的字段只有一层时，{"key":"val"},其中key是要提取的key名称，val是固定的
当要提取的字段多层嵌套时，{"userProfile":["cellPhone"]}，原本的val换成列表，里面填每一层的key的名称。支持同时提取多字段。
14. depended_key：获取前面接口提取的字段 cat,liveId,dog 以逗号隔开即可
15. sleep_time：在本接口执行结束之后等待多少时间执行下一个接口，可以自定义，不填默认0.1s

#### 关于数据依赖
extract_key：
    这一列填写本接口返回值中需要被后面接口用到的字段，包含以下几种场景：
    
    json文件：
    {
        "key1":"val1"，
        
        "key2":"val1"
        
    }
    
    提取格式：{"key1_string":"val"，"key2_string":"val"} 
    
    这里的val是固定的，前面的key需要和返回值中的key一致,key的后面可以用下划线加自定义字符串来达到重命名的目的
    
    
    json文件：
    {
        "key1":
        {
            "key2":
            {
                "key3":"val"
            }
        }
    }
    
    提取格式：{"key1":["key2","key3_string"]} 
    
    多层提取也支持下划线的方式自定义名称
    
    
    json文件：
    {
        "key1":[{"key2":"val"},{"key3":"val"},{"key4":"val"}]
    }
    
    提取格式：{"key1_string":["key2_diyword"]} 
    
    这种情况只能取到元组中的第一个元素，也就是key2
header场景

    1.如果请求中要求添加token，需要注意token传参,token值前加"Bearer "注意Bear后的空格：
          "header_token":
     {
        "Content-Type": "application/json",
         "Authorization":"Bearer {access_token_xuan}"
     } 
   
body的场景

    1.正常情况按照标准的json文件上传就行
    
    2.异常情形：
    
    body：[{"key1","val2"},{"key2":"val2"}]
    
    处理方式：json文件中，body的命名加上"_list",key用"list",呃。。。就像这样：
    
      "sns_list":
      {
        "list":["8D17250882B43AAA"]
      }
      
    其他异常场景支持扩展
    
    3.上传文件（目前仅做了excel文件的上传，有其他需要可以快速扩展）
     
      "uploadWordSize_excel": 
       {
        "file_key":"file",
        "file_path":"../../data/buffet/工作簿18888.xlsx",
        "data":""

       }
       
       body的key后面加"_key"后缀，第一个参数是和开发约定好的名称，第二个参数是文件的路径，第三个参数存放其他信息，如果没有则传 ""
       
       
    4。post请求中body为form-data格式
        
    "login_master_formdata": 
    {
        "username": "buffetautotest4@yopmail.com",
        "password}": "Xk7pHynrrtSbAFv9FPxJUOBKDQqd0XjlopX8GZ/Qlgl46QCgmuMD+Q/25KAJF/Cc432NMQh7AyNnaXqaTgEFfwslvFl+y3tmVsfYZS2BQGFfIeExop+xF32MIyvGdWFuhpe/XDyXZ9sf/Uv9at4ovBAfWs1WwnTVcMSTR7yEMfU=",
        "{loginType}": "ACCOUNT"
    }   
    
    
    body后面加"_formdata"后缀即可
    
    5.post请求中body为x-www-form-urlencoded类型
    
      "delete_batch__urlencoded":
       {
          "prepareLessonIds": "{prepareLessonId}"
       
        
#### case入口
1. 在cases文件夹下新建py文件
2. 文件中新建`TestMethodPre` 类
3. 添加测试成员函数

```python


    class TestMethodPre(unittest.TestCase):
    
        # 引入语法糖，参数是excel文件相对于"data"的相对路径
        @excelpath("/vod/vod.xlsx")
        def test_vod(self):
           # 调用execute函数，参数（表格名称，json文件名称，配置文件名称）
            execute("vod_zhou", "vod_zhou.json", "config_pre_uss")        
   
    if __name__ == '__main__':
    fp = open('../report/html_report.html', 'wb')

    suite = unittest.TestSuite()
    suite.addTest(TestMethodPre('test_vod'))
    suite.addTest(TestMethodPre('test_vod2'))

    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title="API Report")
    runner.run(suite)
```      
#### 项目目录结构

* project
    * data
        * vod (module_name directory)
            * vod.xls(excel表格)
            * vod_zhou.json(json文件)
            * vod_hao.json(json文件)
            * vod_junwei.json(json文件)
    * src
        * base
            * HTMLTestRunner.py
        * case
            * case.py
        * public
            * common.py
            * data_path.py
            * execute.py
            * send_msg.py
            * signature.py
        * report
            * html_report.html
        * utils
            * excel_opt.py
            * json_opt.py
            * log_opt.py
        
#### 签名使用规则
 * 不用签名：配置文件中不写"{token}"或者参数值传""/{signature}=="no"
 * 旧签名：写"{token}",不写"{signature}"或者"{signature}"的值不等于"new"
 * 新签名：写"{token}",配置"{signature}"："new"
 
 
#### 通用异常
 * 在配置文件中将 "{exception}"设置为 true ，测试过程便会自动生成通用异常进行测试
 * 目前通用异常是将异常场景中状态码为500的相关case过滤到 log 文件中，log件在report目录下（追加模式）
 * 通用异常指的是，针对请求body中的每一个key分别将value置为 " "，null以及删除整个k-v，查看状态码不能为500
    
    
#### 参与贡献
biubiubiu

#### 码云特技
1. 使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2. 码云官方博客 [blog.gitee.com](https://blog.gitee.com)
3. 你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解码云上的优秀开源项目
4. [GVP](https://gitee.com/gvp) 全称是码云最有价值开源项目，是码云综合评定出的优秀开源项目
5. 码云官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6. 码云封面人物是一档用来展示码云会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)