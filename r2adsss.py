# -*- coding: utf-8 -*-

import random
import time
import math
from typing import Type

from base.message import *
from player.player import *
from r2a.ir2a import IR2A
from statistics import mean


class R2ADsss(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)

        self.qi = []
        self.time = 0
        self.vazoes = []
        self.SS = []

    def handle_xml_request(self, msg):

        self.time = time.time()

        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.time
        self.vazoes.append((msg.get_bit_length()) / t)

        for i in range(len(self.qi) - 1):
            if self.vazoes[-1] > self.qi[i]:
                self.SS.append(i)

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        self.time = time.perf_counter()

        media_vazoes = mean(self.vazoes)
        M = len(self.vazoes)
        weight = 0
        for i in range(M):
            weight = weight + (abs(self.vazoes[i] - media_vazoes) * i)/M

        p = media_vazoes / (media_vazoes + weight)

        print(f'P = {p}')

        max_omega = 0

        if len(self.SS) == 0:
            max_omega = 0
        else:
            max_omega = self.SS[-1] - 1

        print(f'MAX_OMEGA = {max_omega}')

        t_estranho = (1 - p) * self.qi[max_omega]

        print(f'T_ESTRANHO = {t_estranho}')

        min_omega = 0

        n = len(self.qi)

        if len(self.SS) != 0:
            min_omega = n - 1
        else:
            min_omega = 1

        print(f'MIN_OMEGA = {min_omega}')

        tetha = p * self.qi[min_omega]

        ss_linha = 0

        if len(self.SS) != 0:
            ss_linha = abs(self.qi[self.SS[-1]] - t_estranho + tetha)
        else:
            ss_linha = abs(self.qi[0] - t_estranho + tetha)

        avg = ss_linha

        selected_qi = 0
        for i in range(len(self.qi)):
            if avg > self.qi[i]:
                selected_qi = i

        msg.add_quality_id(self.qi[selected_qi])
        self.send_down(msg)

    def handle_segment_size_response(self, msg):

        t = time.perf_counter() - self.time
        self.vazoes.append((msg.get_bit_length()) / t)
        for i in range(len(self.qi)):
            if self.vazoes[-1] > self.qi[i]:
                self.SS.append(i)
        self.send_up(msg)

    def initialize(self):

        pass

    def finalization(self):
        pass
