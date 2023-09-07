# reinforcementLearningBased-autoattack-in-Minecraft

* Minecraft 1.19.2 with Forge
* Pytroch

![Alt](https://github.com/3c0tr/reinforcementLearningBased-autoattack-in-Minecraft/blob/main/%E6%BC%94%E7%A4%BA/Run.jpg)  

> 本项目采用截图目标检测(yolov5)的方式获取屏幕中怪物的位置，再通过自定义一个基于Forge的MOD获取游戏内事件，比如实体受伤/死亡事件，~~为什么不直接用Forge获取详细位置信息~~，以及随机生成地牢中的怪物，来实现全自动强化学习训练，试图教会Steve如何在地牢中对抗来袭的僵尸  

> 演示中的僵尸每回合将会生成在<font color=red>红色地板</font>上的任意位置，且每回合Steve将拿着武器从固定位置重生  

* classgame.py 负责进行目标检测  
* maze.py 负责用socket接收来自Minecraft的游戏事件，调用上方的目标检测函数获取怪物的位置信息，并操控Steve与进行强化学习训练  
* send_mesg.java 基于Forge API 的MOD源码，获取并处理游戏事件，部分游戏事件将被发送给python进程用于训练模型  
* PYserver.java 这是个socket服务器  
