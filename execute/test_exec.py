
import nodji as nd

time = nd.NTime.get_current_time()
print(time.min)
time.min += 6
print(time.min)
print(time)