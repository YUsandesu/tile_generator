# 参考程序：

https://aatishb.com/patterncollider/

# 参考文献:

https://mathpages.com/home/kmath621/kmath621.htm

https://www.sciencedirect.com/science/article/pii/S0019357713000530
6.2. Inflation rules
**一种常用的创建大型镶嵌的方法是通过重复应用某些膨胀规则：将所有镶嵌片膨胀并用一组原始镶嵌片替换每个镶嵌片，遵循非常精确的规则。镶嵌百科全书给出了超过 180 个例子。**

# 想要读的书(暂时看不到)：

《Tilings and Patterns》（Branko Grünbaum 和 G.C. Shephard 著），详细介绍铺砖理论。
https://link.springer.com/chapter/10.1007/978-3-031-28428-1_5
本章介绍了 Nicolaas G. de Bruijn 引入的方法和理念，他为 Penrose 镶嵌的研究提供了一些主要贡献。
在这里，我们学习如何将一个正五格网转化为一个 Penrose 镶嵌图案。
我们讨论了切割-投影法，首先是针对一维镶嵌，然后是 Penrose 镶嵌。
我们学习如何通过将二维晶格的一部分投影到一条线上来构建斐波那契镶嵌图案，
以及如何通过将五维晶格的一部分投影到一个平面上来构建由 Penrose 菱形构成的镶嵌图案。
我们研究了一个五格网在组合过程中如何变化，并分类与正五格网相关的镶嵌。

Kurt Bruckner’s view on the Penrose tiling
https://link.springer.com/article/10.1007/s11224-016-0790-1?fromPaywallRec=true

# 备忘录:

<think>因为是以n平分2pi产生来的,所以使用最小单位 2pi/n 必定可以继续细分小Tilling,我应该沿着这个方向继续探索对于视觉效果中Tilling的细分问题.
https://www.math.utah.edu/~treiberg/PenroseSlides.pdf
本文28 开始讨论了PenroseTilling自相变换细分问题.

## 研究方向:

群论：分析 Penrose Tiling 的五次对称性，可用十次对称的二面体群研究。

除了关注的 P2 和 P3 类型，还有 P1, P4, P5 等不同类型的 Penrose tiling
**它们可以通过不同的 Cut and Project 方法或 Bruijn's grid 变体生成。**

充气和收缩 (Inflation and Deflation): 
Penrose tiling 具有自相似性，可以通过充气和收缩规则来生成和分析。研究 Bruijn's grid 方法如何体现充气和收缩规则是一个有趣的方向。

# 当前进度:

TODO 应该测试下 Tilling 同时绘制两个网格的效果

TODO 调整gird 返回的 数据类型

效果参考:
https://www.instagram.com/p/CFe4yYBnuHS/
![节点风格.png](picture%2F%E8%8A%82%E7%82%B9%E9%A3%8E%E6%A0%BC.png)