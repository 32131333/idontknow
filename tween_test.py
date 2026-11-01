# Тест -> Tween

import time

def get_bezier_t(target_x, A, B, C, epsilon=1e-6):
    if target_x <= 0.0: return 0.0
    if target_x >= 1.0: return 1.0

    t_min = 0.0
    t_max = 1.0
    t = target_x 

    # 8 итераций Ньютона
    for _ in range(8):
        # Исправлено: Схема Горнера считает A*t^3 + B*t^2 + C*t
        current_x = ((A * t + B) * t + C) * t
        # Производная: 3*A*t^2 + 2*B*t + C
        dx = (3.0 * A * t + 2.0 * B) * t + C

        if abs(dx) < 1e-6:
            break

        next_t = t - (current_x - target_x) / dx
        
        if next_t < t_min or next_t > t_max:
            break
            
        if abs(next_t - t) < epsilon:
            return next_t
        t = next_t

    # 12 итераций бисекции (фолбэк)
    for _ in range(12):
        current_x = ((A * t + B) * t + C) * t
        if abs(current_x - target_x) < epsilon:
            return t
        if target_x > current_x:
            t_min = t
        else:
            t_max = t
        t = (t_min + t_max) * 0.5

    return t

class TweenFrame:
    def __init__(self):
        self.ttype = 0
        self.f = None
        
        # Коэффициенты полиномов для Безье
        self.ax, self.bx, self.cx = 0.0, 0.0, 0.0
        self.ay, self.by, self.cy = 0.0, 0.0, 0.0
    
    def reach(self, fromValue, toValue, p):
        # p - процентное время пройденного времени. Но здесь от 0 до 1
        # В основе используется принцип классической интерполяции
        
        if self.ttype == 0:
            # Линейная
            return fromValue + (toValue-fromValue)*p
        elif self.ttype == 1:
            # Содержит какую-нибудь функцию
            return fromValue + (toValue-fromValue)*self.f(p)
        elif self.ttype == 2:
            # Находим t по значению p (которое и есть наш X-время)
            # Передаем коэффициенты строго в порядке: A, B, C
            t = get_bezier_t(p, self.ax, self.bx, self.cx)
            
            # Считаем финальный y по исправленной схеме Горнера
            y = ((self.ay * t + self.by) * t + self.cy) * t
            
            return fromValue + (toValue - fromValue) * y
  
    def bezier(self, x1, x2, y1, y2):
        self.ttype = 2
        
        # Считаем коэффициенты ОДИН раз при создании кадра
        self.cx = 3.0 * x1
        self.bx = 3.0 * (x2 - x1) - self.cx
        self.ax = 1.0 - self.cx - self.bx
        
        self.cy = 3.0 * y1
        self.by = 3.0 * (y2 - y1) - self.cy
        self.ay = 1.0 - self.cy - self.by
        
        return self
  
    def func(self, f):
        # Например -> lambda x: ( math.sin(x * math.pi * 5) * 0.5 + 0.5 )
        # Принимается желательно в значении от 0 до 1, чтобы от нуля до енициы функция отлично сработала
        self.ttype = 1
        self.f = f
        
        return self


class Tween:
    def __init__(self):
        self.time = time.time()
        self.endtime = 0
        
        self.repeatable = False
        
        self.start = 0
        
        self.TweenFrames = []
        # { "time": 12.11, "e": 123, "tf": [ TweenFrame ] }
        # Время измеряется в секундах
    
    def appendFrame(self, t, end, tf: TweenFrame):
        self.TweenFrames.append({
            "time": t,
            "e": end,
            "tf": tf
        })
        
        self.TweenFrames.sort(key=lambda x: x["time"])
        
        return self
    
    def repeat(self, v):
        self.repeatable = v
        return self
        
    def startFrom(self, v):
        self.start = v
        return self
    
    def value(self):
        # Сколько времени прошло
        t = self.endtime - self.time
        
        a = list(filter(
            lambda x: (t <= x["time"] or (self.TweenFrames.index(x)+1 == len(self.TweenFrames))),
            self.TweenFrames
        ))
        
        if len(a) == 0:
            return
        else:
            frame = a[0]
            
            end = frame["e"]
            endtime = frame["time"]
            tf = frame["tf"]
        
            fromtime = 0
            fromValue = 0
            
            # Если нам известно, что кадр не последний, нужно достать оттуда последнее время, чтобы начать отсчёт относительно него
            indx = self.TweenFrames.index(frame)
            if indx > 0:
                fromtime = self.TweenFrames[indx-1]["time"]
                fromValue = self.TweenFrames[indx-1]["e"]
            else:
                fromValue = self.start
            
            # Ищем процентное соотношение пройденного времени
            pt = (t - fromtime)/(endtime - fromtime)
            
            return tf.reach( 
                fromValue,
                end,
                min(max(pt, 0.0), 1.0)
            )
     
    def tick(self):
        self.endtime = time.time()
        if self.repeatable:
            t = self.endtime - self.time
            
            a = list(filter(
                lambda x: (t <= x["time"]),
                self.TweenFrames
            ))
            
            if len(a) == 0:
                self.time = self.endtime
        
        return self
 

# Всякое!!
"""

Разное, что я нашёл

lambda x: x**i
- ease-in при i>1 . Рекомендовано 2 (парабола)
- ease-out при i<1

lambda x: ( (3*x)**i - (2*x)**i )

Для самих сглаживаний, как узнал, используется специальная формула
Кривая Безье

"""


if __name__ == "__main__":
    import math 
    
    t = Tween().startFrom(0).repeat(True)
    
    t.appendFrame(
        10, # 10 секунд
        10,
        TweenFrame().func(lambda x: ( math.sin(x * math.pi * 5) * 0.5 + 0.5 ))
    ).appendFrame(
        10+5,
        100,
        TweenFrame().func(lambda x: x**5)
    ).appendFrame(
        10+5+15,
        0,
        TweenFrame()
    ).appendFrame(
        10+5+15+20,
        -100,
        TweenFrame().bezier(0.42, 0.58, 0.0, 1.0)
    )
    
    while True:
        print(f"Текущее значение: {t.tick().value():.2f}", end="\r")