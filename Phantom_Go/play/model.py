# -*- coding: utf-8 -*-

from board import *
import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()
# gpus = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(gpus[0], True)

FILTER_CNT = 96
# 残块量
# 与网络深度有关
BLOCK_CNT = 6
# 标准化系数
w_wdt = 0.007
b_wdt = 0.015


class DualNetwork(object):

    # 获取参数，默认获取权重
    @staticmethod
    def get_variable(shape_, width_=0.007, name_="weight"):
        var = tf.get_variable(name_, shape=shape_,
                              initializer=tf.random_normal_initializer(
                                  mean=0, stddev=width_))

        if not tf.get_variable_scope()._reuse:
            tf.add_to_collection("vars_train", var)

        return var

    # 二维卷积核
    @staticmethod
    def conv2d(x, w):
        # [batch, in_height, in_width, in_channels]
        # [filter_height, filter_width, in_channels, out_channels]
        # 每一维的步长
        # 当其为‘SAME’时，表示卷积核可以停留在图像边缘
        return tf.nn.conv2d(x, w, strides=[1, 1, 1, 1],
                            padding='SAME', name="conv2d")

    # 输入层 中间层 输出层
    # dr_block 减少程度
    def res_block(self, x, input_size, middle_size, output_size,
                  dr_block=1.0, scope_name="res"):

        with tf.variable_scope(scope_name + "_0"):
            w0 = self.get_variable([3, 3, input_size, middle_size],
                                   w_wdt, name_="weight")
            b0 = self.get_variable([middle_size], b_wdt, name_="bias")
            # x>0?x:0
            conv0 = tf.nn.relu(self.conv2d(x, w0) + b0)
        with tf.variable_scope(scope_name + "_1"):
            w1 = self.get_variable([3, 3, middle_size, output_size],
                                   w_wdt, name_="weight")
            b1 = self.get_variable([output_size], b_wdt, name_="bias")
            # 使输入tensor中某些元素变为0，其它没变0的元素变为原来的1/keep_prob大小
            # 稀疏tensor，防止过拟合
            conv1 = tf.nn.dropout(self.conv2d(conv0, w1) + b1, dr_block)

        if input_size == output_size:
            x_add = x
        elif input_size < output_size:
            # 扩张指定维数
            x_add = tf.pad(x, [[0, 0], [0, 0], [0, 0],
                               [0, output_size - input_size]])
        else:
            # 当输出维度小于输入维度时，从输入中截取
            x_add = tf.slice(x, [0, 0, 0, 0],
                             [-1, BSIZE, BSIZE, output_size])

        return tf.nn.relu(tf.add(conv1, x_add))

    def model(self, x, temp=1.0, dr=1.0):
        """
        模型输出结果
        :param x:
        :param temp:
        :param dr:
        :return: return policy, value
        """
        hi = []

        prev_h = tf.reshape(x, [-1, BSIZE, BSIZE, FEATURE_CNT])

        # residual blocks加深网络深度
        # residual blocks with N layers
        for i in range(BLOCK_CNT):
            # 首块为7其他为FILTER_CNT
            input_size = FEATURE_CNT if i == 0 else FILTER_CNT
            dr_block = 1 - (1 - dr) / BLOCK_CNT * i

            hi.append(self.res_block(prev_h, input_size, FILTER_CNT, FILTER_CNT,
                                     dr_block=dr_block, scope_name="res%d" % i))
            prev_h = hi[i]

        # policy connection
        with tf.variable_scope('pfc'):
            # 1st layer
            # [-1, BSIZE, BSIZE, FILTER_CNT] => [-1, BSIZE**2 * 2]
            w_pfc0 = self.get_variable([1, 1, FILTER_CNT, 2],
                                       w_wdt, name_="weight0")
            b_pfc0 = self.get_variable([BSIZE, BSIZE, 2], b_wdt, name_="bias0")
            conv_pfc0 = tf.reshape(self.conv2d(hi[BLOCK_CNT - 1], w_pfc0)
                                   + b_pfc0, [-1, BVCNT * 2])

            # 2nd layer
            # [-1, BSIZE**2 * 2] => [-1, BSIZE**2 + 1]
            w_pfc1 = self.get_variable([BVCNT * 2, BVCNT + 1],
                                       w_wdt, name_="weight1")
            b_pfc1 = self.get_variable([BVCNT + 1], b_wdt, name_="bias1")
            conv_pfc1 = tf.matmul(conv_pfc0, w_pfc1) + b_pfc1

            # divided by softmax temp and apply softmax
            policy = tf.nn.softmax(tf.div(conv_pfc1, temp), name="policy")

        # value connection
        with tf.variable_scope('vfc'):
            # 1st layer
            # [-1, BSIZE, BSIZE, FILTER_CNT] => [-1, BSIZE**2]
            w_vfc0 = self.get_variable([1, 1, FILTER_CNT, 1],
                                       w_wdt, name_="weight0")
            b_vfc0 = self.get_variable([BSIZE, BSIZE, 1], b_wdt, name_="bias0")
            conv_vfc0 = tf.reshape(self.conv2d(hi[BLOCK_CNT - 1], w_vfc0)
                                   + b_vfc0, [-1, BVCNT])

            # 2nd layer
            # [-1, BSIZE**2] => [-1, 256]
            w_vfc1 = self.get_variable([BVCNT, 256], w_wdt, name_="weight1")
            b_vfc1 = self.get_variable([256], b_wdt, name_="bias1")
            conv_vfc1 = tf.matmul(conv_vfc0, w_vfc1) + b_vfc1
            relu_vfc1 = tf.nn.relu(conv_vfc1)

            # 3rd layer
            # [-1, 256] => [-1, 1]
            w_vfc2 = self.get_variable([256, 1], w_wdt, name_="weight2")
            b_vfc2 = self.get_variable([1], b_wdt, name_="bias2")
            conv_vfc2 = tf.matmul(relu_vfc1, w_vfc2) + b_vfc2

            # apply tanh
            value = tf.nn.tanh(tf.reshape(conv_vfc2, [-1]), name="value")

        return policy, value

    @staticmethod
    def create_sess(ckpt_path=""):
        """
        创建会话
        :param ckpt_path: 模型保存位置
        :return:
        """
        with tf.get_default_graph().as_default():

            sess_ = tf.Session(config=tf.ConfigProto(
                gpu_options=tf.GPUOptions(
                    per_process_gpu_memory_fraction=0.9,  # 高达最大值的 90%
                    allow_growth=True  # True-> 需要时保护，False-> 全部
                ),
                allow_soft_placement=True, log_device_placement=False))
            vars_train = tf.get_collection("vars_train")
            v_to_init = list(set(tf.global_variables()) - set(vars_train))

            saver = tf.train.Saver(vars_train, write_version=1)
            if ckpt_path != "":
                saver.restore(sess_, ckpt_path)
                sess_.run(tf.variables_initializer(v_to_init))
            else:
                sess_.run(tf.global_variables_initializer())

        return sess_

    @staticmethod
    def save_vars(sess_, ckpt_path="model.ckpt"):
        """
        保存训练变量信息
        :param sess_: tf会话
        :param ckpt_path: 参数路径
        :return:
        """
        with tf.get_default_graph().as_default():
            # 获得图中变量的信息
            vars_train = tf.get_collection("vars_train")
            # 保存变量信息
            saver = tf.train.Saver(vars_train, write_version=1)
            # 指定存放文件
            saver.save(sess_, ckpt_path)
