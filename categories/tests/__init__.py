from .category_model_test import *
from .views_test import *
from .category_tree_formating_test import *
from .serializers_test import *

import logging

# disable logging in tests
logging.basicConfig(level=logging.CRITICAL)
