# -*- coding: utf-8 -*-
from collections import Counter

import requests
import numpy as np
import pandas as pd
import nodji as nd
import random


def email_lotto_numbers():
    lotto = Lotto()
    email = nd.Email()

    result = []
    lotto.update()
    for i in range(10):
        result.append('번호는 : ' + ', '.join([str(i) for i in lotto.draw()]))

    email.send(msg='\n'.join(result))
    for i in result:
        print(i)


class Consts:
    API_URL = 'https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo='
    EMAIL = 'sin3514@naver.com'


class Lotto:
    """로또의 예상 번호를 받기 위해 만들었다.

    실행방법
        Lotto.draw()
    """

    def __init__(self):
        self.df = nd.NData('lotto').load()

    def __repr__(self):
        return str(self.df)

    def draw(self):
        """로또 번호를 뽑는다.
        
        각 전략을 갈아낄 수 있도록 하고 싶었으나 복잡해져서 
        그냥 직접 전략을 적어서 구현을 했다.
        
        'chat gpt'가 겜블러의 오류라고 놀리지만 뭐 어쨌든 다 운이라면
        내 상식에서 그나마 맞다고 생각하는 전략으로 운을 바래 본다.
        
        전략: 
            가장 적게 나온 번호들이 더 확률이 높다.
                
                현재 발행 횟수곱하기 * 2 를 해준다.
                만약 5번을 발행을 했고 현재 확률적으로 특정 번호가 5번이 나왔어야 했는데
                세번만 나왔다고 해보자.
                
                그러면 앞으로 5번동안 특정 번호는 8번이 나와야 할것이다.
                단순한 계산이다.
        """
        last_round = self.df['round'].iloc[-1]
        nums, freqs = self.get_number_counts_until_specific_round()

        # 총 나와야 하는 횟수
        should_count = last_round * 2 * (1 / 45) * 6  # 한 회차에 6번을 던지니까
        weights = [((should_count - freq) / last_round * 2) for freq in freqs]
        numbers = sorted(random.choices(nums, weights=weights, k=6))
        if self._exists_duplicated_numbers(numbers):
            return self.draw()
        else:
            return numbers

    def get_number_counts_history(self):
        """매 회차를 기준으로 각 숫자들이 몇 번 나왔는지 기록한 데이터 프레임"""
        counts_df = self._generate_new_statistics_dataframe()
        round_counts = self.df['round'].iloc[-1]
        empty_rows = [pd.DataFrame([{}]) for _ in range(round_counts)]
        counts_df = pd.concat([counts_df] + empty_rows, ignore_index=True)

        for round in range(1, round_counts + 1):
            _, draw_counts = self.get_number_counts_until_specific_round(current_round=round)
            for i, draw_count in enumerate(draw_counts):
                counts_df.loc[round - 1, f'no{i + 1}'] = draw_count

            counts_df.loc[round - 1, 'date'] = self.df.loc[self.df['round'] == round]['date'].iloc[-1]
            counts_df.loc[round - 1, 'round'] = round

        return counts_df

    def get_number_count_rankings_history(self):
        """매 회차를 기준으로 가장 많이 나온 순위를 기록한 데이터 프레임"""
        ranking_df = self._generate_new_statistics_dataframe()
        start_round = 3
        last_round = self.df['round'].iloc[-1]

        empty_rows = [pd.DataFrame([{}]) for _ in range(last_round - start_round + 1)]
        ranking_df = pd.concat([ranking_df] + empty_rows, ignore_index=True)

        for idx, round in enumerate(range(start_round, last_round + 1)):
            nums, counts = self.get_number_counts_until_specific_round(current_round=round)
            freq_count = Counter(freq)  # 여기를 counter가 아니고 numpy 의 순서 sortarg인가로 바꿔야함
            for rank, count in enumerate(sorted(freq_count.keys(), reverse=True)):
                for _ in range(freq_count[count]):
                    ranking_df.loc[idx, f'no{nums.pop(0)}'] = rank + 1

            ranking_df.loc[idx, 'date'] = self.df.loc[self.df['round'] == round]['date'].iloc[-1]
            ranking_df.loc[idx, 'round'] = round

        return ranking_df

    def get_number_counts_until_specific_round(self, current_round=None, round_range=0,
                                               include_bonus_number=False,
                                               sort_by_count=True):
        """
        특정 round 까지 각 숫자들이 몇 번 나왔는지 반환한다.

        Args:
            current_round:
                테스트에서 쓰기 위해서 임의로 현재 round가 몇 round인지 지정할 수 있다.
            round_range: 
                최근 회차중 몇 회차중에 뽑을 꺼냐
                0으로 두면 모든 회차를 대상으로 번호를 뽑는다.
            include_bonus_number: 
                보너스 번호를 쓸껀지
            sort_by_count:
                많이 나온 숫자 순서대로 반환할껀지
            
        Returns:
            숫자들, 숫자들의 빈도수
        """
        if not self._validate_variables_of_get_frequent_numbers(current_round, round_range):
            return
        if include_bonus_number:
            df = self.df[['no1', 'no2', 'no3', 'no4', 'no5', 'no6', 'bonus']]
        else:
            df = self.df[['no1', 'no2', 'no3', 'no4', 'no5', 'no6']]

        if current_round is None:
            last_round = self.df['round'].iloc[-1]
        else:
            last_round = current_round

        if round_range == 0:
            start_round = 1
        else:
            start_round = last_round - round_range + 1

        df = df.loc[start_round - 1:last_round - 1]
        arr = np.array(df, dtype='int').flatten()
        counts = np.bincount(arr)[1:]
        if len(counts) < 45:
            counts = np.append(counts, np.zeros(45 - len(counts)))
        freq_ids = np.argsort(counts)  # count가 적은 값부터 순서대로 id를 반환함
        nums = list(reversed((freq_ids + 1).tolist()))
        freq = [int(i) for i in reversed(counts[freq_ids].tolist())]
        if sort_by_count:
            return nums, freq
        else:
            combined_data = list(zip(nums, freq))
            sorted_data = sorted(combined_data, key=lambda x: x[0])

            nums, freq = zip(*sorted_data)
            return nums, freq

    def update(self):
        """로또 데이터를 업데이트 한다."""
        lotto_df = nd.NData('lotto').load()
        self.df = self._download_lotto_data_from_server(lotto_df)
        data = nd.NData('lotto')
        data.set_dataframe(self.df)
        data.save()
        return self.df

    def _exists_duplicated_numbers(self, numbers):
        return len(numbers) != len(set(numbers))

    def _download_lotto_data_from_server(self, lotto_df: pd.DataFrame) -> pd.DataFrame:
        """lotto df를 서버에서 불러온다.

        lotto df를 자동으로 만들고 하나씩 업데이트 한다.
        """
        if lotto_df.empty:
            lotto_df = self._get_new_lotto_dataframe()
            lotto_round = 0
        else:
            lotto_round = lotto_df['round'].iloc[-1]

        continue_fetch = True
        while continue_fetch:
            request = requests.get(Consts.API_URL + str(lotto_round + 1))
            df = pd.DataFrame(request.json(), index=[0])

            if df['returnValue'].iloc[-1] != 'success':
                continue_fetch = False
            else:
                if lotto_df.empty or lotto_df['round'].iloc[-1] < df['drwNo'].iloc[-1]:
                    lotto_df = pd.concat([lotto_df, pd.DataFrame([{}])], ignore_index=True)
                    idx = lotto_df.index[-1]
                    lotto_df.loc[idx, 'date'] = df['drwNoDate'].iloc[-1]
                    lotto_df.loc[idx, 'round'] = df['drwNo'].iloc[-1]
                    lotto_df.loc[idx, 'no1'] = df['drwtNo1'].iloc[-1]
                    lotto_df.loc[idx, 'no2'] = df['drwtNo2'].iloc[-1]
                    lotto_df.loc[idx, 'no3'] = df['drwtNo3'].iloc[-1]
                    lotto_df.loc[idx, 'no4'] = df['drwtNo4'].iloc[-1]
                    lotto_df.loc[idx, 'no5'] = df['drwtNo5'].iloc[-1]
                    lotto_df.loc[idx, 'no6'] = df['drwtNo6'].iloc[-1]
                    lotto_df.loc[idx, 'bonus'] = df['bnusNo'].iloc[-1]
                    lotto_df.loc[idx, 'sellPrice'] = df['totSellamnt'].iloc[-1]
                    print(f'Loaded round {lotto_round + 1}.')
                    lotto_round += 1
                else:
                    continue_fetch = False

        return lotto_df

    def _generate_new_statistics_dataframe(self):
        """번호별 통계를 작성하기 위한 기본 데이터프레임을 작성하여 반환한다."""
        df = pd.DataFrame(columns=['date', 'round'])
        for i in range(1, 46):
            df[f'no{i}'] = None
        return df

    def _get_new_lotto_dataframe(self):
        return pd.DataFrame(columns=['date', 'round',
                                     'no1', 'no2', 'no3', 'no4', 'no5', 'no6',
                                     'bonus', 'sellPrice'])

    def _validate_variables_of_get_frequent_numbers(self, current_round, round_range):
        if current_round is not None:
            if current_round > self.df['round'].iloc[-1]:
                print(f'There are no rounds higher than the current round, {current_round}.')
                return False
        if round_range < 0:
            print(f'Round range cannot be less than 0.')
            return False
        return True
