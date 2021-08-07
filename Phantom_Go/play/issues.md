# 目录
- [目录](#目录)
- [7/25更新](#725更新)
```python
board = Board()
tree = search.Tree("model.ckpt", use_gpu=False)
board.showboard()
move, _ = tree.search(board, 10, ponder=True)   
```

生成落子位置是这个`tree.search`,然后传入一个当前棋盘的状态

```python
# 搜索
def search(self, b, time_, ponder=False, clean=False):
    start = time.time()
    # 通过模型得到策略
    prob, v = self.evaluate(b)  # 返回policy和value
    self.root_id = self.create_node(b.info(), prob[0])
    self.root_move_cnt = b.move_cnt
```
进入search函数里面用到了evaluate这个函数
```python
def evaluate(self, b):
    """
    判断当前局势
    :param b: board()
    :return: policy, value
    """
    return self.sess.run(self.pv,
                            feed_dict={self.x: np.reshape(b.feature, (1, BVCNT, 7))})
```
**第一个问题**

里面有一个b.feature是一个python装饰器函数

关键在这里，feature是一个shape是(121, 7)，第0， 1列记录分别当前棋盘黑棋和白棋的位置；2，3，4，5列分别记录上次和上上次棋盘中黑棋和白棋的位置，第6列是当前棋子的颜色，然后返回值返回除去边界所在索引的所有行。shape：（81， 7）
把这样一个有白棋有黑棋的棋面信息给了模型去估计。这里就是问题。所有其他函数都是照着有黑有白的棋面去判断的。

所以打算三个个函数
```python
def play_my_side(self, v, not_fill_eye=True): #仅仅走一边的子
    pass
    
def take_remove(self, v):
        """
        若棋子因为提子移走，调用这个函数 将该棋子四周放上另一边的棋子
        :param v:
        """
        flag = []
        self.turn = int(self.turn == 0)
        for d in dir4:
            i = self.play_my_side(v + d)
            if i != 0:
                flag.append((v+d))

        for i in flag:
            self.play_my_side(i)
        self.turn = int(self.turn == 0)

def illegal_remove(self, v): # 把这个棋子的位置填上另一边的棋子颜色
    """若棋子因为不合法拿走，调用这个函数"""
    self.turn = int(self.turn == 0)
    self.play_my_side(v)
    self.turn = int(self.turn == 0)
```
主要需要解决evaluate估计的时候用到了黑棋白棋棋面

# 7/25更新
实际运行的时候发现，程序如果没有看到对面的棋子，且没有落子错误和提子的话，会自认为自己的win rate是80%以上，所以程序本身不严谨