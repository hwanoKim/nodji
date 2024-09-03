
import nodji as nd
time = nd.NTime.get_current_time()

print(11, time, time.time_zone)
print(22, time.to_utc(), time.to_utc().time_zone)