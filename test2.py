import matplotlib.pyplot as plt

# 假设timbre数组为timbre_arr
timbre_arr = [0.1, 0.3, 0.5, 0.7, 0.9, 0.8, 0.6, 0.4, 0.2, 0.1, 0.3, 0.5]

# 绘制折线图
plt.plot(range(12), timbre_arr)

# 添加x轴和y轴标签
plt.xlabel('Timbre Index')
plt.ylabel('Timbre Value')

# 显示图形
plt.show()