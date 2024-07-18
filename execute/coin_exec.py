from typing import Sequence, TypeVar, Generic

import nodji as nd

nd.set_log_level(nd.LogLevel.INFO)

assets = nd.Assets()
assets.update()
