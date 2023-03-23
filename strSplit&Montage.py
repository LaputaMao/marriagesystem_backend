"""
3.23计划将择偶条件的范围上界和下界存到一个表项中
使用时从mysql中取出string用split解析成范围
"""
if __name__ == '__main__':
    teststr = '160,180'
    liststr = teststr.split(',')
    print(liststr[0], liststr[1])


